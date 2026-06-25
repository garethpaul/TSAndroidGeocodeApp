import io
import os
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr
from pathlib import Path
from unittest.mock import patch

import scripts.check_android_contracts as contracts


VALID_WORKFLOW = """name: Check

on:
  pull_request:
  push:
    branches:
      - master
  workflow_dispatch:

permissions:
  contents: read

concurrency:
  group: check-${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  static-contracts:
    runs-on: ubuntu-24.04
    timeout-minutes: 5
    strategy:
      fail-fast: false
      matrix:
        python-version: ["3.10", "3.12"]
    steps:
      - name: Check out repository
        uses: actions/checkout@df4cb1c069e1874edd31b4311f1884172cec0e10 # v6.0.3
        with:
          persist-credentials: false
      - name: Verify clean checkout
        run: make checkout-integrity
      - name: Set up Python
        uses: actions/setup-python@a309ff8b426b58ec0e2a45f0f869d46889d02405 # v6.2.0
        with:
          python-version: ${{ matrix.python-version }}
      - name: Run repository verification
        run: make static

  android:
    runs-on: ubuntu-24.04
    timeout-minutes: 15
    steps:
      - name: Check out repository
        uses: actions/checkout@df4cb1c069e1874edd31b4311f1884172cec0e10 # v6.0.3
        with:
          persist-credentials: false
      - name: Verify clean checkout
        run: make checkout-integrity
      - name: Set up Java
        uses: actions/setup-java@ad2b38190b15e4d6bdf0c97fb4fca8412226d287 # v5.3.0
        with:
          distribution: temurin
          java-version: "17"
          cache: gradle
      - name: Install Android SDK packages
        run: '"$ANDROID_HOME/cmdline-tools/latest/bin/sdkmanager" "platforms;android-36" "build-tools;35.0.0"'
      - name: Run Android verification
        run: make check
      - name: Verify build kept checkout clean
        run: make checkout-integrity
"""

ROOT_BUILD_WITH_UPDATED_AGP = """plugins {
    id "com.android.application" version "8.10.1" apply false
}
"""

APP_BUILD = """plugins {
    id 'com.android.application'
}

android {
    namespace = 'com.sample.foo.tsgeocodeapp'
    compileSdk = 36

    defaultConfig {
        applicationId = 'com.sample.foo.tsgeocodeapp'
        minSdk = 21
        targetSdk = 36
        versionCode = 1
        versionName = '1.0'
    }

    buildTypes {
        release {
            minifyEnabled = false
            proguardFiles getDefaultProguardFile('proguard-android-optimize.txt'), 'proguard-rules.pro'
        }
    }

    compileOptions {
        sourceCompatibility JavaVersion.VERSION_1_8
        targetCompatibility JavaVersion.VERSION_1_8
    }

    lint {
        warningsAsErrors = true
    }
}

dependencies {
    implementation platform('org.jetbrains.kotlin:kotlin-bom:2.2.21')
    implementation 'androidx.appcompat:appcompat:1.7.1'
    //noinspection GradleDependency -- Lifecycle 2.10+ requires minSdk 23.
    implementation 'androidx.lifecycle:lifecycle-livedata:2.9.4'
    //noinspection GradleDependency -- Lifecycle 2.10+ requires minSdk 23.
    implementation 'androidx.lifecycle:lifecycle-viewmodel:2.9.4'

    testImplementation 'androidx.arch.core:core-testing:2.2.0'
    testImplementation 'junit:junit:4.13.2'
}
"""

WRAPPER_WITH_UPDATED_GRADLE = """distributionBase=GRADLE_USER_HOME
distributionPath=wrapper/dists
distributionSha256Sum=bbaeb2fef8710818cf0e261201dab964c572f92b942812df0c3620d62a529a01
distributionUrl=https\\://services.gradle.org/distributions/gradle-9.6.0-bin.zip
networkTimeout=10000
validateDistributionUrl=true
zipStoreBase=GRADLE_USER_HOME
zipStorePath=wrapper/dists
"""

MAKEFILE = """.PHONY: build check checkout-integrity lint static test verify

override ROOT := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))
PYTHON ?= python3
GRADLEW ?= $(ROOT)/gradlew

checkout-integrity:
\tcd "$(ROOT)" && test -z "$$(git status --porcelain --untracked-files=no)"
\tcd "$(ROOT)" && git ls-files --eol gradlew | grep -Eq '^i/lf[[:space:]]+w/lf[[:space:]]+attr/text eol=lf[[:space:]]+gradlew$$'
\tcd "$(ROOT)" && git ls-files --eol gradlew.bat | grep -Eq '^i/lf[[:space:]]+w/crlf[[:space:]]+attr/text eol=crlf[[:space:]]+gradlew[.]bat$$'

static:
\tcd "$(ROOT)" && PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest tests.test_check_android_contracts -v
\t$(PYTHON) "$(ROOT)/scripts/check_android_contracts.py"

test:
\tcd "$(ROOT)" && "$(GRADLEW)" --no-daemon testDebugUnitTest

build:
\tcd "$(ROOT)" && "$(GRADLEW)" --no-daemon assembleDebug

lint: static
\tcd "$(ROOT)" && "$(GRADLEW)" --no-daemon lintDebug

verify: static
\tcd "$(ROOT)" && $(PYTHON) "$(ROOT)/scripts/run_android_verification.py" "$(GRADLEW)"

check: verify
"""

VALID_DEPENDABOT = """version: 2
updates:
  - package-ecosystem: gradle
    directory: /
    schedule:
      interval: weekly
    ignore:
      # Lifecycle 2.10+ requires minSdk 23; remove after the API 21 migration.
      - dependency-name: "androidx.lifecycle:*"
        versions:
          - "[2.10.0,)"
      # Kotlin 2.3+ requires AGP 8.13.2; remove after the AGP migration.
      - dependency-name: "org.jetbrains.kotlin:kotlin-bom"
        versions:
          - "[2.3.0,)"
    groups:
      android-dependencies:
        patterns:
          - "*"
        update-types:
          - minor
          - patch
  - package-ecosystem: github-actions
    directory: /
    schedule:
      interval: weekly
    groups:
      github-actions:
        patterns:
          - "*"
        update-types:
          - minor
          - patch
"""


class CheckHostedVerificationContractsTest(unittest.TestCase):
    def test_accepts_updated_immutable_action_sha_with_semver_annotation(self):
        contracts.check_hosted_verification_text(VALID_WORKFLOW)

    def test_rejects_noncanonical_workflow_content(self):
        setup_java = "actions/setup-java@ad2b38190b15e4d6bdf0c97fb4fca8412226d287 # v5.3.0"
        mutations = {
            "floating tag": VALID_WORKFLOW.replace(setup_java, "actions/setup-java@v5.3.0 # v5.3.0"),
            "short sha": VALID_WORKFLOW.replace(setup_java, "actions/setup-java@ad2b38190b15 # v5.3.0"),
            "missing annotation": VALID_WORKFLOW.replace(
                setup_java, "actions/setup-java@ad2b38190b15e4d6bdf0c97fb4fca8412226d287"
            ),
            "comment uses": VALID_WORKFLOW + "        # uses: attacker/setup-java@v1\n",
            "attacker action": VALID_WORKFLOW
            + "        uses: attacker/setup-java@ad2b38190b15e4d6bdf0c97fb4fca8412226d287 # v5.3.0\n",
            "quoted key": VALID_WORKFLOW
            + '        "uses": attacker/setup-java@ad2b38190b15e4d6bdf0c97fb4fca8412226d287\n',
            "flow map": VALID_WORKFLOW
            + "      - { uses: attacker/setup-java@ad2b38190b15e4d6bdf0c97fb4fca8412226d287 }\n",
            "unicode key": VALID_WORKFLOW
            + '        "\\u0075ses": attacker/setup-java@ad2b38190b15e4d6bdf0c97fb4fca8412226d287\n',
            "extra key": VALID_WORKFLOW + "unexpected: true\n",
        }

        for name, workflow in mutations.items():
            with self.subTest(name=name), self.assertRaises(AssertionError):
                contracts.check_hosted_verification_text(workflow)


class CheckModernAndroidBuildContractsTest(unittest.TestCase):
    def check_build_text(
        self,
        root_build=ROOT_BUILD_WITH_UPDATED_AGP,
        app_build=APP_BUILD,
        wrapper=WRAPPER_WITH_UPDATED_GRADLE,
        makefile=None,
    ):
        if makefile is None:
            makefile = contracts.CANONICAL_MAKEFILE
        contracts.check_modern_android_build_text(root_build, app_build, wrapper, makefile)

    def test_accepts_reviewed_toolchain_tuple(self):
        self.check_build_text()

    def test_rejects_unsupported_kotlin_agp_matrix(self):
        cases = {
            "2.3.0": "Kotlin 2.3 requires AGP 8.13.2",
            "2.4.0": "Kotlin 2.4 requires AGP 9.1.0",
            "2.5.0": "Kotlin 2.5 is not in the reviewed compatibility matrix",
        }

        for kotlin_version, message in cases.items():
            unsupported = APP_BUILD.replace("kotlin-bom:2.2.21", f"kotlin-bom:{kotlin_version}")
            with self.subTest(kotlin_version=kotlin_version), self.assertRaisesRegex(
                AssertionError, message
            ):
                self.check_build_text(app_build=unsupported)

    def test_rejects_mismatched_gradle_distribution_checksum(self):
        mismatched = WRAPPER_WITH_UPDATED_GRADLE.replace(
            "bbaeb2fef8710818cf0e261201dab964c572f92b942812df0c3620d62a529a01",
            "a" * 64,
        )

        with self.assertRaisesRegex(AssertionError, "reviewed Gradle wrapper tuple"):
            self.check_build_text(wrapper=mismatched)

    def test_binds_reviewed_wrapper_jar_checksum(self):
        self.assertEqual(
            getattr(contracts, "GRADLE_WRAPPER_JAR_SHA256", None),
            "497c8c2a7e5031f6aa847f88104aa80a93532ec32ee17bdb8d1d2f67a194a9c7",
        )

    def test_rejects_noncanonical_root_build_content(self):
        mutations = {
            "dynamic version": ROOT_BUILD_WITH_UPDATED_AGP.replace('version "8.10.1"', 'version "+"'),
            "comment": ROOT_BUILD_WITH_UPDATED_AGP.replace("}", "    // unexpected\n}"),
            "duplicate": ROOT_BUILD_WITH_UPDATED_AGP.replace(
                "}", '    id "com.android.application" version "8.11.0" apply false\n}'
            ),
            "unicode declaration": ROOT_BUILD_WITH_UPDATED_AGP
            + 'id "com.android.applicat\\u0069on" version "+" apply false\n',
            "extra content": ROOT_BUILD_WITH_UPDATED_AGP + "unexpected\n",
        }

        for name, root_build in mutations.items():
            with self.subTest(name=name), self.assertRaises(AssertionError):
                self.check_build_text(root_build=root_build)

    def test_rejects_app_build_comment_decoys_and_later_overrides(self):
        mutations = {}
        for setting, valid_value, invalid_value in (
            ("compileSdk", "36", "35"),
            ("targetSdk", "36", "35"),
            ("minSdk", "21", "19"),
            ("warningsAsErrors", "true", "false"),
        ):
            canonical_line = f"        {setting} = {valid_value}"
            if setting == "compileSdk":
                canonical_line = f"    {setting} = {valid_value}"
            mutations[f"{setting} comment decoy"] = APP_BUILD.replace(
                canonical_line,
                f"        // {setting} = {invalid_value}\n{canonical_line}",
            )
            mutations[f"{setting} later override"] = APP_BUILD.replace(
                canonical_line,
                f"{canonical_line}\n        {setting} = {invalid_value}",
            )

        for name, app_build in mutations.items():
            with self.subTest(name=name), self.assertRaises(AssertionError):
                self.check_build_text(app_build=app_build)

    def test_accepts_updated_literal_dependency_versions(self):
        updates = {
            "Kotlin BOM": (
                "org.jetbrains.kotlin:kotlin-bom:2.2.21",
                "org.jetbrains.kotlin:kotlin-bom:2.2.20",
            ),
            "AppCompat": (
                "androidx.appcompat:appcompat:1.7.1",
                "androidx.appcompat:appcompat:1.8.0",
            ),
            "Lifecycle LiveData": (
                "androidx.lifecycle:lifecycle-livedata:2.9.4",
                "androidx.lifecycle:lifecycle-livedata:2.9.5",
            ),
            "Lifecycle ViewModel": (
                "androidx.lifecycle:lifecycle-viewmodel:2.9.4",
                "androidx.lifecycle:lifecycle-viewmodel:2.9.5",
            ),
            "Architecture Core Testing": (
                "androidx.arch.core:core-testing:2.2.0",
                "androidx.arch.core:core-testing:2.3.0",
            ),
            "JUnit": ("junit:junit:4.13.2", "junit:junit:4.14.0"),
        }

        for name, (current, updated) in updates.items():
            with self.subTest(name=name):
                self.check_build_text(app_build=APP_BUILD.replace(current, updated))

    def test_rejects_nonliteral_or_extra_dependency_lines(self):
        kotlin_line = "    implementation platform('org.jetbrains.kotlin:kotlin-bom:2.2.21')"
        appcompat_line = "    implementation 'androidx.appcompat:appcompat:1.7.1'"
        lifecycle_line = "    implementation 'androidx.lifecycle:lifecycle-livedata:2.9.4'"
        core_testing_line = "    testImplementation 'androidx.arch.core:core-testing:2.2.0'"
        junit_line = "    testImplementation 'junit:junit:4.13.2'"
        mutations = {
            "dynamic Kotlin BOM": APP_BUILD.replace(
                kotlin_line,
                "    implementation platform('org.jetbrains.kotlin:kotlin-bom:+')",
            ),
            "nonliteral AppCompat": APP_BUILD.replace(
                appcompat_line,
                "    implementation \"androidx.appcompat:appcompat:${appcompatVersion}\"",
            ),
            "dynamic Lifecycle": APP_BUILD.replace(
                lifecycle_line,
                "    implementation 'androidx.lifecycle:lifecycle-livedata:+'",
            ),
            "nonliteral Core Testing": APP_BUILD.replace(
                core_testing_line,
                "    testImplementation \"androidx.arch.core:core-testing:${coreTestingVersion}\"",
            ),
            "dynamic JUnit": APP_BUILD.replace(
                junit_line,
                "    testImplementation 'junit:junit:latest.release'",
            ),
            "duplicate dependency": APP_BUILD.replace(
                appcompat_line,
                appcompat_line + "\n" + appcompat_line,
            ),
            "extra dependency": APP_BUILD.replace(
                junit_line,
                junit_line + "\n    implementation 'com.example:extra:1.0.0'",
            ),
        }

        for name, app_build in mutations.items():
            with self.subTest(name=name), self.assertRaises(AssertionError):
                self.check_build_text(app_build=app_build)

    def test_rejects_noncanonical_wrapper_content(self):
        checksum = "distributionSha256Sum=bbaeb2fef8710818cf0e261201dab964c572f92b942812df0c3620d62a529a01"
        url = "distributionUrl=https\\://services.gradle.org/distributions/gradle-9.6.0-bin.zip"
        mutations = {
            "dynamic version": WRAPPER_WITH_UPDATED_GRADLE.replace("gradle-9.6.0-bin.zip", "gradle-latest-bin.zip"),
            "comment": WRAPPER_WITH_UPDATED_GRADLE + "# unexpected\n",
            "duplicate url": WRAPPER_WITH_UPDATED_GRADLE.replace(url, url + "\n" + url),
            "missing checksum": WRAPPER_WITH_UPDATED_GRADLE.replace(checksum + "\n", ""),
            "duplicate checksum": WRAPPER_WITH_UPDATED_GRADLE.replace(checksum, checksum + "\n" + checksum),
            "empty checksum": WRAPPER_WITH_UPDATED_GRADLE.replace(checksum, "distributionSha256Sum=\n" + checksum),
            "colon separator": WRAPPER_WITH_UPDATED_GRADLE + "distributionUrl: gradle-latest-bin.zip\n",
            "whitespace separator": WRAPPER_WITH_UPDATED_GRADLE + "distributionSha256Sum deadbeef\n",
            "unicode key": WRAPPER_WITH_UPDATED_GRADLE + "distribution\\u0055rl=gradle-latest-bin.zip\n",
            "continuation": WRAPPER_WITH_UPDATED_GRADLE + "unexpected=one\\\ntwo\n",
            "extra key": WRAPPER_WITH_UPDATED_GRADLE + "unexpected=true\n",
        }

        for name, wrapper in mutations.items():
            with self.subTest(name=name), self.assertRaises(AssertionError):
                self.check_build_text(wrapper=wrapper)

    def test_rejects_noncanonical_makefile_content(self):
        canonical_makefile = contracts.CANONICAL_MAKEFILE
        recipe = (
            '\tcd "$(ROOT)" && PYTHONDONTWRITEBYTECODE=1 $(PYTHON) '
            "-m unittest tests.test_check_android_contracts -v\n"
        )
        static_block = (
            "static:\n"
            + recipe
            + '\t$(PYTHON) "$(ROOT)/scripts/check_android_contracts.py"\n'
        )
        mutations = {
            "duplicate recipe": canonical_makefile.replace(recipe, recipe + recipe),
            "recipe under decoy target": canonical_makefile.replace(
                static_block,
                "decoy:\n"
                + recipe
                + "\nstatic:\n"
                + '\t$(PYTHON) "$(ROOT)/scripts/check_android_contracts.py"\n',
            ),
            "no-op static target": canonical_makefile.replace(
                static_block,
                "decoy:\n"
                + recipe
                + '\t$(PYTHON) "$(ROOT)/scripts/check_android_contracts.py"\n\n'
                + "static: ; @true\n",
            ),
            "disabled python": canonical_makefile.replace("PYTHON ?= python3", "PYTHON := true"),
        }

        for name, makefile in mutations.items():
            with self.subTest(name=name), self.assertRaises(AssertionError):
                self.check_build_text(makefile=makefile)

    def test_requires_checkout_and_metadata_gates_in_makefile(self):
        self.check_build_text(makefile=MAKEFILE)


class CheckoutIntegrityContractsTest(unittest.TestCase):
    def test_repository_line_endings_are_canonical(self):
        self.assertEqual(
            (contracts.ROOT / ".gitattributes").read_text(encoding="utf-8"),
            "* text=auto\ngradlew text eol=lf\ngradlew.bat text eol=crlf\n",
        )
        index_bytes = subprocess.run(
            ["git", "show", ":gradlew.bat"],
            cwd=contracts.ROOT,
            check=True,
            stdout=subprocess.PIPE,
        ).stdout
        self.assertNotIn(b"\r", index_bytes)
        self.assertIn(b"\r\n", (contracts.ROOT / "gradlew.bat").read_bytes())
        eol = subprocess.run(
            ["git", "ls-files", "--eol", "gradlew", "gradlew.bat"],
            cwd=contracts.ROOT,
            check=True,
            stdout=subprocess.PIPE,
            text=True,
        ).stdout
        self.assertRegex(eol, r"(?m)^i/lf\s+w/lf\s+attr/text eol=lf\s+gradlew$")
        self.assertRegex(eol, r"(?m)^i/lf\s+w/crlf\s+attr/text eol=crlf\s+gradlew\.bat$")


class RunAndroidVerificationTest(unittest.TestCase):
    def run_verifier(self, output, exit_code=0, require_app_dependency_insight=False):
        with tempfile.TemporaryDirectory() as temp_dir:
            fake_gradle = Path(temp_dir) / "gradle"
            argument_guard = ""
            if require_app_dependency_insight:
                argument_guard = (
                    "if any(argument.endswith('dependencyInsight') for argument in sys.argv) "
                    "and ':app:dependencyInsight' not in sys.argv:\n    sys.exit(9)\n"
                )
            fake_gradle.write_text(
                f"#!{sys.executable}\nimport sys\n{argument_guard}"
                f"print({output!r})\nsys.exit({exit_code})\n",
                encoding="utf-8",
            )
            fake_gradle.chmod(0o755)
            return subprocess.run(
                [
                    sys.executable,
                    str(contracts.ROOT / "scripts" / "run_android_verification.py"),
                    str(fake_gradle),
                ],
                cwd=contracts.ROOT,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False,
            )

    def test_rejects_successful_gradle_output_with_kotlin_metadata_errors(self):
        result = self.run_verifier(
            "org.jetbrains.kotlin:kotlin-stdlib:2.2.21\n"
            "An error occurred when parsing kotlin metadata\n"
            "BUILD SUCCESSFUL"
        )

        self.assertEqual(result.returncode, 1)
        self.assertIn("Kotlin metadata incompatibility", result.stderr)

    def test_accepts_clean_gradle_output_with_expected_kotlin_resolution(self):
        result = self.run_verifier(
            "org.jetbrains.kotlin:kotlin-stdlib:2.2.21\nBUILD SUCCESSFUL"
        )

        self.assertEqual(result.returncode, 0, result.stderr)

    def test_rejects_dependency_insight_forced_to_newer_kotlin(self):
        result = self.run_verifier(
            "org.jetbrains.kotlin:kotlin-stdlib:2.2.21 -> 2.4.0\nBUILD SUCCESSFUL"
        )

        self.assertEqual(result.returncode, 1)
        self.assertIn("resolved unexpected Kotlin stdlib", result.stderr)

    def test_scopes_dependency_insight_to_app_project(self):
        result = self.run_verifier(
            "org.jetbrains.kotlin:kotlin-stdlib:2.2.21\nBUILD SUCCESSFUL",
            require_app_dependency_insight=True,
        )

        self.assertEqual(result.returncode, 0, result.stderr)

    def test_propagates_gradle_failure(self):
        result = self.run_verifier("Gradle failed", exit_code=7)

        self.assertEqual(result.returncode, 7)


class ServiceCoordinatePayloadContractsTest(unittest.TestCase):
    SERVICE = """else if(fetchType == Constants.USE_ADDRESS_LOCATION) {
        if(!intent.hasExtra(Constants.LOCATION_LATITUDE_DATA_EXTRA)
                || !intent.hasExtra(Constants.LOCATION_LONGITUDE_DATA_EXTRA)) {
            errorMessage = \"Invalid Latitude or Longitude Used\";
        } else {
            double latitude = intent.getDoubleExtra(Constants.LOCATION_LATITUDE_DATA_EXTRA, 0);
            double longitude = intent.getDoubleExtra(Constants.LOCATION_LONGITUDE_DATA_EXTRA, 0);
            addresses = geocoder.getFromLocation(latitude, longitude, 1);
        }
        }
        else {
        errorMessage = "Unknown Type";
        }
"""

    def test_requires_paired_coordinate_extra_guard_before_reads(self):
        contracts.check_service_coordinate_payload_text(self.SERVICE)

        mutations = {
            "missing latitude presence": self.SERVICE.replace(
                "!intent.hasExtra(Constants.LOCATION_LATITUDE_DATA_EXTRA)\n"
                "                || ",
                "",
                1,
            ),
            "missing longitude presence": self.SERVICE.replace(
                "\n                || !intent.hasExtra(Constants.LOCATION_LONGITUDE_DATA_EXTRA)",
                "",
                1,
            ),
            "guard after coordinate reads": self.SERVICE.replace(
                "        if(!intent.hasExtra(Constants.LOCATION_LATITUDE_DATA_EXTRA)\n"
                "                || !intent.hasExtra(Constants.LOCATION_LONGITUDE_DATA_EXTRA)) {\n"
                "            errorMessage = \"Invalid Latitude or Longitude Used\";\n"
                "        } else {\n"
                "            double latitude = intent.getDoubleExtra(Constants.LOCATION_LATITUDE_DATA_EXTRA, 0);\n"
                "            double longitude = intent.getDoubleExtra(Constants.LOCATION_LONGITUDE_DATA_EXTRA, 0);\n",
                "        double latitude = intent.getDoubleExtra(Constants.LOCATION_LATITUDE_DATA_EXTRA, 0);\n"
                "        double longitude = intent.getDoubleExtra(Constants.LOCATION_LONGITUDE_DATA_EXTRA, 0);\n"
                "        if(!intent.hasExtra(Constants.LOCATION_LATITUDE_DATA_EXTRA)\n"
                "                || !intent.hasExtra(Constants.LOCATION_LONGITUDE_DATA_EXTRA)) {\n"
                "            errorMessage = \"Invalid Latitude or Longitude Used\";\n"
                "        } else {\n",
                1,
            ),
        }
        for name, service in mutations.items():
            with self.subTest(name=name), self.assertRaises(AssertionError):
                contracts.check_service_coordinate_payload_text(service)


class StaticVerificationEntryPointTest(unittest.TestCase):
    def test_make_static_runs_from_outside_repository(self):
        if os.environ.get("ANDROID_CONTRACT_EXTERNAL_MAKE_TEST") == "1":
            self.assertEqual(contracts.ROOT, Path.cwd())
            return

        environment = os.environ.copy()
        environment["ANDROID_CONTRACT_EXTERNAL_MAKE_TEST"] = "1"
        with tempfile.TemporaryDirectory() as temporary_directory:
            result = subprocess.run(
                ["make", "-f", str(contracts.ROOT / "Makefile"), "static"],
                cwd=temporary_directory,
                env=environment,
                capture_output=True,
                text=True,
                check=False,
            )

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)


class CheckDependabotContractsTest(unittest.TestCase):
    def test_requires_kotlin_agp_compatibility_ceiling(self):
        contracts.check_dependabot_contracts_text(VALID_DEPENDABOT)

        kotlin_ceiling = (
            "      # Kotlin 2.3+ requires AGP 8.13.2; remove after the AGP migration.\n"
            "      - dependency-name: \"org.jetbrains.kotlin:kotlin-bom\"\n"
            "        versions:\n"
            "          - \"[2.3.0,)\"\n"
        )
        mutations = {
            "missing ceiling": VALID_DEPENDABOT.replace(kotlin_ceiling, "", 1),
            "compatible 2.2 updates ignored": VALID_DEPENDABOT.replace(
                "[2.3.0,)", "[2.2.0,)", 1
            ),
            "Kotlin 2.3 updates remain allowed": VALID_DEPENDABOT.replace(
                "[2.3.0,)", "[2.4.0,)", 1
            ),
        }

        for name, dependabot in mutations.items():
            with self.subTest(name=name), self.assertRaises(AssertionError):
                contracts.check_dependabot_contracts_text(dependabot)

    def test_requires_api_21_lifecycle_version_ceiling(self):
        contracts.check_dependabot_contracts_text(VALID_DEPENDABOT)

        lifecycle_ceiling = (
            "    ignore:\n"
            "      # Lifecycle 2.10+ requires minSdk 23; remove after the API 21 migration.\n"
            "      - dependency-name: \"androidx.lifecycle:*\"\n"
            "        versions:\n"
            "          - \"[2.10.0,)\"\n"
        )
        mutations = {
            "missing ceiling": VALID_DEPENDABOT.replace(lifecycle_ceiling, "", 1),
            "all Lifecycle updates ignored": VALID_DEPENDABOT.replace(
                "        versions:\n          - \"[2.10.0,)\"\n", "", 1
            ),
            "compatible 2.9 updates ignored": VALID_DEPENDABOT.replace(
                "[2.10.0,)", "[2.9.0,)", 1
            ),
        }

        for name, dependabot in mutations.items():
            with self.subTest(name=name), self.assertRaises(AssertionError):
                contracts.check_dependabot_contracts_text(dependabot)

    def test_accepts_canonical_content_with_optional_trailing_newline(self):
        contracts.check_dependabot_contracts_text(VALID_DEPENDABOT)
        contracts.check_dependabot_contracts_text(VALID_DEPENDABOT.rstrip("\n"))

    def test_rejects_noncanonical_content(self):
        gradle_block = VALID_DEPENDABOT.split("  - package-ecosystem: github-actions\n", 1)[0]
        mutations = {
            "missing update types": VALID_DEPENDABOT.replace(
                "        update-types:\n          - minor\n          - patch\n", "", 1
            ),
            "major grouped": VALID_DEPENDABOT.replace(
                "          - patch\n", "          - patch\n          - major\n", 1
            ),
            "missing groups": VALID_DEPENDABOT.replace("    groups:\n", "", 1),
            "misindented groups": VALID_DEPENDABOT.replace(
                "    groups:\n", "  groups:\n", 1
            ),
            "extra wildcard group": VALID_DEPENDABOT.replace(
                "      android-dependencies:\n",
                "      all-gradle-majors:\n"
                "        patterns:\n"
                "          - \"*\"\n"
                "      android-dependencies:\n",
                1,
            ),
            "duplicate groups": VALID_DEPENDABOT.replace(
                "  - package-ecosystem: github-actions\n",
                "    groups:\n"
                "      unsafe-override:\n"
                "        patterns:\n"
                "          - \"*\"\n"
                "  - package-ecosystem: github-actions\n",
            ),
            "extra setting": VALID_DEPENDABOT.replace(
                "    schedule:\n      interval: weekly\n",
                "    schedule:\n"
                "      interval: weekly\n"
                "    open-pull-requests-limit: 5\n",
                1,
            ),
            "duplicate ecosystem": (
                VALID_DEPENDABOT + gradle_block.split("updates:\n", 1)[1]
            ),
            "flow groups": VALID_DEPENDABOT.replace(
                "    groups:\n"
                "      android-dependencies:\n"
                "        patterns:\n"
                "          - \"*\"\n"
                "        update-types:\n"
                "          - minor\n"
                "          - patch\n",
                "    groups: { android-dependencies: { patterns: [\"*\"], "
                "update-types: [minor, patch] } }\n",
                1,
            ),
        }

        for name, dependabot in mutations.items():
            with self.subTest(name=name), self.assertRaises(AssertionError):
                contracts.check_dependabot_contracts_text(dependabot)

    def test_main_invokes_dependabot_contracts(self):
        with (
            patch.object(contracts, "check_docs_plans", lambda: None),
            patch.object(contracts, "check_xml_resources", lambda: None),
            patch.object(contracts, "check_manifest_contracts", lambda: None),
            patch.object(contracts, "check_gradle_application_id", lambda: None),
            patch.object(contracts, "check_hosted_verification", lambda: None),
            patch.object(contracts, "check_coordinate_input_guard", lambda: None),
            patch.object(contracts, "check_modern_android_build", lambda: None),
            patch.object(contracts, "read_text", return_value="version: 2\nupdates: []\n"),
            redirect_stderr(io.StringIO()),
        ):
            self.assertEqual(1, contracts.main())


if __name__ == "__main__":
    unittest.main()

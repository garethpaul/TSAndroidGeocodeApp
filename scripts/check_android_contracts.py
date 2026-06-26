#!/usr/bin/env python3
"""Static verification for the legacy Android geocode sample."""

import logging
from pathlib import Path
import re
import subprocess
import sys
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
ANDROID_NS = "http://schemas.android.com/apk/res/android"
DOCS_PLANS = ROOT / "docs" / "plans"
CANONICAL_PLAN = DOCS_PLANS / "2026-06-08-tsandroidgeocodeapp-baseline.md"
RESULT_RECEIVER_PAYLOAD_PLAN = DOCS_PLANS / "2026-06-09-result-receiver-payload-guard.md"
ANDROID_BACKUP_PLAN = DOCS_PLANS / "2026-06-09-android-backup-opt-out.md"
STALE_CHECKBOX_PLAN = DOCS_PLANS / "2026-06-09-stale-checkbox-reference.md"
HOSTED_VERIFICATION_PLAN = DOCS_PLANS / "2026-06-10-hosted-static-verification.md"
LIFECYCLE_RECEIVER_PLAN = DOCS_PLANS / "2026-06-10-result-receiver-lifecycle.md"
GEOCODE_LOG_PRIVACY_PLAN = DOCS_PLANS / "2026-06-12-geocode-log-privacy.md"
TYPED_RECEIVER_PLAN = DOCS_PLANS / "2026-06-13-typed-result-receiver-extra.md"
GEOCODER_AVAILABILITY_PLAN = DOCS_PLANS / "2026-06-13-geocoder-availability.md"
SINGLE_INFLIGHT_PLAN = DOCS_PLANS / "2026-06-13-single-inflight-geocode-request.md"
ROOT_OVERRIDE_PLAN = DOCS_PLANS / "2026-06-14-make-root-override-protection.md"
RECREATION_RESULT_PLAN = DOCS_PLANS / "2026-06-17-activity-recreation-result-state.md"
API_FLOOR_DECISION_PLAN = DOCS_PLANS / "2026-06-25-api-21-lifecycle-decision.md"
EXPECTED_AGP_VERSION = "8.10.1"
EXPECTED_KOTLIN_BOM_VERSION = "2.2.21"
EXPECTED_GRADLE_VERSION = "9.6.0"
EXPECTED_GRADLE_DISTRIBUTION_SHA256 = (
    "bbaeb2fef8710818cf0e261201dab964c572f92b942812df0c3620d62a529a01"
)
GRADLE_WRAPPER_JAR_SHA256 = "497c8c2a7e5031f6aa847f88104aa80a93532ec32ee17bdb8d1d2f67a194a9c7"
CANONICAL_GITATTRIBUTES = "* text=auto\ngradlew text eol=lf\ngradlew.bat text eol=crlf\n"
KOTLIN_MINIMUM_AGP = {
    (1, 8): (7, 4, 0),
    (1, 9): (8, 0, 0),
    (2, 0): (8, 5, 0),
    (2, 1): (8, 6, 0),
    (2, 2): (8, 10, 0),
    (2, 3): (8, 13, 2),
    (2, 4): (9, 1, 0),
}
ACTION_LINE_PATTERN = re.compile(
    r"^        uses: "
    r"(?P<action>actions/(?:checkout|setup-python|setup-java))"
    r"@[0-9a-f]{40} # v\d+\.\d+\.\d+$"
)
ROOT_BUILD_PATTERN = re.compile(
    r'plugins \{\n'
    r'    id "com\.android\.application" version "(?P<version>\d+\.\d+\.\d+)" apply false\n'
    r'\}\n?'
)
KOTLIN_BOM_PATTERN = re.compile(
    r"^    implementation platform\('org\.jetbrains\.kotlin:"
    r"kotlin-bom:(?P<version>\d+\.\d+\.\d+)'\)$",
    re.MULTILINE,
)
APP_DEPENDENCY_PATTERNS = (
    (
        "kotlin-bom",
        re.compile(
            r"^    implementation platform\('org\.jetbrains\.kotlin:"
            r"kotlin-bom:\d+\.\d+\.\d+'\)$"
        ),
        "    implementation platform('org.jetbrains.kotlin:kotlin-bom:<VERSION>')",
    ),
    (
        "appcompat",
        re.compile(
            r"^    implementation 'androidx\.appcompat:appcompat:"
            r"\d+\.\d+\.\d+'$"
        ),
        "    implementation 'androidx.appcompat:appcompat:<VERSION>'",
    ),
    (
        "lifecycle-livedata",
        re.compile(
            r"^    implementation 'androidx\.lifecycle:lifecycle-livedata:"
            r"\d+\.\d+\.\d+'$"
        ),
        "    implementation 'androidx.lifecycle:lifecycle-livedata:<VERSION>'",
    ),
    (
        "lifecycle-viewmodel",
        re.compile(
            r"^    implementation 'androidx\.lifecycle:lifecycle-viewmodel:"
            r"\d+\.\d+\.\d+'$"
        ),
        "    implementation 'androidx.lifecycle:lifecycle-viewmodel:<VERSION>'",
    ),
    (
        "core-testing",
        re.compile(
            r"^    testImplementation 'androidx\.arch\.core:core-testing:"
            r"\d+\.\d+\.\d+'$"
        ),
        "    testImplementation 'androidx.arch.core:core-testing:<VERSION>'",
    ),
    (
        "junit",
        re.compile(r"^    testImplementation 'junit:junit:\d+\.\d+\.\d+'$"),
        "    testImplementation 'junit:junit:<VERSION>'",
    ),
)
CANONICAL_APP_BUILD = """plugins {
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
    implementation platform('org.jetbrains.kotlin:kotlin-bom:<VERSION>')
    implementation 'androidx.appcompat:appcompat:<VERSION>'
    //noinspection GradleDependency -- Lifecycle 2.10+ requires minSdk 23.
    implementation 'androidx.lifecycle:lifecycle-livedata:<VERSION>'
    //noinspection GradleDependency -- Lifecycle 2.10+ requires minSdk 23.
    implementation 'androidx.lifecycle:lifecycle-viewmodel:<VERSION>'

    testImplementation 'androidx.arch.core:core-testing:<VERSION>'
    testImplementation 'junit:junit:<VERSION>'
}"""
CANONICAL_GRADLE_WRAPPER = f"""distributionBase=GRADLE_USER_HOME
distributionPath=wrapper/dists
distributionSha256Sum={EXPECTED_GRADLE_DISTRIBUTION_SHA256}
distributionUrl=https\\://services.gradle.org/distributions/gradle-{EXPECTED_GRADLE_VERSION}-bin.zip
networkTimeout=10000
validateDistributionUrl=true
zipStoreBase=GRADLE_USER_HOME
zipStorePath=wrapper/dists
"""
CANONICAL_WORKFLOW = """name: Check

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
        uses: actions/checkout@<SHA> # v<VERSION>
        with:
          persist-credentials: false
      - name: Verify clean checkout
        run: make checkout-integrity
      - name: Set up Python
        uses: actions/setup-python@<SHA> # v<VERSION>
        with:
          python-version: ${{ matrix.python-version }}
      - name: Run repository verification
        run: make static

  android:
    runs-on: ubuntu-24.04
    timeout-minutes: 15
    steps:
      - name: Check out repository
        uses: actions/checkout@<SHA> # v<VERSION>
        with:
          persist-credentials: false
      - name: Verify clean checkout
        run: make checkout-integrity
      - name: Set up Java
        uses: actions/setup-java@<SHA> # v<VERSION>
        with:
          distribution: temurin
          java-version: "17"
          cache: gradle
      - name: Install Android SDK packages
        run: '"$ANDROID_HOME/cmdline-tools/latest/bin/sdkmanager" "platforms;android-36" "build-tools;35.0.0"'
      - name: Run Android verification
        run: make check
      - name: Verify build kept checkout clean
        run: make checkout-integrity"""
CANONICAL_MAKEFILE = """.PHONY: build check checkout-integrity lint static test verify

override ROOT := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))
PYTHON ?= python3
GRADLEW ?= $(ROOT)/gradlew

checkout-integrity:
	cd "$(ROOT)" && test -z "$$(git status --porcelain --untracked-files=no)"
	cd "$(ROOT)" && git ls-files --eol gradlew | grep -Eq '^i/lf[[:space:]]+w/lf[[:space:]]+attr/text eol=lf[[:space:]]+gradlew$$'
	cd "$(ROOT)" && git ls-files --eol gradlew.bat | grep -Eq '^i/lf[[:space:]]+w/crlf[[:space:]]+attr/text eol=crlf[[:space:]]+gradlew[.]bat$$'

static:
	cd "$(ROOT)" && PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest tests.test_check_android_contracts -v
	$(PYTHON) "$(ROOT)/scripts/check_android_contracts.py"

test:
	cd "$(ROOT)" && "$(GRADLEW)" --no-daemon testDebugUnitTest

build:
	cd "$(ROOT)" && "$(GRADLEW)" --no-daemon assembleDebug

lint: static
	cd "$(ROOT)" && "$(GRADLEW)" --no-daemon lintDebug

verify: static
	cd "$(ROOT)" && $(PYTHON) "$(ROOT)/scripts/run_android_verification.py" "$(GRADLEW)"

check: verify"""
CANONICAL_DEPENDABOT = """version: 2
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
          - patch"""


def fail(message):
    print(f"check_android_contracts.py: {message}", file=sys.stderr)
    return 1


def read_text(relative_path):
    return (ROOT / relative_path).read_text(encoding="utf-8")


def parse_xml(relative_path):
    try:
        return ET.parse(ROOT / relative_path)
    except ET.ParseError as exc:
        raise AssertionError(f"{relative_path} is not well-formed XML: {exc}")


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def check_docs_plans():
    require(
        CANONICAL_PLAN.exists(),
        "docs/plans/2026-06-08-tsandroidgeocodeapp-baseline.md is missing",
    )
    require(
        RESULT_RECEIVER_PAYLOAD_PLAN.exists(),
        "docs/plans/2026-06-09-result-receiver-payload-guard.md is missing",
    )
    require(
        ANDROID_BACKUP_PLAN.exists(),
        "docs/plans/2026-06-09-android-backup-opt-out.md is missing",
    )
    require(
        STALE_CHECKBOX_PLAN.exists(),
        "docs/plans/2026-06-09-stale-checkbox-reference.md is missing",
    )
    require(
        HOSTED_VERIFICATION_PLAN.exists(),
        "docs/plans/2026-06-10-hosted-static-verification.md is missing",
    )
    require(
        LIFECYCLE_RECEIVER_PLAN.exists(),
        "docs/plans/2026-06-10-result-receiver-lifecycle.md is missing",
    )
    require(
        GEOCODE_LOG_PRIVACY_PLAN.exists(),
        "docs/plans/2026-06-12-geocode-log-privacy.md is missing",
    )
    require(
        TYPED_RECEIVER_PLAN.exists(),
        "docs/plans/2026-06-13-typed-result-receiver-extra.md is missing",
    )
    require(
        GEOCODER_AVAILABILITY_PLAN.exists(),
        "docs/plans/2026-06-13-geocoder-availability.md is missing",
    )
    require(
        SINGLE_INFLIGHT_PLAN.exists(),
        "docs/plans/2026-06-13-single-inflight-geocode-request.md is missing",
    )
    require(
        ROOT_OVERRIDE_PLAN.exists(),
        "docs/plans/2026-06-14-make-root-override-protection.md is missing",
    )
    require(
        RECREATION_RESULT_PLAN.exists(),
        "docs/plans/2026-06-17-activity-recreation-result-state.md is missing",
    )
    require(
        API_FLOOR_DECISION_PLAN.exists(),
        "docs/plans/2026-06-25-api-21-lifecycle-decision.md is missing",
    )

    plans = sorted(DOCS_PLANS.glob("*.md")) if DOCS_PLANS.exists() else []
    require(plans, "docs/plans must contain at least one completed plan")

    for plan_path in plans:
        plan = plan_path.read_text(encoding="utf-8")
        require(
            "Status: Completed" in plan and "make check" in plan,
            f"{plan_path.relative_to(ROOT)} must record completed status and make check verification",
        )

    documentation_contracts = {
        "README.md": "retained across Activity configuration recreation",
        "SECURITY.md": "retained screen state never stores an Activity, View, or Context",
        "VISION.md": "Retain in-flight geocode state across Activity configuration recreation",
    }
    for relative_path, contract in documentation_contracts.items():
        require(
            contract in read_text(relative_path),
            f"{relative_path} must document recreation-safe result ownership",
        )

    readme = read_text("README.md")
    vision = read_text("VISION.md")
    for contract in (
        "Retain the API 21 minimum",
        "AndroidX Lifecycle 2.9.4",
        "Lifecycle 2.10.0 raised its minimum from API 21 to API 23",
        "IntentService and geocoder migration",
    ):
        require(contract in readme, f"README.md must document the platform-floor decision: {contract}")
    require(
        "Decide whether to raise the API floor from 21 to 23" not in vision,
        "VISION.md must not retain the completed API-floor decision as future work",
    )
    require(
        "Retain API 21 and Lifecycle 2.9.4 until a dedicated, tested lifecycle migration" in vision,
        "VISION.md must record the API-floor decision",
    )


def check_xml_resources():
    for relative_path in [
        "app/src/main/AndroidManifest.xml",
        "app/src/main/res/layout/activity_main.xml",
        "app/src/main/res/values/strings.xml",
        "app/src/main/res/values/styles.xml",
        "app/src/main/res/values/dimens.xml",
        "app/src/main/res/xml/data_extraction_rules.xml",
    ]:
        parse_xml(relative_path)


def check_manifest_contracts():
    manifest = parse_xml("app/src/main/AndroidManifest.xml").getroot()
    application = manifest.find("application")
    require(application is not None, "manifest must declare an application")
    require(
        application.attrib.get(f"{{{ANDROID_NS}}}allowBackup") == "false",
        "manifest application must explicitly disable app-data backup",
    )
    require(
        application.attrib.get(f"{{{ANDROID_NS}}}dataExtractionRules")
        == "@xml/data_extraction_rules",
        "manifest must disable Android 12+ cloud backup and device transfer",
    )

    service_names = {
        service.attrib.get(f"{{{ANDROID_NS}}}name")
        for service in application.findall("service")
    }
    require(
        "com.sample.foo.tsgeocodeapp.GeocodeAddressIntentService" in service_names,
        "geocode IntentService must remain declared",
    )

    activity_names = [
        activity.attrib.get(f"{{{ANDROID_NS}}}name")
        for activity in application.findall("activity")
    ]
    require(
        "com.sample.foo.tsgeocodeapp.MainActivity" in activity_names,
        "MainActivity must remain the declared activity",
    )


def check_gradle_application_id():
    build_gradle = read_text("app/build.gradle")
    match = re.search(r"applicationId\s*=\s*['\"]([^'\"]+)['\"]", build_gradle)
    require(match is not None, "app/build.gradle must declare an applicationId")
    require(
        match.group(1) == "com.sample.foo.tsgeocodeapp",
        "Gradle applicationId must match the manifest and Java package",
    )


def check_hosted_verification_text(workflow):
    normalized_lines = []
    actions = []
    for line in workflow.splitlines():
        match = ACTION_LINE_PATTERN.fullmatch(line)
        if match is None:
            normalized_lines.append(line)
            continue
        action = match.group("action")
        actions.append(action)
        normalized_lines.append(f"        uses: {action}@<SHA> # v<VERSION>")

    require(
        actions
        == [
            "actions/checkout",
            "actions/setup-python",
            "actions/checkout",
            "actions/setup-java",
        ],
        "hosted verification must contain exactly four canonical action lines",
    )
    normalized = "\n".join(normalized_lines)
    require(
        normalized in (CANONICAL_WORKFLOW, CANONICAL_WORKFLOW + "\n"),
        ".github/workflows/check.yml must match the canonical workflow template",
    )


def check_hosted_verification():
    workflow_files = sorted((ROOT / ".github" / "workflows").glob("*"))
    require(
        workflow_files == [ROOT / ".github" / "workflows" / "check.yml"],
        "hosted verification must contain only the reviewed check workflow",
    )
    check_hosted_verification_text(read_text(".github/workflows/check.yml"))


def check_service_coordinate_payload_text(service):
    location_branch = re.search(
        r"else if\(fetchType == Constants\.USE_ADDRESS_LOCATION\) \{"
        r"(?P<body>.*?)\n        \}\n        else \{",
        service,
        re.DOTALL,
    )
    require(
        location_branch is not None,
        "IntentService must keep a dedicated location-mode request branch",
    )
    body = location_branch.group("body")
    presence_guard = re.search(
        r"if\s*\(\s*!intent\.hasExtra\(Constants\.LOCATION_LATITUDE_DATA_EXTRA\)"
        r"\s*\|\|\s*!intent\.hasExtra\(Constants\.LOCATION_LONGITUDE_DATA_EXTRA\)"
        r"\s*\)",
        body,
    )
    require(
        presence_guard is not None,
        "IntentService must reject location requests missing either coordinate extra",
    )

    latitude_read = re.search(
        r"intent\.getDoubleExtra\(\s*Constants\.LOCATION_LATITUDE_DATA_EXTRA",
        body,
    )
    longitude_read = re.search(
        r"intent\.getDoubleExtra\(\s*Constants\.LOCATION_LONGITUDE_DATA_EXTRA",
        body,
    )
    geocoder_lookup = re.search(
        r"addresses\s*=\s*geocoder\.getFromLocation\(latitude, longitude, 1\)",
        body,
    )
    require(
        latitude_read is not None
        and longitude_read is not None
        and geocoder_lookup is not None,
        "IntentService must keep coordinate reads and geocoder lookup",
    )
    require(
        presence_guard.start() < latitude_read.start()
        and presence_guard.start() < longitude_read.start()
        and presence_guard.start() < geocoder_lookup.start(),
        "IntentService must verify coordinate extras before reading or geocoding them",
    )


def check_result_coordinate_guard_text(view_model):
    result_handler = re.search(
        r"private void handleGeocodeResult\(int resultCode, Bundle resultData\) \{"
        r"(?P<body>.*?)\n    \}",
        view_model,
        re.DOTALL,
    )
    require(result_handler is not None, "Geocode result handler must remain present")
    handler_body = result_handler.group("body")
    presence_guard = re.search(
        r"address == null\s*\|\|\s*!address\.hasLatitude\(\)"
        r"\s*\|\|\s*!address\.hasLongitude\(\)\) \{"
        r"(?P<body>.*?)\n\s*\}",
        handler_body,
        re.DOTALL,
    )
    latitude_read = handler_body.find("address.getLatitude()")
    longitude_read = handler_body.find("address.getLongitude()")
    require(
        presence_guard is not None,
        "successful geocode results must require assigned latitude and longitude",
    )
    require(
        "completeResult(resultCode, null, null, resultMessage);"
        in presence_guard.group("body")
        and "return;" in presence_guard.group("body"),
        "missing Address coordinates must settle with the safe fallback before returning",
    )
    require(
        latitude_read >= 0
        and longitude_read >= 0
        and presence_guard.start() < latitude_read
        and presence_guard.start() < longitude_read,
        "Address coordinate presence must be checked before either throwing getter",
    )

    completion = re.search(
        r"void completeResult\(int resultCode, Double latitude, Double longitude, String message\) \{"
        r"(?P<body>.*?)\n    \}",
        view_model,
        re.DOTALL,
    )
    require(completion is not None, "Geocode result completion must remain present")
    require(
        "GeocodeInputValidator.isCoordinateInRange(latitude, longitude)"
        in completion.group("body"),
        "successful geocode results must reject non-finite and out-of-range coordinates",
    )


def check_coordinate_input_guard():
    main_activity = read_text("app/src/main/java/com/sample/foo/tsgeocodeapp/MainActivity.java")
    view_model = read_text("app/src/main/java/com/sample/foo/tsgeocodeapp/GeocodeViewModel.java")
    service = read_text("app/src/main/java/com/sample/foo/tsgeocodeapp/GeocodeAddressIntentService.java")
    validator = read_text("app/src/main/java/com/sample/foo/tsgeocodeapp/GeocodeInputValidator.java")
    validator_test = read_text("app/src/test/java/com/sample/foo/tsgeocodeapp/GeocodeInputValidatorTest.java")
    view_model_test = read_text("app/src/test/java/com/sample/foo/tsgeocodeapp/GeocodeViewModelTest.java")
    strings = read_text("app/src/main/res/values/strings.xml")

    check_service_coordinate_payload_text(service)
    check_result_coordinate_guard_text(view_model)
    for relative_path, contract in {
        "README.md": "Successful geocoder callbacks require assigned",
        "SECURITY.md": "Successful geocoder callbacks require assigned",
        "VISION.md": "Require assigned, finite, in-range coordinates",
        "CHANGES.md": "missing coordinate assignments",
    }.items():
        require(
            contract in read_text(relative_path),
            f"{relative_path} must document successful result coordinate validation",
        )
    for relative_path, contract in {
        "README.md": "require both coordinate extras",
        "SECURITY.md": "require both coordinate extras",
        "VISION.md": "Require both coordinate extras",
        "CHANGES.md": "latitude or longitude extras",
    }.items():
        require(
            contract in read_text(relative_path),
            f"{relative_path} must document incomplete coordinate payload rejection",
        )

    require(
        not (ROOT / "app/src/main/java/com/sample/foo/tsgeocodeapp/MainActivityWithAsyncTask.java").exists(),
        "deprecated, undeclared AsyncTask activity must remain removed",
    )
    require(
        "import android.widget.CheckBox;" not in main_activity,
        "MainActivity must not import the removed checkbox widget",
    )
    require(
        "R.id.checkbox" not in main_activity,
        "MainActivity must not reference a layout checkbox that is not declared",
    )
    require(
        "int fetchType = Constants.USE_ADDRESS_LOCATION;" not in main_activity,
        "MainActivity must not keep a recreation-prone geocode mode field",
    )

    match = re.search(
        r"public void onButtonClicked\(View view\) \{(?P<body>.*?)\n    \}",
        main_activity,
        re.DOTALL,
    )
    require(match is not None, "MainActivity.onButtonClicked must be present")
    body = match.group("body")

    require(
        "((RadioButton) findViewById(R.id.radioAddress)).isChecked()" in body,
        "MainActivity must derive the fetch mode from the restored radio state",
    )
    require(
        body.index("((RadioButton) findViewById(R.id.radioAddress)).isChecked()")
        < body.index("intent.putExtra(Constants.FETCH_TYPE_EXTRA, fetchType)"),
        "MainActivity must derive the fetch mode before creating the service request",
    )

    require(
        "R.string.invalid_latitude_longitude" in body,
        "invalid coordinate feedback must use the shared string resource",
    )
    require(
        "GeocodeInputValidator.normalizeAddress" in body,
        "MainActivity must normalize address-name input before validation",
    )
    require(
        "if(addressName.length() == 0)" in body,
        "MainActivity must reject blank address-name input after trimming",
    )
    require(
        "intent.putExtra(Constants.LOCATION_NAME_DATA_EXTRA, addressName)" in body,
        "MainActivity must pass the trimmed address name to the IntentService",
    )
    require(
        "intent.putExtra(Constants.LOCATION_NAME_DATA_EXTRA, addressEdit.getText().toString())" not in body,
        "MainActivity must not pass raw address-name input to the IntentService",
    )
    require(
        "catch (NumberFormatException" in body,
        "invalid numeric coordinates must not crash MainActivity",
    )
    require(
        "if(!isCoordinateInRange(latitude, longitude))" in body,
        "out-of-range coordinates must be rejected before starting the service",
    )
    require(
        "GeocodeInputValidator.isCoordinateInRange(latitude, longitude)" in main_activity,
        "MainActivity must delegate coordinate validation to the tested validator",
    )
    require(
        re.search(r"catch \(NumberFormatException [^)]+\) \{\s*Toast\.makeText", body, re.DOTALL),
        "invalid coordinate parse failures must show user feedback",
    )
    require(
        "startService(intent)" in body,
        "valid geocode requests must still start the IntentService",
    )
    require(
        body.index("catch (NumberFormatException") < body.index("startService(intent)"),
        "coordinate parse guard must run before starting the service",
    )
    require(
        body.index("if(!isCoordinateInRange(latitude, longitude))") < body.index("startService(intent)"),
        "coordinate range guard must run before starting the service",
    )
    require(
        "import android.location.Geocoder;" in main_activity,
        "MainActivity must import the platform Geocoder availability API",
    )
    require(
        "if (!Geocoder.isPresent())" in body,
        "MainActivity must reject requests when no geocoder backend is present",
    )
    activity_availability = re.search(
        r"if \(!Geocoder\.isPresent\(\)\) \{(?P<body>.*?)\n        \}",
        body,
        re.DOTALL,
    )
    require(
        activity_availability is not None,
        "MainActivity geocoder availability guard must remain a bounded block",
    )
    activity_availability_body = activity_availability.group("body")
    require(
        "progressBar.setVisibility(View.GONE);" in activity_availability_body,
        "MainActivity must leave progress hidden when geocoding is unavailable",
    )
    require(
        "R.string.geocoder_unavailable" in activity_availability_body,
        "MainActivity must show the localized geocoder unavailable message",
    )
    require(
        "return;" in activity_availability_body,
        "MainActivity must stop before service startup when geocoding is unavailable",
    )
    require(
        "geocodeViewModel.beginRequest()" in body,
        "MainActivity must ask retained state to admit the request",
    )
    require(
        body.index("if (!Geocoder.isPresent())") < body.index("geocodeViewModel.beginRequest()"),
        "MainActivity must check geocoder availability before retaining in-flight state",
    )
    require(
        body.index("if (!Geocoder.isPresent())") < body.index("startService(intent)"),
        "MainActivity must check geocoder availability before starting the service",
    )
    for fragment in (
        "Button actionButton;",
        "actionButton = (Button) findViewById(R.id.actionButton);",
        "actionButton.setOnClickListener(this::onButtonClicked);",
        "GeocodeViewModel geocodeViewModel;",
        "new ViewModelProvider(this).get(GeocodeViewModel.class)",
        "geocodeViewModel.getUiState().observe(this, this::renderUiState);",
        "if (!geocodeViewModel.beginRequest())",
        "intent.putExtra(Constants.RECEIVER, geocodeViewModel.getResultReceiver());",
        "geocodeViewModel.cancelRequest();",
    ):
        require(fragment in main_activity, f"MainActivity retained request guard is missing: {fragment}")
    require(
        body.index("geocodeViewModel.beginRequest()")
        < body.index("intent.putExtra(Constants.RECEIVER, geocodeViewModel.getResultReceiver())")
        < body.index("startService(intent)"),
        "MainActivity must retain request state before service startup",
    )
    render_state = re.search(
        r"private void renderUiState\(GeocodeViewModel\.UiState state\) \{(?P<body>.*?)\n    \}",
        main_activity,
        re.DOTALL,
    )
    require(render_state is not None, "MainActivity must render retained ViewModel state")
    for fragment in (
        "progressBar.setVisibility(requestInFlight ? View.VISIBLE : View.GONE);",
        "actionButton.setEnabled(!requestInFlight);",
        "String displayMessage = state.getDisplayMessage();",
        "infoText.setText(displayMessage);",
    ):
        require(
            fragment in render_state.group("body"),
            f"MainActivity retained state renderer is missing: {fragment}",
        )
    require(
        "AddressResultReceiver" not in main_activity
        and "WeakReference<MainActivity>" not in main_activity
        and "handleGeocodeResult" not in main_activity,
        "MainActivity must not own or interpret the retained service receiver",
    )
    require(
        '<string name="invalid_latitude_longitude">' in strings,
        "strings.xml must define invalid_latitude_longitude",
    )
    require(
        '<string name="geocoder_unavailable">' in strings,
        "strings.xml must define geocoder_unavailable",
    )
    for fragment in (
        "public final class GeocodeViewModel extends ViewModel",
        'static final String NO_GEOCODE_RESULT = "No geocode result";',
        "private final MutableLiveData<UiState> uiState",
        "boolean beginRequest()",
        "void cancelRequest()",
        "void completeResult(int resultCode, Double latitude, Double longitude, String message)",
        "private void completeSuccess(double latitude, double longitude, String addressText)",
        "private void completeFailure(String message)",
        "uiState.setValue(state);",
        "if (resultData == null)",
        "String resultMessage = resultData.getString(Constants.RESULT_DATA_KEY);",
        "BundleCompat.getParcelable(",
        "completeResult(resultCode, null, null, resultMessage);",
        "private static final class AddressResultReceiver extends ResultReceiver",
        "private final WeakReference<GeocodeViewModel> viewModelReference;",
        "super(new Handler(Looper.getMainLooper()));",
        "viewModel.handleGeocodeResult(resultCode, resultData);",
    ):
        require(fragment in view_model, f"GeocodeViewModel result-state guard is missing: {fragment}")
    require(
        all(forbidden not in view_model for forbidden in (
            "MainActivity",
            "android.app.Activity",
            "android.view.View",
            "android.content.Context",
        )),
        "retained GeocodeViewModel state must not store Activity, View, or Context references",
    )
    require(
        "runOnUiThread" not in main_activity and "runOnUiThread" not in view_model,
        "ResultReceiver must dispatch directly through its main-looper Handler",
    )
    for test_name in (
        "initialStateIsIdleWithoutAResult",
        "onlyOneRequestCanBeInFlight",
        "successSettlesTheRequestAndFormatsTheAddress",
        "failureSettlesTheRequestWithItsMessage",
        "missingResultsUseTheSafeFallbackAndSettleTheRequest",
        "successWithoutAnAddressUsesTheSafeFallback",
        "emptyFailureMessageUsesTheSafeFallback",
        "cancelledStartupRestoresIdleStateWithoutInventingAResult",
        "liveDataPublishesEachRetainedStateTransition",
        "retainedStateOwnsNoUiObjectFields",
    ):
        require(test_name in view_model_test, f"ViewModel unit test is missing {test_name}")

    require(
        "name = GeocodeInputValidator.normalizeAddress(name);" in service,
        "IntentService must normalize address-name extras before geocoding",
    )
    require(
        "import androidx.core.content.IntentCompat;" in service,
        "IntentService must import AndroidX IntentCompat",
    )
    require(
        "IntentCompat.getParcelableExtra(" in service
        and "Constants.RECEIVER," in service
        and "ResultReceiver.class" in service,
        "IntentService must read the ResultReceiver through the typed compat API",
    )
    require(
        "intent.getParcelableExtra(Constants.RECEIVER)" not in service,
        "IntentService must not restore the deprecated untyped parcelable read",
    )
    require(
        "if (resultReceiver == null)" in service,
        "IntentService must reject requests without a ResultReceiver",
    )
    require(
        service.index("if (resultReceiver == null)")
        < service.index("Geocoder geocoder = new Geocoder"),
        "IntentService must validate ResultReceiver before creating the geocoder",
    )
    require(
        "if (!Geocoder.isPresent())" in service,
        "IntentService must reject requests when no geocoder backend is present",
    )
    service_availability = re.search(
        r"if \(!Geocoder\.isPresent\(\)\) \{(?P<body>.*?)\n        \}",
        service,
        re.DOTALL,
    )
    require(
        service_availability is not None,
        "IntentService geocoder availability guard must remain a bounded block",
    )
    service_availability_body = service_availability.group("body")
    require(
        "errorMessage = getString(R.string.geocoder_unavailable);"
        in service_availability_body,
        "IntentService must use the localized geocoder unavailable message",
    )
    require(
        "deliverResultToReceiver(Constants.FAILURE_RESULT, errorMessage, null);"
        in service_availability_body,
        "IntentService must deliver unavailable geocoder failures",
    )
    require(
        "return;" in service_availability_body,
        "IntentService must stop before geocoder construction when unavailable",
    )
    require(
        service.index("if (!Geocoder.isPresent())")
        < service.index("Geocoder geocoder = new Geocoder"),
        "IntentService must check geocoder availability before creating the geocoder",
    )
    require(
        "if(TextUtils.isEmpty(name))" in service,
        "IntentService must reject blank address-name extras before geocoding",
    )
    require(
        'errorMessage = "Invalid Address Name";' in service,
        "IntentService must report invalid address-name extras without geocoding",
    )
    require(
        "if(!isCoordinateInRange(latitude, longitude))" in service,
        "IntentService must reject out-of-range coordinates before geocoding",
    )
    require(
        "GeocodeInputValidator.isCoordinateInRange(latitude, longitude)" in service,
        "IntentService must delegate coordinate validation to the tested validator",
    )
    require(
        service.index("if(!isCoordinateInRange(latitude, longitude))")
        < service.index("addresses = geocoder.getFromLocation(latitude, longitude, 1)"),
        "IntentService coordinate range guard must run before geocoder lookup",
    )
    require(
        "i <= address.getMaxAddressLineIndex()" in service,
        "IntentService must include the final address line in the delivered result",
    )
    log_calls = re.findall(r"\bLog\.[a-z]+\s*\(.*?\);", service, re.DOTALL)
    for log_call in log_calls:
        for sensitive_reference in (
            "latitude",
            "longitude",
            "getAddressLine",
            "outputAddress",
            "addressFragments",
            "addresses.",
            "address.toString",
        ):
            require(
                sensitive_reference not in log_call,
                "IntentService Logcat calls must not reference geocode data: "
                f"{sensitive_reference}",
            )
    for contract in (
        "Double.isFinite(latitude)",
        "Double.isFinite(longitude)",
        "latitude >= -90",
        "latitude <= 90",
        "longitude >= -180",
        "longitude <= 180",
    ):
        require(contract in validator, f"coordinate validator is missing {contract!r}")
    for test_name in (
        "normalizeAddressTrimsInput",
        "normalizeAddressHandlesMissingInput",
        "coordinatesIncludeGeographicBoundaries",
        "coordinatesRejectValuesOutsideGeographicBoundaries",
        "coordinatesRejectNonFiniteValues",
    ):
        require(test_name in validator_test, f"validator unit test is missing {test_name}")


def parse_version(version):
    return tuple(int(part) for part in version.split("."))


def sha256_hexdigest(content):
    logging_disable_level = logging.root.manager.disable
    logging.disable(logging.CRITICAL)
    try:
        import hashlib
    finally:
        logging.disable(logging_disable_level)
    return hashlib.sha256(content).hexdigest()


def check_kotlin_agp_compatibility(root_build, app_build):
    agp_match = ROOT_BUILD_PATTERN.fullmatch(root_build)
    kotlin_match = KOTLIN_BOM_PATTERN.search(app_build)
    require(agp_match is not None, "build.gradle must declare a literal AGP version")
    require(kotlin_match is not None, "app/build.gradle must declare a literal Kotlin BOM")

    agp_version = parse_version(agp_match.group("version"))
    kotlin_version = parse_version(kotlin_match.group("version"))
    kotlin_line = kotlin_version[:2]
    minimum_agp = KOTLIN_MINIMUM_AGP.get(kotlin_line)
    require(
        minimum_agp is not None,
        f"Kotlin {kotlin_line[0]}.{kotlin_line[1]} is not in the reviewed compatibility matrix",
    )
    require(
        agp_version >= minimum_agp,
        f"Kotlin {kotlin_line[0]}.{kotlin_line[1]} requires AGP "
        f"{minimum_agp[0]}.{minimum_agp[1]}.{minimum_agp[2]}",
    )


def check_modern_android_build_text(root_build, app_build, wrapper, makefile):
    require(
        ROOT_BUILD_PATTERN.fullmatch(root_build) is not None,
        "build.gradle must match the canonical literal AGP declaration",
    )
    check_kotlin_agp_compatibility(root_build, app_build)
    require(
        not app_build.endswith("\n\n"),
        "app/build.gradle must have at most one trailing newline",
    )
    app_build_content = app_build[:-1] if app_build.endswith("\n") else app_build
    normalized_app_build_lines = []
    dependencies = []
    for line in app_build_content.split("\n"):
        for dependency, pattern, placeholder in APP_DEPENDENCY_PATTERNS:
            if pattern.fullmatch(line) is None:
                continue
            dependencies.append(dependency)
            normalized_app_build_lines.append(placeholder)
            break
        else:
            normalized_app_build_lines.append(line)

    normalized_app_build = "\n".join(normalized_app_build_lines)
    require(
        dependencies
        == [
            "kotlin-bom",
            "appcompat",
            "lifecycle-livedata",
            "lifecycle-viewmodel",
            "core-testing",
            "junit",
        ]
        and normalized_app_build == CANONICAL_APP_BUILD,
        "app/build.gradle must match the canonical Android application build",
    )
    require(
        wrapper in (CANONICAL_GRADLE_WRAPPER, CANONICAL_GRADLE_WRAPPER.rstrip("\n")),
        "gradle-wrapper.properties must match the reviewed Gradle wrapper tuple",
    )
    require(
        makefile in (CANONICAL_MAKEFILE, CANONICAL_MAKEFILE + "\n"),
        "Makefile must match the canonical verification targets",
    )


def check_modern_android_build():
    root_build = read_text("build.gradle")
    app_build = read_text("app/build.gradle")
    wrapper = read_text("gradle/wrapper/gradle-wrapper.properties")
    check_modern_android_build_text(
        root_build,
        app_build,
        wrapper,
        read_text("Makefile"),
    )
    require(
        ROOT_BUILD_PATTERN.fullmatch(root_build).group("version") == EXPECTED_AGP_VERSION,
        f"build.gradle must pin reviewed AGP {EXPECTED_AGP_VERSION}",
    )
    require(
        KOTLIN_BOM_PATTERN.search(app_build).group("version") == EXPECTED_KOTLIN_BOM_VERSION,
        f"app/build.gradle must pin reviewed Kotlin BOM {EXPECTED_KOTLIN_BOM_VERSION}",
    )
    wrapper_jar_sha256 = sha256_hexdigest(
        (ROOT / "gradle" / "wrapper" / "gradle-wrapper.jar").read_bytes()
    )
    require(
        wrapper_jar_sha256 == GRADLE_WRAPPER_JAR_SHA256,
        "gradle-wrapper.jar must match the reviewed Gradle wrapper tuple",
    )
    require(
        read_text(".gitattributes") == CANONICAL_GITATTRIBUTES,
        ".gitattributes must match the canonical line-ending policy",
    )
    eol_result = subprocess.run(
        ["git", "ls-files", "--eol", "gradlew", "gradlew.bat"],
        cwd=ROOT,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    require(eol_result.returncode == 0, "git must report wrapper line-ending metadata")
    eol_lines = eol_result.stdout.splitlines()
    require(
        len(eol_lines) == 2
        and re.fullmatch(r"i/lf\s+w/lf\s+attr/text eol=lf\s+gradlew", eol_lines[0])
        and re.fullmatch(
            r"i/lf\s+w/crlf\s+attr/text eol=crlf\s+gradlew\.bat", eol_lines[1]
        ),
        "wrapper scripts must use LF index blobs with canonical Unix/Windows worktree endings",
    )
    require(
        "docs/plans/2026-06-14-make-root-override-protection.md"
        in read_text("README.md"),
        "README.md must index Make root override protection evidence",
    )


def check_dependabot_contracts_text(dependabot):
    require(
        dependabot in (CANONICAL_DEPENDABOT, CANONICAL_DEPENDABOT + "\n"),
        ".github/dependabot.yml must match the canonical grouped update policy",
    )


def check_dependabot_contracts():
    check_dependabot_contracts_text(read_text(".github/dependabot.yml"))


def main():
    checks = [
        check_docs_plans,
        check_xml_resources,
        check_manifest_contracts,
        check_gradle_application_id,
        check_hosted_verification,
        check_coordinate_input_guard,
        check_modern_android_build,
        check_dependabot_contracts,
    ]
    try:
        for check in checks:
            check()
    except AssertionError as exc:
        return fail(str(exc))

    print(f"Static Android contracts passed ({len(checks)} checks).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

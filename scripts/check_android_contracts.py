#!/usr/bin/env python3
"""Static verification for the legacy Android geocode sample."""

from pathlib import Path
import re
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
ACTION_LINE_PATTERN = re.compile(
    r"^        uses: "
    r"(?P<action>actions/(?:checkout|setup-python|setup-java))"
    r"@[0-9a-f]{40} # v\d+\.\d+\.\d+$"
)
ROOT_BUILD_PATTERN = re.compile(
    r'plugins \{\n'
    r'    id "com\.android\.application" version "\d+\.\d+\.\d+" apply false\n'
    r'\}\n?'
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

    testImplementation 'junit:junit:<VERSION>'
}"""
GRADLE_WRAPPER_PATTERN = re.compile(
    r"distributionBase=GRADLE_USER_HOME\n"
    r"distributionPath=wrapper/dists\n"
    r"distributionSha256Sum=[0-9a-fA-F]{64}\n"
    r"distributionUrl=https\\://services\.gradle\.org/distributions/"
    r"gradle-\d+\.\d+(?:\.\d+)?-bin\.zip\n"
    r"networkTimeout=10000\n"
    r"validateDistributionUrl=true\n"
    r"zipStoreBase=GRADLE_USER_HOME\n"
    r"zipStorePath=wrapper/dists\n?"
)
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
      - name: Set up Java
        uses: actions/setup-java@<SHA> # v<VERSION>
        with:
          distribution: temurin
          java-version: "17"
          cache: gradle
      - name: Install Android SDK packages
        run: $ANDROID_HOME/cmdline-tools/latest/bin/sdkmanager "platforms;android-36" "build-tools;35.0.0"
      - name: Run Android verification
        run: make check"""
CANONICAL_MAKEFILE = """.PHONY: build check lint static test verify

ROOT := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))
PYTHON ?= python3
GRADLEW ?= $(ROOT)/gradlew

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
	cd "$(ROOT)" && "$(GRADLEW)" --no-daemon testDebugUnitTest assembleDebug lintDebug

check: verify"""
CANONICAL_DEPENDABOT = """version: 2
updates:
  - package-ecosystem: gradle
    directory: /
    schedule:
      interval: weekly
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

    plans = sorted(DOCS_PLANS.glob("*.md")) if DOCS_PLANS.exists() else []
    require(plans, "docs/plans must contain at least one completed plan")

    for plan_path in plans:
        plan = plan_path.read_text(encoding="utf-8")
        require(
            "Status: Completed" in plan and "make check" in plan,
            f"{plan_path.relative_to(ROOT)} must record completed status and make check verification",
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
    check_hosted_verification_text(read_text(".github/workflows/check.yml"))


def check_coordinate_input_guard():
    main_activity = read_text("app/src/main/java/com/sample/foo/tsgeocodeapp/MainActivity.java")
    service = read_text("app/src/main/java/com/sample/foo/tsgeocodeapp/GeocodeAddressIntentService.java")
    validator = read_text("app/src/main/java/com/sample/foo/tsgeocodeapp/GeocodeInputValidator.java")
    validator_test = read_text("app/src/test/java/com/sample/foo/tsgeocodeapp/GeocodeInputValidatorTest.java")
    strings = read_text("app/src/main/res/values/strings.xml")

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
        '<string name="invalid_latitude_longitude">' in strings,
        "strings.xml must define invalid_latitude_longitude",
    )
    for fragment in (
        "import android.text.TextUtils;",
        'private static final String NO_GEOCODE_RESULT = "No geocode result";',
        "if (resultData == null)",
        "final String resultMessage = resultData.getString(Constants.RESULT_DATA_KEY);",
        "address == null || TextUtils.isEmpty(resultMessage)",
        "showResultText(NO_GEOCODE_RESULT)",
        "private void showResultText(final String message)",
    ):
        require(fragment in main_activity, f"MainActivity result receiver guard is missing: {fragment}")
    require(
        "infoText.setText(resultData.getString(Constants.RESULT_DATA_KEY))" not in main_activity,
        "MainActivity must not render raw ResultReceiver bundle strings directly",
    )
    for fragment in (
        "import java.lang.ref.WeakReference;",
        "import android.os.Looper;",
        "mResultReceiver = new AddressResultReceiver(this);",
        "private static final class AddressResultReceiver extends ResultReceiver",
        "private final WeakReference<MainActivity> activityReference;",
        "super(new Handler(Looper.getMainLooper()));",
        "activityReference = new WeakReference<>(activity);",
        "MainActivity activity = activityReference.get();",
        "activity == null || activity.isFinishing() || activity.isDestroyed()",
        "activity.handleGeocodeResult(resultCode, resultData);",
        "private void handleGeocodeResult(int resultCode, Bundle resultData)",
    ):
        require(fragment in main_activity, f"MainActivity lifecycle-safe receiver is missing: {fragment}")
    require(
        "mResultReceiver = new AddressResultReceiver(null);" not in main_activity,
        "MainActivity must bind the receiver through a weak activity reference",
    )
    require(
        "runOnUiThread" not in main_activity,
        "ResultReceiver must dispatch directly through its main-looper Handler",
    )

    require(
        "name = GeocodeInputValidator.normalizeAddress(name);" in service,
        "IntentService must normalize address-name extras before geocoding",
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
        service.count("i <= address.getMaxAddressLineIndex()") >= 2,
        "IntentService must include the final address line in all result loops",
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


def check_modern_android_build_text(root_build, app_build, wrapper, makefile):
    require(
        ROOT_BUILD_PATTERN.fullmatch(root_build) is not None,
        "build.gradle must match the canonical literal AGP declaration",
    )
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
        dependencies == ["kotlin-bom", "appcompat", "junit"]
        and normalized_app_build == CANONICAL_APP_BUILD,
        "app/build.gradle must match the canonical Android application build",
    )
    require(
        GRADLE_WRAPPER_PATTERN.fullmatch(wrapper) is not None,
        "gradle-wrapper.properties must match the canonical pinned wrapper template",
    )
    require(
        makefile in (CANONICAL_MAKEFILE, CANONICAL_MAKEFILE + "\n"),
        "Makefile must match the canonical verification targets",
    )


def check_modern_android_build():
    check_modern_android_build_text(
        read_text("build.gradle"),
        read_text("app/build.gradle"),
        read_text("gradle/wrapper/gradle-wrapper.properties"),
        read_text("Makefile"),
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

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


def check_hosted_verification():
    workflow = read_text(".github/workflows/check.yml")
    required_contracts = [
        "pull_request:",
        "workflow_dispatch:",
        "branches:\n      - master",
        "permissions:\n  contents: read",
        "cancel-in-progress: true",
        "timeout-minutes: 5",
        "timeout-minutes: 15",
        'python-version: ["3.10", "3.12"]',
        "actions/checkout@df4cb1c069e1874edd31b4311f1884172cec0e10",
        "actions/setup-python@a309ff8b426b58ec0e2a45f0f869d46889d02405",
        "actions/setup-java@be666c2fcd27ec809703dec50e508c2fdc7f6654",
        "java-version: \"17\"",
        "run: make static",
        '$ANDROID_HOME/cmdline-tools/latest/bin/sdkmanager "platforms;android-36" "build-tools;35.0.0"',
        "run: make check",
    ]
    for contract in required_contracts:
        require(contract in workflow, f"hosted verification must include {contract!r}")
    require("@v" not in workflow, "hosted verification actions must use immutable SHAs")


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

    match = re.search(
        r"public void onButtonClicked\(View view\) \{(?P<body>.*?)\n    \}",
        main_activity,
        re.DOTALL,
    )
    require(match is not None, "MainActivity.onButtonClicked must be present")
    body = match.group("body")

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


def check_modern_android_build():
    root_build = read_text("build.gradle")
    app_build = read_text("app/build.gradle")
    wrapper = read_text("gradle/wrapper/gradle-wrapper.properties")
    require('version "8.10.1"' in root_build, "Android Gradle Plugin must remain pinned")
    require("compileSdk = 36" in app_build, "compileSdk must remain on API 36")
    require("targetSdk = 36" in app_build, "targetSdk must remain on API 36")
    require("minSdk = 21" in app_build, "minSdk must match AndroidX AppCompat support")
    require("warningsAsErrors = true" in app_build, "Android lint warnings must fail verification")
    require(
        "gradle-8.14.5-bin.zip" in wrapper,
        "Gradle wrapper distribution must remain pinned to 8.14.5",
    )
    require(
        "distributionSha256Sum=6f74b601422d6d6fc4e1f9a1ab6522f642c2fdcbc15ae33ebd30ba3d7198e854"
        in wrapper,
        "Gradle wrapper distribution checksum must remain pinned",
    )


def main():
    checks = [
        check_docs_plans,
        check_xml_resources,
        check_manifest_contracts,
        check_gradle_application_id,
        check_hosted_verification,
        check_coordinate_input_guard,
        check_modern_android_build,
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

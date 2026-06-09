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
    ]:
        parse_xml(relative_path)


def check_manifest_contracts():
    manifest = parse_xml("app/src/main/AndroidManifest.xml").getroot()
    package_name = manifest.attrib["package"]
    require(package_name == "com.sample.foo.tsgeocodeapp", "manifest package changed unexpectedly")

    application = manifest.find("application")
    require(application is not None, "manifest must declare an application")
    require(
        application.attrib.get(f"{{{ANDROID_NS}}}allowBackup") == "false",
        "manifest application must explicitly disable app-data backup",
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
    match = re.search(r'applicationId\s+"([^"]+)"', build_gradle)
    require(match is not None, "app/build.gradle must declare an applicationId")
    require(
        match.group(1) == "com.sample.foo.tsgeocodeapp",
        "Gradle applicationId must match the manifest and Java package",
    )


def check_coordinate_input_guard():
    main_activity = read_text("app/src/main/java/com/sample/foo/tsgeocodeapp/MainActivity.java")
    async_activity = read_text("app/src/main/java/com/sample/foo/tsgeocodeapp/MainActivityWithAsyncTask.java")
    service = read_text("app/src/main/java/com/sample/foo/tsgeocodeapp/GeocodeAddressIntentService.java")
    strings = read_text("app/src/main/res/values/strings.xml")

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
        "String addressName = addressEdit.getText().toString().trim();" in body,
        "MainActivity must trim address-name input before validation",
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
        "latitude >= -90 && latitude <= 90" in main_activity
        and "longitude >= -180 && longitude <= 180" in main_activity,
        "MainActivity must define latitude/longitude range limits",
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
        "import android.widget.Toast;" in async_activity,
        "async activity must import Toast for validation feedback",
    )
    require(
        "catch (NumberFormatException" in async_activity,
        "async activity must guard invalid numeric coordinates before starting AsyncTask",
    )
    require(
        "R.string.invalid_latitude_longitude" in async_activity,
        "async activity invalid coordinate feedback must use the shared string resource",
    )
    require(
        "if(!isCoordinateInRange(latitude, longitude))" in async_activity,
        "async activity must reject out-of-range coordinates before starting AsyncTask",
    )
    require(
        "latitude >= -90 && latitude <= 90" in async_activity
        and "longitude >= -180 && longitude <= 180" in async_activity,
        "async activity must define latitude/longitude range limits",
    )
    require(
        "new GeocodeAsyncTask(fetchType" in async_activity,
        "async activity must pass validated request values into GeocodeAsyncTask",
    )
    require(
        async_activity.index("if(!isCoordinateInRange(latitude, longitude))")
        < async_activity.index("new GeocodeAsyncTask(fetchType, null, latitude, longitude)"),
        "async coordinate range guard must run before starting AsyncTask",
    )
    require(
        "GeocodeAsyncTask(int taskFetchType, String addressName, double latitude, double longitude)" in async_activity,
        "GeocodeAsyncTask must capture validated request values",
    )
    require(
        "Double.parseDouble(latitudeEdit.getText().toString())" not in async_activity.split("protected Address doInBackground", 1)[-1],
        "GeocodeAsyncTask must not parse latitude from UI text in doInBackground",
    )
    require(
        "Double.parseDouble(longitudeEdit.getText().toString())" not in async_activity.split("protected Address doInBackground", 1)[-1],
        "GeocodeAsyncTask must not parse longitude from UI text in doInBackground",
    )
    require(
        "i <= address.getMaxAddressLineIndex()" in async_activity,
        "async activity must include the final address line when rendering results",
    )
    require(
        'name = name == null ? "" : name.trim();' in service,
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
        "latitude >= -90 && latitude <= 90" in service
        and "longitude >= -180 && longitude <= 180" in service,
        "IntentService must define latitude/longitude range limits",
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


def main():
    checks = [
        check_docs_plans,
        check_xml_resources,
        check_manifest_contracts,
        check_gradle_application_id,
        check_coordinate_input_guard,
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

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
        "catch (NumberFormatException" in body,
        "invalid numeric coordinates must not crash MainActivity",
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
        '<string name="invalid_latitude_longitude">' in strings,
        "strings.xml must define invalid_latitude_longitude",
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

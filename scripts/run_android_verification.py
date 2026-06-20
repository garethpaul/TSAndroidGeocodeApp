#!/usr/bin/env python3
"""Run Android verification and fail closed on Kotlin metadata incompatibility."""

from pathlib import Path
import re
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_KOTLIN_STDLIB = "org.jetbrains.kotlin:kotlin-stdlib:2.2.21"
KOTLIN_STDLIB_PATTERN = re.compile(
    r"(?m)^org\.jetbrains\.kotlin:kotlin-stdlib:"
    r"(?P<requested>\d+\.\d+\.\d+)"
    r"(?:\s+->\s+(?P<selected>\d+\.\d+\.\d+))?"
)
FORBIDDEN_OUTPUT = (
    "an error occurred when parsing kotlin metadata",
    "unexpected error during rewriting of kotlin metadata",
    "module was compiled with an incompatible version of kotlin",
)


def run(command):
    result = subprocess.run(
        command,
        cwd=ROOT,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    print(result.stdout, end="")
    if result.returncode != 0:
        return result.returncode, result.stdout

    normalized_output = result.stdout.lower()
    for marker in FORBIDDEN_OUTPUT:
        if marker in normalized_output:
            print(
                "run_android_verification.py: Kotlin metadata incompatibility "
                f"marker found: {marker}",
                file=sys.stderr,
            )
            return 1, result.stdout
    return 0, result.stdout


def main(argv=None):
    arguments = sys.argv[1:] if argv is None else argv
    if len(arguments) != 1:
        print("usage: run_android_verification.py GRADLEW", file=sys.stderr)
        return 2

    gradlew = arguments[0]
    dependency_status, dependency_output = run(
        [
            gradlew,
            "--no-daemon",
            ":app:dependencyInsight",
            "--dependency",
            "org.jetbrains.kotlin:kotlin-stdlib",
            "--configuration",
            "debugRuntimeClasspath",
        ]
    )
    if dependency_status != 0:
        return dependency_status
    resolved_versions = {
        match.group("selected") or match.group("requested")
        for match in KOTLIN_STDLIB_PATTERN.finditer(dependency_output)
    }
    if resolved_versions != {"2.2.21"}:
        print(
            "run_android_verification.py: dependencyInsight resolved unexpected Kotlin "
            f"stdlib versions: {sorted(resolved_versions)!r}; expected {EXPECTED_KOTLIN_STDLIB}",
            file=sys.stderr,
        )
        return 1

    verification_status, _ = run(
        [
            gradlew,
            "--no-daemon",
            "testDebugUnitTest",
            "assembleDebug",
            "lintDebug",
        ]
    )
    return verification_status


if __name__ == "__main__":
    raise SystemExit(main())

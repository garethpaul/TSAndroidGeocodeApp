.PHONY: build check lint static test verify

PYTHON ?= python3
GRADLEW ?= ./gradlew

static:
	$(PYTHON) scripts/check_android_contracts.py

test:
	$(GRADLEW) --no-daemon testDebugUnitTest

build:
	$(GRADLEW) --no-daemon assembleDebug

lint: static
	$(GRADLEW) --no-daemon lintDebug

verify: static
	$(GRADLEW) --no-daemon testDebugUnitTest assembleDebug lintDebug

check: verify

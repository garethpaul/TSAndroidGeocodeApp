.PHONY: build check lint static test verify

ROOT := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))
PYTHON ?= python3
GRADLEW ?= $(ROOT)/gradlew

static:
	$(PYTHON) "$(ROOT)/scripts/check_android_contracts.py"

test:
	cd "$(ROOT)" && "$(GRADLEW)" --no-daemon testDebugUnitTest

build:
	cd "$(ROOT)" && "$(GRADLEW)" --no-daemon assembleDebug

lint: static
	cd "$(ROOT)" && "$(GRADLEW)" --no-daemon lintDebug

verify: static
	cd "$(ROOT)" && "$(GRADLEW)" --no-daemon testDebugUnitTest assembleDebug lintDebug

check: verify

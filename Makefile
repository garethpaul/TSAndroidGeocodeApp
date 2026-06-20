.PHONY: build check checkout-integrity lint static test verify

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

check: verify

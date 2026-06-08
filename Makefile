.PHONY: lint test build verify

PYTHON ?= python3

lint:
	$(PYTHON) scripts/check_android_contracts.py

test: lint

build:
	@if [ -x ./gradlew ]; then \
		./gradlew assembleDebug; \
	elif [ -f settings.gradle ] && command -v gradle >/dev/null 2>&1; then \
		gradle assembleDebug; \
	else \
		echo "Android build skipped: no Gradle wrapper or root settings.gradle is checked in."; \
	fi

verify: lint test build

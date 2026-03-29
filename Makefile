UV ?= uv
RUN = $(UV) run

.PHONY: sync sync-dev canonical transfer verify export-hf-space export-hf-dataset release preflight test

sync:
	$(UV) sync --frozen

sync-dev:
	$(UV) sync --frozen --extra dev

canonical:
	$(RUN) spectralbio canonical

transfer:
	$(RUN) spectralbio transfer

verify:
	$(RUN) spectralbio verify

export-hf-space:
	$(RUN) spectralbio export-hf-space

export-hf-dataset:
	$(RUN) spectralbio export-hf-dataset

release:
	$(RUN) spectralbio release

preflight:
	$(RUN) python scripts/preflight.py

test:
	$(RUN) pytest

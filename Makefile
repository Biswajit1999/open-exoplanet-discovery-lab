.PHONY: test validate nets census web

test:
	python -m pytest -q

validate:
	python scripts/run_synthetic_validation.py

nets:
	python scripts/build_nets_manifest.py
	python scripts/run_nets_report.py

census:
	python scripts/build_eso_overlap_census.py

web:
	cd web && npm install && npm run build

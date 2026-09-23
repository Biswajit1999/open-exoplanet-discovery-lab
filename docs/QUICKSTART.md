# Quickstart

## Install

    git clone https://github.com/Biswajit1999/open-exoplanet-discovery-lab.git
    cd open-exoplanet-discovery-lab
    python -m venv .venv
    source .venv/bin/activate
    python -m pip install --upgrade pip
    pip install -e .[test]

On Windows PowerShell, activate with:

    .venv\Scripts\Activate.ps1

## Validate the code

    pytest -q
    python scripts/run_synthetic_validation.py

## Inspect source states

    exolab sources

A source with state WAIT or FUTURE is deliberately blocked from normal present-data use.

## Acquire NETS III

    python scripts/build_nets_manifest.py

This downloads the public VizieR catalogue tables for J/AJ/170/264 and creates a checksum-bearing manifest.

Then:

    python scripts/run_nets_report.py

The report is descriptive and diagnostic. A GLS peak is not labelled as a planet.

## Build NIRPS/HARPS overlap census

    python scripts/build_eso_overlap_census.py

The script queries the public ESO ObsCore service, deduplicates product-level rows into target/epoch records, performs a coordinate-based target crossmatch and reports overlap counts at ±1 h, ±6 h, ±1 d, ±3 d and ±7 d.

This is an archive census, not yet a precision-RV science sample. Product-level reduction provenance must pass the NIRPS/HARPS QC contract before inference.

## Run the web interface

    cd web
    npm install
    npm run dev

The website is a research interface. Publication calculations remain in Python.

## Where to read next

- research/STATISTICAL_ANALYSIS_PLAN.md
- research/INSTRUMENT_SYSTEMATICS.md
- research/QUALITY_CONTROL.md
- research/LITERATURE_NOVELTY.md
- docs/REPRODUCIBILITY.md
- docs/DATA_DICTIONARY.md

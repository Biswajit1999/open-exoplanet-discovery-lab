# Reproducibility Guide

## Principle

A figure is not reproducible merely because its plotting code is public. Reproduction requires the identity of the source observations, their reduction provenance, the analysis configuration and the software revision.

## Recommended release sequence

1. Clone the repository at a tagged release.
2. Create an isolated Python environment.
3. Install the package and test extras.
4. Validate the source registry.
5. Acquire public archive products using the scripted client.
6. Write a manifest immediately after acquisition.
7. Verify checksums before analysis.
8. Run deterministic preprocessing.
9. Run diagnostics and validation.
10. Generate tables before figures.
11. Generate static paper figures from those tables.
12. Store the software commit and manifest hash in each generated product.

## Initial commands

    python -m venv .venv
    source .venv/bin/activate
    python -m pip install --upgrade pip
    pip install -e .[test]
    pytest -q
    python scripts/run_synthetic_validation.py

NETS III acquisition:

    python scripts/build_nets_manifest.py
    python scripts/run_nets_report.py

ESO overlap census:

    python scripts/build_eso_overlap_census.py

## Data directories

data/raw/
Archive products acquired locally. Not committed by default.

data/census/
Compact archive-census tables.

data/manifests/
Immutable JSON provenance records.

outputs/
Derived results that can be regenerated from a manifest and configuration.

## Integrity

The provenance module records SHA-256 hashes for local inputs. verify_manifest fails if either the metadata or a local file has changed.

## Network failures

Archive acquisition is intentionally separate from numerical tests. Unit tests must pass without network access. A failed archive request must not be replaced with embedded fake data.

## Randomness

Stochastic analyses use explicit seeds. A scientific release stores the seed, grid/prior definition and the number of simulations.

## Notebooks

Notebooks may explain or explore results, but production calculations belong in importable package functions and scripts. A notebook must not contain the only implementation of a headline result.

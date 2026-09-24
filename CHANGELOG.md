# Changelog

## 0.3.1 — 2026-09-24

Added:
- exact SIMBAD-to-Gaia DR3 identity resolution for all 41 NETS III survey stars;
- a frozen Gaia DR3 identity and astrometric-context table with ADQL, input/query hashes and checksums;
- Gaia identity, parallax, photometric context and explicitly non-diagnostic RUWE display in the Target Atlas;
- strict completeness checks for ambiguous, missing or duplicate identity responses.

Gaia DR4 remains gated, and no Gaia astrometric field is interpreted as a companion detection.

## 0.3.0 — 2026-09-23

Added the frozen NETS III completeness, ESO NIRPS × HARPS census, TESS temporal-context and 55 Cnc e reproducibility results; the scientist-facing Target Atlas, Completeness Lab, provenance inspector and paper mode; and the first citable A-to-Z public research release.

## 0.2.0 — 2026-09-23

The repository was expanded from a TESS-first transit laboratory into the Open Exoplanet Evidence Lab.

Added:
- provenance manifests and SHA-256 integrity verification;
- versioned public-source registry and access-state gates;
- weighted EPRV fitting primitives with instrument offsets;
- GLS and cadence/window diagnostics;
- optical/NIR RV coherence and epoch-simultaneity tools;
- circular RV injection/recovery and completeness aggregation;
- repeated-atmosphere random-effects reproducibility statistics;
- VizieR and ESO TAP acquisition clients;
- live NETS III acquisition and descriptive-report scripts;
- public NIRPS/HARPS ObsCore overlap-census pipeline;
- statistical analysis plan, QC contract, systematics register and novelty gate;
- JSON data/result schemas;
- deterministic science-validation workflow;
- scientist-facing React/TypeScript/Motion web interface and web CI.

Scientific scope is intentionally conservative: periodogram peaks are not planet detections, cross-wavelength agreement is not automatic confirmation, and future/unreleased archive products are not treated as current inputs.

## 0.1.0 — 2026-08-16

Initial public TESS transit-search and candidate-vetting laboratory.

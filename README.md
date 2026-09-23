# Open Exoplanet Evidence Lab

**A provenance-first 2026 research programme for extreme-precision radial velocity, stellar activity, transit context, atmospheric reproducibility, and future astrometric cross-validation.**

Developed by **Biswajit Jana**.

> This repository is being rebuilt as a scientist-facing research platform. The objective is not to maximise the number of plots or candidate labels. The objective is to quantify how strongly exoplanet conclusions depend on instrumental systematics, stellar variability, cadence, wavelength, reduction provenance, and cross-archive evidence.

## Central scientific question

**How stable are exoplanet inferences and survey-completeness claims when instrumental zero points, stellar activity, chromatic RV behaviour, temporal sampling, and independent observing modalities are modelled explicitly rather than treated as secondary corrections?**

The project separates three things that are often mixed together:

1. **measurement** — what an archive actually reports;
2. **inference** — what model converts those measurements into a planet or non-detection statement;
3. **robustness** — whether that statement survives alternative but defensible assumptions.

A positive result may be a more reliable planet constraint. A scientifically useful null result may be evidence that a simpler published method is already robust.

## Programme architecture

This is one repository with multiple scientifically isolated work packages that share acquisition, provenance, statistics, validation, and reporting infrastructure.

### WP0 — Archive registry and provenance
Create frozen machine-readable manifests for every dataset, recording query, access date, archive identifier, DOI, pipeline/reduction version, file checksum, time system, units, quality flags, and selection rules.

### WP1 — NETS III: EPRV completeness under realistic noise models
Use the public **NEID Earth Twin Survey III** RV and activity time series to measure how planet-detection completeness changes when zero-point epochs, activity correlations, temporal covariance, and held-out instrumental eras are included.

Primary output: baseline completeness C(P,K) versus instrument/activity-aware completeness C*(P,K), reported as Delta C(P,K), K50(P), and K90(P).

### WP2 — NIRPS × HARPS: optical/NIR coherence
Build a verified overlap sample and test whether RV signals remain coherent in period, phase, and semi-amplitude between optical HARPS and near-infrared NIRPS measurements.

This work package is explicitly sensitive to pipeline provenance. NIRPS products reduced with DRS 3.2.6 between 2025-04-01 and 2025-07-24 must not be used for sub-10 m/s science; corrected Phase-3 products were reprocessed with DRS 3.2.7.

### WP3 — SPORES-HWO II: long-baseline RV robustness
When the consolidated public tables are accessible, reproduce selected published companion-sensitivity maps and test their robustness to eccentric injections, correlated stellar noise, and leave-one-instrument-out experiments.

This is **not** a second generic planet search.

### WP4 — TESS: photometric context and temporal validation
Use recent TESS releases for stellar rotation/activity context, transit ephemerides, and out-of-sample temporal validation. Sector 106 can serve as a mature control for Sector 107 while weekly FFI ingestion is still evolving.

### WP5 — Atmospheric reproducibility
Treat JWST/HST **Rocky Worlds** products and the NASA Exoplanet Archive atmospheric-spectroscopy collection as independent evidence streams. The scientific question is reproducibility: how much additional inter-visit, inter-reduction, or inter-instrument variance is required for published spectra/eclipses to be mutually consistent?

This work package is statistically separate from the RV likelihood unless a target-specific physical model explicitly justifies a joint analysis.

### WP6 — Gaia astrometry interface
Use Gaia DR3/current products where appropriate and design a versioned adapter for Gaia DR4 **only after DR4 is public and its final schema is verified**. Future astrometry can convert RV minimum masses into stronger orbit/mass constraints, but no present result will depend on unreleased DR4 data.

## Why these pieces belong in one project

The common object is not a particular telescope. It is the **credibility of an exoplanet inference**.

    archive products
        ↓
    identity + provenance
        ↓
    quality control
        ↓
    instrument / stellar nuisance model
        ↓
    signal search or known-signal fit
        ↓
    null tests + injection/recovery
        ↓
    cross-wavelength / cross-epoch / cross-archive checks
        ↓
    robustness statement
        ↓
    reproducible figure, table, and machine-readable result

The repository must never combine heterogeneous measurements merely because they are available. Every cross-archive join needs a stated physical reason.

## Scientific guardrails

- A periodic signal is not automatically a planet.
- Improved residual RMS is not automatically improved inference.
- A Gaussian process is not automatically a better activity model.
- A near-infrared activity amplitude is not assumed to be smaller than its optical counterpart.
- A non-detection is interpreted only after completeness is measured.
- A candidate is not described as confirmed without appropriate independent evidence.
- Archive display values are not substituted for publication-native quantities when the archive warns against that use.
- Pipeline versions, instrument upgrades, time systems, and zero points are part of the model, not footnotes.
- No result is labelled novel until its exact question has passed a literature audit.
- No fabricated or demonstration data may appear in a science-results directory.

## Current public-data anchors

| Stream | Current role | Access state |
|---|---|---|
| NEID Earth Twin Survey III | Core EPRV benchmark | public |
| ESO NIRPS Phase-3 stream | NIR RV / chromaticity | public, dynamic |
| HARPS archive | optical RV comparison | public products available by target |
| SPORES-HWO II | long-baseline robustness | VizieR tables scheduled after 2026-10-04; verify alternate official deposit before use |
| TESS S106/S107 | photometric/activity context | S107 ingestion still evolving on 2026-09-23 |
| Rocky Worlds HLSP | repeated rocky-planet eclipse + UV context | public, actively updated |
| NASA Exoplanet Archive atmospheric spectra | cross-study reproducibility | public |
| Gaia DR3 | current astrometric context | public |
| Gaia DR4 | future extension only | not treated as public until verified |

See [research/DATA_RELEASE_REGISTRY.md](research/DATA_RELEASE_REGISTRY.md) for versioned source notes and access gates.

## Repository map

    open-exoplanet-discovery-lab/
    ├── configs/                    archive/source contracts and analysis configs
    ├── data/                       local data only; raw archive payloads not committed by default
    ├── docs/                       architecture, web interface, reproducibility docs
    ├── notebooks/                  exploration only; canonical science lives in src/
    ├── outputs/                    generated tables/figures, reproducible from manifests
    ├── research/                   hypotheses, literature gates, statistical analysis plans
    ├── src/exolab/                 reusable Python science package
    ├── tests/                      scientific invariants + software tests
    └── web/                        scientist-facing React/TypeScript interface, added in staged build

Notebooks are for explanation and exploratory checks; they are not the source of truth.

## A-to-Z build reference

The complete project lifecycle is maintained in [research/A_TO_Z_BLUEPRINT.md](research/A_TO_Z_BLUEPRINT.md).

The first milestones are:

- **M0 — frozen archive census and manifests**
- **M1 — acquisition/provenance layer**
- **M2 — EPRV and activity diagnostics**
- **M3 — joint / chromatic modelling**
- **M4 — injection–recovery and null tests**
- **M5 — population and cross-archive analysis**
- **M6 — paper-quality reproducibility release + research interface**

No later milestone is allowed to silently change the M0 inclusion rules. Any change requires a new manifest version.

## Web research interface

The website is a **research interface**, not a dashboard substitute for the science pipeline.

It will use a custom React/TypeScript implementation with Motion for restrained transitions and interaction. Motion, Framer, 21st.dev, and the UI/UX Pro Max skill are design references only; components and layouts will not be copied wholesale.

The interface must expose target-level evidence pages, provenance drawers, RV/activity/window-function/periodogram/posterior views, completeness maps, optical/NIR coherence comparisons, transit/rotation context, atmospheric repeatability panels, uncertainty and null-test status by default, primary-source links, reduced-motion support, and a paper mode with static citable figures.

See [docs/WEB_RESEARCH_INTERFACE.md](docs/WEB_RESEARCH_INTERFACE.md).

## Reproducibility target

The intended end state is a cloneable environment in which a frozen manifest drives scripted archive acquisition, checksum verification, deterministic preprocessing, analysis, validation/null tests, and regeneration of figures, tables, and machine-readable results.

Large third-party archive data should normally be downloaded from the authoritative source rather than mirrored in Git.

## Reference sources

- NEID / NETS III paper: https://arxiv.org/abs/2506.23704
- ESO NIRPS Phase-3 DOI: https://doi.org/10.18727/archive/92
- ESO NIRPS DRS issue notice: https://archive.eso.org/cms/eso-archive-news/issue-on-reduced-nirps-data.html
- Rocky Worlds HLSP: https://archive.stsci.edu/hlsp/rocky-worlds
- NASA Exoplanet Archive: https://exoplanetarchive.ipac.caltech.edu/
- TESS archive holdings: https://outerspace.stsci.edu/spaces/TESS/pages/35094700/TESS%2BHoldings%2BAvailable%2Bby%2BMAST%2BService
- Gaia: https://www.cosmos.esa.int/web/gaia/

## Authorship

**Biswajit Jana**  
Independent/open-science research project.

Cite the original archives, data releases, software, and scientific papers associated with every result in addition to this repository.

## License

Software in this repository is MIT-licensed unless a file states otherwise. External archive data retain their original licences, access policies, acknowledgements, and citation requirements.

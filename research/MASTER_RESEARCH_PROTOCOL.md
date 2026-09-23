# Master Research Protocol

## 1. Purpose

This document defines the scientific contract for the 2026 Open Exoplanet Evidence Lab. It is intentionally stricter than a normal project roadmap because the repository is expected to be read by astronomers and instrument scientists.

The project is an umbrella research programme with one shared infrastructure layer and several scientifically distinct work packages. Shared code is encouraged; shared conclusions are not. A result from one work package may inform another only when the physical connection and statistical dependency are explicitly defined.

## 2. Primary research question

How stable are exoplanet inferences and survey-completeness statements when instrumental zero points, stellar activity, chromatic RV behaviour, temporal sampling, reduction provenance, and independent observing modalities are modelled explicitly?

This question is operationalised through five measurable robustness axes:

1. instrument-era robustness;
2. stellar-activity robustness;
3. wavelength robustness;
4. temporal robustness;
5. cross-archive robustness.

## 3. Core hypotheses

### H1 — EPRV completeness is model dependent
For at least a subset of stars, the inferred recovery probability C(P,K) changes materially when instrumental zero-point epochs and stellar correlated noise are included.

### H2 — Keplerian signals are more wavelength-coherent than many activity signals
For suitable HARPS/NIRPS overlap targets, a planetary reflex signal should remain consistent in period and phase and should not require arbitrary wavelength-dependent semi-amplitudes after accounting for instrument offsets and uncertainties.

This is a probabilistic expectation, not an absolute rule. Activity may remain coherent across wavelength and Zeeman effects can increase near-infrared RV variability.

### H3 — published sensitivity limits can depend on orbital and noise assumptions
Long-baseline RV completeness maps may shift when circular injections are replaced by an astrophysically justified eccentricity distribution, when correlated noise is included, or when one dominant instrument is withheld.

### H4 — repeated atmospheric measurements contain an empirical reproducibility scale
For planets with multiple visits, reductions, or instruments, reported pointwise uncertainties may not fully account for between-visit or between-reduction variance. The project will estimate this extra variance rather than assuming it is zero.

### H5 — useful null results exist
If more complex modelling leaves published conclusions essentially unchanged, that is a positive robustness result and must be reported as such.

## 4. Work packages

### WP0 — Identity, archive registry, and provenance

Deliverables:
- canonical target identifiers;
- archive query definitions;
- access date and source URL;
- product identifiers;
- instrument and mode;
- pipeline/reduction version;
- time standard and velocity convention;
- units;
- checksums;
- quality flags;
- inclusion/exclusion reason;
- literature references;
- immutable release manifests.

A target may not enter downstream analysis without a manifest record.

### WP1 — NETS III EPRV completeness

Dataset:
NEID Earth Twin Survey III, 41 stars with published RV and activity time series.

Primary comparison:
- baseline white-jitter / published-style recovery assumptions;
- era-aware offsets and jitters;
- activity-conditioned models;
- correlated-noise models only when diagnostics justify them.

Required outputs:
- per-star window functions;
- RV and activity periodograms;
- instrument-era step diagnostics;
- known-signal recovery checks;
- injection/recovery maps;
- K50(P) and K90(P);
- Delta C(P,K) between model families;
- held-out-era validation.

Do not claim a new planet from this work package unless an independent discovery/validation process is completed.

### WP2 — NIRPS × HARPS optical/NIR coherence

Scope gate:
This work package proceeds only after a frozen overlap census verifies enough targets and usable epochs.

Required target metadata:
- canonical identifier;
- Gaia DR3 source_id;
- spectral type;
- N_HARPS;
- N_NIRPS;
- time baselines;
- near-simultaneous pairs under fixed windows;
- pipeline versions;
- activity indicators;
- known planets;
- literature saturation class.

Instrument rule:
NIRPS observations reduced with DRS 3.2.6 from 2025-04-01 12:00 to 2025-07-24 12:00 are excluded for precision RV work unless corrected products reprocessed with DRS 3.2.7 are used.

Primary measurements:
- period agreement;
- phase agreement;
- semi-amplitude ratio;
- instrument-specific jitter;
- activity-proxy coherence;
- season-to-season stability.

Model comparison:
- achromatic Keplerian model;
- chromatic/activity model;
- instrument-specific nuisance terms.

### WP3 — SPORES-HWO II long-baseline robustness

Access gate:
Do not ingest VizieR tables before they are actually public. As of 2026-09-23, the catalogue page lists access after 2026-10-04. An alternate official deposit may be used only after its identity and content are verified.

Primary experiment:
Reproduce a selected published completeness result, then perturb the assumptions one at a time:
- eccentric injections;
- correlated activity;
- leave-one-instrument-out;
- alternative long-term trend treatment.

Report:
Delta M50(a) and Delta M90(a), not a second generic planet search.

### WP4 — TESS temporal and activity context

Roles:
- estimate stellar rotation/activity periods where defensible;
- improve ephemeris context for known transiting systems;
- provide out-of-sample temporal validation;
- quantify how inference changes as partial FFI releases become complete.

Sector 106 is a control dataset for methodology that will later be applied to the evolving Sector 107 release.

No TESS candidate is called a planet without appropriate external validation.

### WP5 — Atmospheric reproducibility

Datasets:
- Rocky Worlds HLSP;
- NASA Exoplanet Archive atmospheric spectroscopy products;
- source publications for every spectrum or eclipse result used.

Two separate experiments are allowed:
1. repeated-eclipse reproducibility within a programme/target;
2. cross-study spectral consistency across instruments or reductions.

Core statistic:
Estimate the extra variance required to reconcile independent measurements after accounting for reported uncertainties and known covariance limitations.

Do not perform retrieval merely to make the project look larger. A retrieval is justified only if it answers a robustness question.

### WP6 — Gaia interface

Current:
Gaia DR3 and other currently public astrometric information may be used.

Future:
Gaia DR4 integration is an adapter milestone, not a present scientific result. Final schema, table names, and public availability must be verified at implementation time.

## 5. Shared data model

Each observation record should be representable with the following fields or an instrument-specific extension:

- target_id
- canonical_name
- archive
- collection
- instrument
- mode
- product_id
- observation_time
- time_scale
- observable
- value
- uncertainty
- unit
- pipeline_version
- quality_state
- provenance_id
- source_reference

Derived products add:
- method_version
- configuration_hash
- input_manifest_hash
- software_commit
- output_checksum

## 6. Statistical analysis contract

Every major result must state:

- null hypothesis;
- alternative hypothesis;
- likelihood or test statistic;
- nuisance parameters;
- priors, if Bayesian;
- convergence criterion;
- false-alarm or calibration procedure;
- held-out validation, where possible;
- sensitivity to reasonable model alternatives.

Bayes factors and information criteria are supporting diagnostics, not automatic truth machines.

Gaussian processes are used only after demonstrating that a correlated-noise model is warranted. Kernel choice must be motivated and tested.

## 7. Injection and recovery

Injection/recovery is mandatory for claims about detection sensitivity.

The injected parameter grid must be frozen before examining recovery summaries. At minimum the manifest stores:
- period;
- semi-amplitude or radius/depth;
- phase;
- eccentricity distribution where relevant;
- noise realisation;
- target;
- instrument subset;
- recovery rule.

Recovery rules must be harmonic aware and must distinguish:
- detected at injected period;
- alias/harmonic;
- incorrect detection;
- non-detection.

## 8. Null tests

Required families:
- time permutation where scientifically meaningful;
- residual permutation/bootstrap with caveats;
- sign or label shuffling for nuisance relationships;
- off-period injections;
- leave-one-season-out;
- leave-one-instrument-out;
- activity-proxy controls;
- known stable-star controls.

A pipeline that only succeeds on positive examples is not validated.

## 9. Instrument-systematics contract

Instrument effects are model components.

For every RV dataset, inspect:
- hardware upgrades;
- pipeline versions;
- calibration mode;
- drift correction;
- mask/template choice;
- fibre configuration;
- order selection;
- telluric handling;
- barycentric convention;
- zero-point changes;
- duplicated/reprocessed products.

The analysis must be able to reproduce the sample after excluding a problematic instrument era.

## 10. Literature novelty gate

Before a work package produces a novelty statement, the repository must contain a target/question-specific literature note recording:
- search date;
- search terms;
- ADS/SciX or publisher links;
- closest existing analyses;
- exact difference between published work and this project;
- conditions that would make the proposed result non-novel.

The phrase "first ever" is prohibited unless supported by the literature audit.

## 11. Reproducibility contract

A research release must be reconstructable from:
- source manifest;
- environment lock or versioned dependency specification;
- archive acquisition script;
- configuration files;
- deterministic preprocessing where possible;
- random seeds for stochastic tests;
- analysis scripts;
- figure/table generation scripts;
- checksums;
- software commit hash.

Raw third-party archive files should not be mirrored unless licence terms clearly permit it.

## 12. Repository engineering rules

- canonical science code lives in src/exolab;
- notebooks call package code rather than reimplementing it;
- tests include numerical/scientific invariants;
- generated outputs include provenance metadata;
- source URLs and DOIs are kept in machine-readable configuration;
- no credentials are committed;
- no fake detections are committed as science results;
- synthetic data are clearly labelled and isolated.

## 13. Figure standard

Every paper-quality figure must have:
- units;
- uncertainty representation;
- target/sample definition;
- method/version reference;
- caption describing what is measured versus inferred;
- machine-readable source table where feasible.

Interactive figures do not replace static archival figures.

## 14. Milestones

### M0 — Census and frozen manifest
Freeze data sources, target sample, inclusion rules, literature gates, and initial checksums.

### M1 — Acquisition and provenance
Implement archive clients, caching, integrity checks, target identity resolution, and data contracts.

### M2 — Diagnostics
Window functions, activity metrics, periodograms, instrument-era checks, spectral/photometric QC.

### M3 — Joint modelling
Keplerian, chromatic, nuisance, and correlated-noise models with explicit comparison.

### M4 — Injection/recovery
Completeness surfaces, null tests, held-out validation, robustness maps.

### M5 — Population and cross-archive analysis
Aggregate per-target results without erasing target/instrument heterogeneity.

### M6 — Reproducibility release
Frozen environment, release manifest, paper-quality figures/tables, web research interface, citation metadata, and archival release.

## 15. Stop conditions

Pause a work package if:
- public data are insufficient;
- literature already answers the same question;
- target identity is ambiguous;
- pipeline provenance cannot be reconstructed;
- a required calibration product is missing;
- the analysis only becomes interesting after tuning choices to the desired outcome.

A smaller defensible project is preferred to a larger ambiguous one.

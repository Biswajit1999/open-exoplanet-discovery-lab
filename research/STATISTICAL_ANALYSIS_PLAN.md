# Statistical Analysis Plan

## Scope

This document fixes the main statistical comparisons before interpreting the final archive outputs. It is designed to reduce post-hoc tuning and to make null results scientifically interpretable.

## Primary endpoint

The primary EPRV endpoint is the **change in detection completeness** induced by explicit nuisance modelling:

[
Delta C(P,K)=C_{m systematics}(P,K)-C_{m baseline}(P,K)
]

with companion summaries (K_{50}(P)) and (K_{90}(P)), the semi-amplitudes required for 50% and 90% recovery under a frozen recovery rule.

The primary optical/NIR endpoint is not a binary "planet/activity score". It is the joint posterior or uncertainty-aware comparison of:

- period;
- phase;
- semi-amplitude;
- instrument-specific jitter;
- activity-indicator behaviour;
- temporal/seasonal stability.

The primary atmospheric endpoint is the additional between-visit or between-reduction scatter required to make independent measurements statistically consistent.

## Analysis populations

### NETS III
All 41 survey targets are included in the archive census. Per-target science analyses require enough accepted RV epochs after quality and instrument-era cuts to support the requested period range.

### NETS IV / HD 190360
HD 190360 is a validation benchmark because a low-amplitude 88.69 d signal has been published using a much broader RV and astrometric baseline. The project does not treat the published planet as a new discovery.

### NIRPS × HARPS
The sample is frozen from the ESO archive census. A target enters the population analysis only if:
1. identity is unambiguous;
2. public precision-RV products exist from both instruments;
3. NIRPS PROCSOFT passes the documented quality gate;
4. epoch counts and baselines satisfy the frozen sample rule;
5. exact overlap statistics are recorded;
6. the target-specific literature audit does not show that the same archival experiment has already been exhausted.

### Atmospheric spectroscopy
Each row in the NASA Exoplanet Archive `spectra` table is treated as a spectrum-level metadata object. Multiple reductions of the same photons are not counted as independent observations.

## Baseline EPRV model

The minimum model contains:
- per-instrument or per-era offset;
- formal measurement uncertainty;
- per-instrument white jitter;
- deterministic Keplerian term only when a period is explicitly under test.

The baseline search uses a generalized Lomb–Scargle periodogram with an observing-window diagnostic and a frozen period grid.

## Alternative nuisance models

Alternative models are introduced one at a time:

1. instrument-era offsets;
2. activity regression;
3. linear trend;
4. correlated-noise model when residual diagnostics justify it;
5. chromatic amplitude/phase freedom for optical/NIR comparisons.

A lower residual RMS alone does not select a model.

## Model comparison

Report:
- log likelihood;
- BIC;
- AICc when defined;
- held-out predictive residuals where sample size permits;
- posterior predictive diagnostics for Bayesian models;
- sensitivity of the astrophysical parameter of interest.

Bayes factors may be reported only if the prior specification and evidence calculation are stable under reasonable alternatives.

## Period-search calibration

Every claimed periodicity must be accompanied by:
- spectral window;
- analytic FAP where valid;
- simulation or permutation calibration for headline claims;
- alias/harmonic check;
- season-by-season or leave-one-era check where possible.

## Injection/recovery

The injection grid is frozen before aggregate recovery summaries are viewed.

For RV:
- period (P);
- semi-amplitude (K);
- phase;
- eccentricity when the work package requires it;
- target;
- instrument subset;
- noise model;
- random seed.

Recovery can be:
- exact period;
- accepted harmonic;
- wrong period;
- non-detection.

Completeness is always reported with the number of injections contributing to each cell.

## Optical/NIR simultaneity

The census reports unique one-to-one epoch matches within:
- ±1 h;
- ±6 h;
- ±1 d;
- ±3 d;
- ±7 d.

The scientific model does not require simultaneous observations, but simultaneity determines how strongly active-region evolution can confound a direct wavelength comparison.

## Activity analysis

Activity indicators are diagnostic covariates, not truth labels.

The analysis checks:
- indicator periodogram;
- RV–indicator correlation;
- slope uncertainty;
- season dependence;
- whether correction changes the fitted planet amplitude;
- whether correction lowers residual scatter while biasing an injected planet.

## Atmospheric reproducibility

For repeated scalar measurements (y_i) with quoted errors (sigma_i), estimate an extra scatter (	au) using

[
chi^2(	au)/(N-1)=1
]

when the zero-extra-scatter model is overdispersed. This is a transparent empirical reproducibility floor, not a replacement for a full covariance model.

## Multiple testing

Population-level searches will report:
- number of targets searched;
- number of periods/trials or effective frequency range;
- per-target FAP calibration;
- any family-level correction used.

No single low p-value is presented without the search context.

## Null results

A null result is retained when it constrains:
- (K_{50}) or (K_{90});
- mass sensitivity;
- an amplitude-ratio interval;
- extra atmospheric scatter;
- the magnitude of an instrumental-era effect;
- the maximum change introduced by a more complex model.

## Frozen reporting language

Allowed:
- "recovered"
- "consistent with"
- "inconsistent with under this model"
- "requires additional scatter"
- "not detected above the stated completeness limit"
- "candidate signal"

Not allowed without independent confirmation:
- "new planet"
- "confirmed planet"
- "activity-free"
- "first ever"
- "definitive"

## Reproducibility

Every headline number must carry:
- manifest hash;
- software commit;
- analysis configuration hash;
- input product identifiers;
- units;
- result state: measured, derived, fitted, simulated, literature, or provisional.

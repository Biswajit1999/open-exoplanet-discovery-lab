# A-to-Z Research Build Reference

This document is the operational alphabet for the project. Each letter maps to a scientific or engineering checkpoint that should exist before the corresponding analysis is considered mature.

## A — Acquisition
All archive access is scripted. Store the query, access date, endpoint, archive collection, and exact product identifiers. Manual downloads may be used for debugging but never as the only reproducible path.

## B — Bibliography and benchmark systems
Maintain a question-specific literature file for each work package. Define benchmark stars/planets with known signals, known activity cases, and stable controls before tuning models.

## C — Crossmatch and canonical identity
Resolve target aliases to a canonical name and Gaia source identifier where possible. Record coordinate epoch, match radius, and ambiguity flags. Never join datasets on a loose string match alone.

## D — Data contracts
Define schema, units, time systems, quality flags, nullable fields, instrument mode, and provenance keys. Reject silent unit conversion.

## E — EPRV baseline
For each RV target, reproduce the simplest defensible baseline: timestamps, RVs, formal errors, weighted mean, RMS, cadence, window function, and a documented period search.

## F — False-alarm calibration
Do not report a periodogram peak without an explicit calibration strategy. Use analytic FAP only where assumptions are justified; otherwise add bootstrap/permutation or simulation-based calibration.

## G — Gaussian-process gate
A GP is not the default. First show evidence for correlated residual structure or activity-linked covariance. Compare kernels and check whether real planetary power is being absorbed.

## H — Harmonisation
Harmonise only what has a physical reason to be comparable. Track velocity convention, time standard, wavelength regime, zero-point epoch, reduction pipeline, and instrument upgrades.

## I — Injection and recovery
Freeze the injected population before reading the final recovery map. Save every injected parameter and recovery decision. Report completeness and reliability, not only successful recoveries.

## J — Joint likelihood
When combining instruments, use one physically motivated joint model with instrument-specific offsets/jitters and shared astrophysical parameters where justified. Do not concatenate RV columns and treat them as one instrument.

## K — Keplerian model
State the parameterisation, priors, eccentricity treatment, reference epoch, and convergence diagnostics. Known-planet fits are validation cases before any new-signal interpretation.

## L — Literature novelty gate
For every claim, record the closest prior paper and the exact difference. If the difference is merely a new plot, the work package does not pass the gate.

## M — Metadata and manifests
Every release receives an immutable manifest containing source identifiers, checksums, software commit, configuration hashes, and inclusion/exclusion rules.

## N — Null tests
Include stable-star controls, activity controls, off-period tests, leave-one-season-out tests, leave-one-instrument-out tests, and synthetic null datasets where useful.

## O — Optical/NIR comparison
For HARPS/NIRPS work, compare period, phase, K, activity proxies, and season dependence. Never assume activity amplitude monotonically decreases toward the NIR.

## P — Photometric context
Use TESS to constrain rotation, variability, transit ephemerides, and temporal consistency. Photometric periodicity is context, not automatic proof of an RV activity origin.

## Q — Quality control
Preserve rejected points and rejection reasons. QC must be reproducible from explicit rules, not from invisible manual cleaning.

## R — Reproducibility
A release is valid only if a clean environment can reacquire the public inputs and regenerate the declared figures/tables. Randomised analyses record seeds.

## S — Systematics
Instrument upgrades, DRS versions, calibration states, tellurics, barycentric corrections, fibre changes, and detector/order effects are first-class model inputs.

## T — TESS temporal validation
Use mature sectors to calibrate the method and newer releases for out-of-sample tests. Distinguish partial FFI availability from final mission products.

## U — Uncertainty
Propagate measurement uncertainty, nuisance-parameter uncertainty, model uncertainty, and where possible inter-reduction/inter-visit scatter. Do not quote more precision than the analysis supports.

## V — Validation
Validate on known planets, known activity cases, and stable stars. Cross-check recovery on held-out data. A good-looking posterior is not validation.

## W — Web research interface
The website must expose evidence, provenance, uncertainty, and method state. It is not a decorative dashboard. Static paper-quality outputs remain canonical.

## X — Cross-archive evidence
Cross-archive joins require a scientific question: for example RV plus TESS rotation, RV plus Gaia astrometry, or repeated atmospheric spectra. More archives do not automatically mean stronger evidence.

## Y — Yield and completeness
Translate pipeline performance into physically interpretable quantities such as K50, K90, mass sensitivity, radius/depth sensitivity, or empirical reproducibility floors.

## Z — Zenodo / archival release
For major versions, prepare a citable research release with frozen manifests, environment information, source references, generated results, and a clear statement of what is and is not claimed.

---

# Work-package execution order

## Phase 0 — Foundation
A, B, C, D, L, M, Q, R.

## Phase 1 — EPRV core
E, F, G, H, J, K, N, S, U, V.

## Phase 2 — Detection sensitivity
I, Y.

## Phase 3 — Cross-wavelength and cross-archive
O, P, T, X.

## Phase 4 — Public research interface
W.

## Phase 5 — Archival release
Z.

---

# Scientist-facing definition of done

A work package is not done when the code runs. It is done when another researcher can answer all of the following without asking the author:

1. Which public observations entered the sample?
2. Which observations were rejected and why?
3. Which version of each reduction pipeline produced the inputs?
4. What model was fitted?
5. Which assumptions were fixed in advance?
6. Which nuisance terms were fitted?
7. How was significance or model comparison calibrated?
8. What null tests were run?
9. How was sensitivity/completeness measured?
10. Which result is measurement, which is model-dependent inference, and which is interpretation?
11. Which prior papers most closely overlap the analysis?
12. Can the result be regenerated from a frozen manifest?

If any answer is missing, the corresponding result remains provisional.

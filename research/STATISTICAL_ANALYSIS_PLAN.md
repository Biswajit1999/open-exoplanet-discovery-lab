# Statistical Analysis Plan

## Scope

This plan is frozen before interpretation of new archive-derived signals. It separates descriptive diagnostics, confirmatory comparisons, and exploratory follow-up.

## 1. Measurement model

For radial velocities from instrument or reduction stream j,

v_i = gamma_j + v_Kep(t_i; theta) + v_activity(t_i) + epsilon_i,

where gamma_j is an instrument/reduction zero point and epsilon_i contains the reported measurement uncertainty plus an instrument-specific jitter term when justified.

A linear trend is added only when a long-timescale acceleration is physically or empirically supported.

## 2. Period searches

GLS periodograms are diagnostic search tools, not planet validators.

Every interpreted peak requires:
- observing-window inspection;
- alias/harmonic assessment;
- analytic FAP as a baseline;
- permutation/bootstrap or simulation calibration where assumptions are questionable;
- activity-period comparison;
- stability across observing seasons or instrument subsets.

## 3. Keplerian fitting

Known signals are fitted before any unidentified signal is interpreted.

The full Keplerian parameterisation may include:
- P;
- K;
- epoch/mean longitude;
- e and omega using a sampling-stable transformation;
- per-instrument gamma;
- per-instrument jitter.

Circular fits are permitted as benchmark models but must not silently define the final completeness model for long-period giant-planet work.

## 4. Activity models

Activity regressors are admitted only if:
1. the proxy has a defined physical/instrumental meaning;
2. its temporal behaviour is inspected;
3. the model is evaluated out of sample or by held-out epochs;
4. a real injected/known Keplerian signal is not systematically absorbed.

Gaussian processes require an explicit correlated-noise gate. Kernel hyperparameters and priors are reported.

## 5. Optical/NIR coherence

At a shared candidate period, estimate:
- K_VIS;
- K_NIR;
- phase_VIS;
- phase_NIR;
- instrument-specific jitter;
- activity-proxy dependence.

Primary diagnostics:
- posterior or bootstrap distribution of K_NIR/K_VIS;
- wrapped phase difference;
- likelihood improvement of a chromatic-amplitude model over an achromatic model;
- season-to-season stability.

No rule assumes that stellar activity is weaker in the NIR in every physical regime.

## 6. Injection/recovery

For sensitivity claims, inject signals before final recovery summaries are inspected.

Each injection records:
- target;
- timestamp set;
- instrument subset;
- P;
- K;
- phase;
- eccentricity or eccentricity prior where used;
- random seed;
- activity/noise model;
- recovery decision.

Recovery must classify injected period, harmonics/aliases, incorrect periods and non-detections separately.

## 7. Completeness summaries

Report C(P,K) and physically useful contours such as K50(P) and K90(P).

For model-comparison experiments report:

Delta C(P,K) = C_systematics-aware(P,K) - C_baseline(P,K).

A null Delta C is a robustness result, not a failed project.

## 8. Repeated atmospheric measurements

For repeated eclipse depths or compatible spectral bins, estimate a non-negative between-measurement variance term in addition to reported formal uncertainties.

This term is described as an empirical reproducibility scale unless astrophysical variability can be independently separated from reduction/instrument effects.

Independent observations and alternate reductions of the same photons are labelled separately.

## 9. Multiple testing

Population scans report how many stars/periods were searched. Exploratory peaks are not upgraded to discoveries by quoting only a local single-frequency statistic.

## 10. Validation hierarchy

Level 0 — unit/numerical tests  
Level 1 — deterministic synthetic injections  
Level 2 — known published signals and stable controls  
Level 3 — held-out seasons/instruments  
Level 4 — independent archive or wavelength validation  
Level 5 — new astrophysical interpretation

No result is presented at Level 5 if it has only passed Level 0–1.

## 11. Reporting

Every headline number carries:
- sample definition;
- uncertainty;
- model family;
- release/manifest identifier;
- software commit;
- status: measured / fitted / simulated / literature / provisional.

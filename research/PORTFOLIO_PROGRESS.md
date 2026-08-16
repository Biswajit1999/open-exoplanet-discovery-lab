# Exoplanet portfolio deepening: persistent progress ledger

Last updated: 2026-08-16

This file is the handoff record for the 31-repository scientific deepening
programme in [`PORTFOLIO_DEEPENING_MATRIX.md`](PORTFOLIO_DEEPENING_MATRIX.md).
It records completed, merged work rather than intentions. A target is marked
complete only after its new data provenance, reproducible analysis, generated
outputs, tests, report text, and GitHub checks have all been reviewed and merged.

## Merged upgrades: 5 of 31 targets

| Target | Scientific extension | Reproduced result | Verification | Merged work |
|---|---|---|---|---|
| WASP-12 b | Individual-transit timing and long-baseline orbital-decay comparison | 62 supported TESS events do not prefer TESS-only curvature (Delta BIC = -1.9); 158 published timings give Pdot = -29.28 +/- 2.03 ms/yr, Delta BIC = 202.5, a 3.22 Myr timescale, and conditional Q-prime-star about 2.07e5 | Tests passed locally and in Python 3.11/3.12 CI | [PR 2](https://github.com/Biswajit1999/wasp-12b-exoplanet-report/pull/2), merge `a9b50bd` |
| WASP-19 b | Individual-transit timing limits with correlated-noise inflation | 89 supported TESS events over 1,496 d prefer a linear ephemeris (Delta BIC linear-minus-quadratic = -3.529); conditional Pdot = -199 +/- 203 ms/yr and weak Q-prime-star lower bound 4.7e3 expose the baseline's limited curvature leverage | 8 tests plus Python 3.11/3.12 CI | [PR 2](https://github.com/Biswajit1999/wasp-19b-exoplanet-report/pull/2), merge `2c285fe` |
| WASP-39 b | Public JWST/PRISM CO2 model-ablation robustness | Supplied no-CO2-minus-full diagnostic Delta chi-square = 774.8; worst leave-one-bin value 685.0, factor-8 rebin 596.1, and strong illustrative correlated-covariance cases 135-139; methane-like significance language is explicitly avoided | 10 tests plus Python 3.11/3.12 CI; figure inspected | [PR 2](https://github.com/Biswajit1999/wasp-39b-exoplanet-report/pull/2), merge `cd46099` |
| WASP-43 b | Phase-resolved thermal spectrum and conditional energy budget | Blackbody-star color temperatures 1,597 +/- 15 K dayside and 890 +/- 18 K nightside; 708 +/- 24 K contrast, flux ratio 3.22, and 9.23 +/- 0.45 degree eastward hotspot proxy; conditional Cowan-Agol grid A_B = 0.218 and epsilon = 0.221 is labelled non-retrieval | 10 tests plus Python 3.11/3.12 CI; figure inspected | [PR 2](https://github.com/Biswajit1999/wasp-43b-exoplanet-report/pull/2), merge `d75fb6b` |
| WASP-80 b | Cross-geometry methane morphology using the Nature source workbook | No-CH4-minus-full diagnostics are 84.36 in transmission and 240.65 in emission; worst leave-one-bin values are 64.60 and 202.50, and factor-4 values are 77.35 and 219.96. Published log-CH4 abundances agree within 0.34 sigma | 10 tests plus Python 3.11/3.12 CI; figure inspected | [PR 2](https://github.com/Biswajit1999/wasp-80b-exoplanet-report/pull/2), merge `a80c980` |

The chi-square differences above are repository diagnostics unless explicitly
identified as a published likelihood comparison. They are not automatically
detection significances. The individual reports document the exact data source,
assumptions, transformations, and scientific limitations.

## Current pilot status

| Pilot | Complete | Next targets |
|---|---:|---|
| Timing | 2 / 3 | Kepler-51 b |
| Spectral robustness | 1 / 4 | LHS 475 b, K2-18 b, TRAPPIST-1 e |
| Energy budget | 1 / 4 | 55 Cancri e, GJ 1214 b, WASP-18 b |
| Escape | 0 / 4 | HAT-P-11 b, GJ 3470 b, WASP-69 b, WASP-107 b |
| Additional cross-geometry chemistry | 1 / 1 | WASP-80 b complete |

## Next recommended upgrade

Proceed with **LHS 475 b atmospheric exclusion analysis**. It complements the
positive molecular-feature cases with a scientifically important non-detection:
reproduce which clear atmospheres the public spectrum excludes, repeat the
comparison under coarser binning and covariance assumptions, express model
amplitudes in scale heights, and distinguish "excluded", "not detected", and
"not tested". Start from the repository's existing committed data and the
primary paper DOI `10.1038/s41550-023-02064-z`; retrieve additional public data
only with a checksum and transformation record.

After LHS 475 b, finish Kepler-51 b timing, then K2-18 b and TRAPPIST-1 e
spectral robustness. This completes two pilot stories before starting the energy
and escape cohorts.

## Resume protocol

For every target:

1. Begin from the remote default branch and confirm the working tree is clean.
2. Audit existing data, scripts, report claims, tests, and primary literature.
3. Add only public or clearly derived data with URL/DOI, retrieval date,
   checksum, units, and deterministic transformation notes.
4. Implement a target-specific quantitative question, at least one alternative
   model, sensitivity tests, machine-readable outputs, and a report figure.
5. Keep repository diagnostics separate from published retrieval evidence and
   avoid novelty or detection claims that the calculation cannot establish.
6. Run the full local suite, inspect the figure, commit on a `codex/` branch,
   open a ready pull request, wait for every CI job, and merge only when green.
7. Add the merged PR, merge commit, numerical headline, and next target to this
   ledger before ending the session.

## Remaining 26 targets

55 Cancri e, GJ 1214 b, GJ 3470 b, GJ 9827 d, HAT-P-11 b, HAT-P-26 b,
HAT-P-32 b, HD 106315 b, HD 149026 b, HD 189733 b, HD 209458 b, HD 97658 b,
K2-18 b, Kepler-51 b, LHS 475 b, LTT 9779 b, TOI-270 d, TOI-836 b,
TRAPPIST-1 e, WASP-17 b, WASP-18 b, WASP-69 b, WASP-96 b, WASP-107 b,
WASP-121 b, and WASP-127 b.

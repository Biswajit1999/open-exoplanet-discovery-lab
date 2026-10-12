# Literature and Novelty Audit

This file records the closest prior work and prevents the repository from claiming novelty by omission.

## NETS III

Primary survey reference:
- Gupta et al., *The NEID Earth Twin Survey. III. Survey Performance After Three Years on Sky*, AJ 170, 264 (2025), DOI 10.3847/1538-3881/ae0339.
- VizieR J/AJ/170/264.

Published work already includes:
- 41-star survey description;
- the full NEID RV and stellar-activity time series;
- calibration/discussion of instrument zero-point changes;
- RVSearch analysis and sensitivity to known planets;
- newly detected RV signals flagged for follow-up.

Therefore this project must **not** present a re-run of RVSearch or a reproduction of the survey plots as the scientific contribution.

Remaining project question:
How much do the survey completeness surfaces change when instrument-era structure, activity conditioning, correlated residuals, and held-out-era validation are treated as explicit robustness dimensions?

## NETS IV / HD 190360

Primary reference:
- Giovinazzi et al., *The NEID Earth Twin Survey. IV. Confirming an 89 d, m sin i ≈ 10 Earth-mass Planet Orbiting a Nearby Sun-like Star*, AJ 171, 286 (2026), DOI 10.3847/1538-3881/ae48f1.
- VizieR J/AJ/171/286.

Published result:
- period near 88.69 d;
- semi-amplitude about 1.48 m/s;
- more than 30 years of RV context;
- Hipparcos/Gaia astrometric information;
- nearly 100 NEID observations.

Project role:
Use this as a known low-amplitude benchmark for recovery, instrument-era tests, and model sensitivity. It is not a discovery target.

## NIRPS Phase-3 × HARPS

Archive facts:
- ESO released the NIRPS pipeline-reduced open stream in May 2025.
- NIRPS spans roughly 970–1850 nm and complements optical HARPS.
- The release grows continuously.
- ESO documented a precision-RV issue affecting DRS 3.2.6 observations from 2025-04-01 12:00 to 2025-07-24 12:00 and reprocessed the affected Phase-3 products with DRS 3.2.7.

Novelty rule:
A population-level optical/NIR coherence analysis may proceed only after target-by-target ADS/publisher searching verifies that the exact joint comparison is not already published for the same systems.

Prior optical/NIR RV literature from HARPS+CARMENES, HARPS+SPIRou, CARMENES VIS/NIR and similar programmes must be treated as methodological precedent, not ignored.

The project will not claim that stellar activity always decreases toward the NIR. Cool spots, faculae, convective effects, Zeeman sensitivity, line selection, tellurics, and active-region evolution can produce non-monotonic wavelength behaviour.

## SPORES-HWO II

Primary reference:
- Harada et al., *The SPORES-HWO Survey. II. Thirty-five Years of Radial
  Velocity Monitoring of 141 Nearby Stars*, AJ 170, 343 (2025), bibcode
  `2025AJ....170..343H`.
- VizieR J/AJ/170/343.

Published work already includes the heterogeneous 1987–2023 RV compilation,
catalogued signals and trends, and circular-orbit habitable-zone sensitivity
products for the eligible sample. The catalogue tables were verified public
on 2026-10-12.

This project therefore does not claim to discover the catalogue, its signals,
or its baseline sensitivity result. Its bounded extension is a pre-declared
no-catalogued-signal control analysis that varies instrument offsets, empirical
white versus order-preserving nulls, eccentric injections and removal of the
dominant instrument. Exact TESS-SVC links provide independent variability
context, not a rotation or planet classification.

## TESS

TESS/SPOC/QLP already provide extensive transit-search and vetting infrastructure. The project therefore uses new sectors primarily for:
- out-of-sample temporal validation;
- stellar rotation/activity context;
- ephemeris checks;
- completeness experiments with explicit held-out time ranges.

A BLS peak alone is not novel.

## Atmospheric spectroscopy

NASA Exoplanet Archive's current `spectra` table groups published spectra and explicitly preserves multiple reductions as separate spectra when publications provide them.

The project question is reproducibility:
How much between-visit, between-reduction, or between-instrument scatter is required to reconcile independent published measurements?

A simple overplot of spectra is not considered a research result.

## Rocky Worlds

The MAST Rocky Worlds HLSP is an active, versioned programme containing repeated MIRI secondary-eclipse products and HST host-star products. Individual target science is already being analysed by the programme teams; this repository focuses on transparent repeatability metrics and reduction/visit sensitivity.

## Gaia

Gaia DR3 may be used now for identity and current astrometric context. Gaia DR4 is a future adapter only until the release and final archive schema are public.

## Novelty claim template

Before any paper or README statement uses words such as "new", "first", "unexplored", or "novel", add a dated entry containing:
- exact question;
- ADS/SciX search terms;
- closest three papers;
- their samples and methods;
- the measurable difference introduced here;
- what finding would make the claim non-novel.

Absence of a matching title is not evidence of novelty.

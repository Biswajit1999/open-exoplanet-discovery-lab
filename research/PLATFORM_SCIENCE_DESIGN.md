# Platform science design

## Scientific objective

Build an open, auditable system that turns public survey measurements into three useful outputs:

1. **candidate report cards** for transit-like signals requiring human review;
2. **completeness maps** describing which planets a search could and could not recover;
3. **homogeneous physical summaries** connecting the 31 existing target reports.

The project is not an automated planet-announcement machine. Its credible contribution is transparent triage, reproducibility and well-calibrated uncertainty.

## Live data graph

```text
NASA Exoplanet Archive
  ├── ps / pscomppars: confirmed systems and parameters
  ├── toi: TESS Objects of Interest and dispositions
  └── Kepler TCE tables: threshold-crossing events

MAST
  ├── TESS SPOC/TESS-SPOC light curves
  ├── target-pixel files
  ├── full-frame images through TESScut
  └── data-validation reports and time series

Gaia DR3
  └── neighbours, astrometry, colour, duplicated-source and RUWE context

ExoFOP-TESS / literature
  └── candidate dispositions, follow-up notes and prior analyses
```

The NASA Exoplanet Archive exposes `ps`, `pscomppars`, `toi`, microlensing, KOI and Kepler TCE tables through TAP. MAST provides the actual TESS pixels, light curves, FFIs and validation products. Gaia supplies the spatial-confusion layer that a one-dimensional light curve cannot provide.

## Search stages and outputs

### 1. Reproducible target selection

Select current TOIs using explicit cuts on disposition, magnitude, radius, period and data availability. Preserve the complete returned table and retrieval time. A ranking score is a scheduling convenience, never a probability that the signal is planetary or novel.

### 2. Independent photometry paths

For a high-priority signal compare:

- mission-produced PDCSAP flux;
- raw SAP flux with explicit detrending;
- at least one FFI extraction using a documented aperture/background model.

A signal that exists in only one reduction is a diagnostic problem, not a discovery.

### 3. Transit search

Use BLS as the transparent baseline and TLS as an optional small-planet extension. Save the full searched period/duration domain, not only the maximum peak. Iteratively mask strong signals only after checking harmonics and data gaps.

### 4. Automated attempts to falsify

- odd versus even depths;
- secondary eclipse near phase 0.5;
- transit count and single-event dominance;
- duration versus stellar-density plausibility;
- V-shape/grazing diagnostic;
- rolling-band, momentum-dump and scattered-light coincidence;
- centroid/difference-image displacement;
- nearby Gaia source dilution;
- repeatability between sectors and reductions.

### 5. Completeness and false-alarm calibration

Inject signals before detrending, rerun the complete pipeline and recover on a period–depth–duration grid. Use time-scrambling or transit-time scrambling to estimate empirical false-alarm behaviour. Publish both successful and failed injections.

### 6. Human review and escalation

Candidate cards should link directly to plots, product identifiers, code commit and rejection flags. High-priority objects should be reviewed by more than one person. Only then should the project consider ExoFOP coordination or observational follow-up.

## Twenty future modules—not twenty empty repositories

These are best implemented as tested modules or substantial case studies. Promote a module into its own repository only when it has independent data, results and a clear research question.

1. Gaia astrometric acceleration and known-planet cross-match.
2. Transit-timing-variation search and ephemeris forecasting.
3. Orbital-decay model comparison for ultra-short-period giants.
4. Circumbinary planets through eclipse-timing variations.
5. Pulsar-timing planet tutorial using public timing residuals.
6. Optical phase curves: reflection, beaming and ellipsoidal variation.
7. Infrared phase curves and day–night energy budgets.
8. High-resolution molecular cross-correlation spectroscopy.
9. Atmospheric escape from He I 10830 Å and Lyα proxies.
10. Exomoon injection–recovery and correlated false positives.
11. Ring and asymmetric-transit searches.
12. Transit-duration variations and nodal precession.
13. Difference-image centroid vetting for TESS FFIs.
14. Gaia-aware dilution and background-eclipsing-binary simulation.
15. Statistical validation comparison with TRICERATOPS/vespa-style inputs.
16. Direct-imaging orbit fitting and observability forecasting.
17. Microlensing event-model and degeneracy laboratory.
18. Atmospheric retrieval reproducibility benchmark across pipelines.
19. Occurrence rates with empirically measured completeness.
20. Follow-up scheduler using ephemeris uncertainty and observatory visibility.

## Gate for creating a separate repository

A proposed repository must have all of the following:

- a question not already answered by another portfolio project;
- an immutable public dataset or documented live query;
- at least one quantitative null-versus-alternative comparison;
- uncertainty propagation or a justified limitation;
- an executable notebook/script and regression test;
- machine-readable output;
- a conclusion that distinguishes direct calculation from cited literature;
- a route to falsification or independent validation.

If it lacks those elements, it remains a module or issue in this platform rather than increasing the repository count.

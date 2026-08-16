# Scientific deepening programme for 31 exoplanet reports

Implementation status, merged pull requests, headline measurements, and the
next-session handoff are maintained in
[`PORTFOLIO_PROGRESS.md`](PORTFOLIO_PROGRESS.md).

## Standard of evidence

“No one else has done this” is not a result that can be established from a quick search. Each repository should use the following labels:

1. **Reproduction** — the repository independently reproduces a published quantity.
2. **Extension** — it applies an established method to an additional sector, reduction, model grid or diagnostic.
3. **Original synthesis** — it combines public measurements in a new homogeneous comparison.
4. **Novel candidate result** — reserved until a documented ADS/arXiv search, independent review and appropriate validation have been completed.

The immediate opportunity is an original **homogeneous synthesis** across the portfolio, with target-specific extensions inside each repository. That is more defensible than claiming 31 unrelated discoveries.

## Every report should answer five quantitative questions

1. What was measured, with units, uncertainty and provenance?
2. Which physical model was fitted, and what assumptions were fixed?
3. How much better is it than a stated null or alternative model?
4. Which physical quantities follow, with propagated uncertainties?
5. Which conclusions are excluded, unresolved or dependent on a published retrieval?

Every derived table should preserve machine-readable values, units, uncertainty type, data DOI, code version and retrieval date. Report effect sizes and confidence intervals alongside p-values or information criteria.

## Target-specific enhancement matrix

| Target | Lead question | Quantitative additions beyond the existing report | Primary starting point |
|---|---|---|---|
| 55 Cancri e | Is the dayside emission genuinely variable between observing seasons? | Refit the eight individual Spitzer eclipses hierarchically; compare constant, season-dependent and stochastic-depth models; propagate eclipse depth into brightness temperature; map the albedo–recirculation degeneracy; report Bayes/likelihood criteria and posterior predictive checks. | [Demory et al. phase map](https://doi.org/10.1038/nature17169); [CHEOPS phase curve](https://doi.org/10.1051/0004-6361/202140892) |
| GJ 1214 b | What combinations of metallicity, albedo and heat transport remain compatible with its phase curve? | Recalculate wavelength-dependent day/night brightness temperatures; integrate hemispheric fluxes; fit a redistribution–Bond-albedo grid; test whether one offset or wavelength-correlated covariance changes the inference. | [Kempton et al. 2023](https://doi.org/10.1038/s41586-023-06159-5) |
| GJ 3470 b | Can photochemical SO2 and atmospheric escape be placed on one energy budget? | Add the public JWST spectrum; compare equilibrium and photochemical templates with fitted offsets; calculate scale height, Jeans parameter and energy-limited escape ranges; separate repository likelihood ratios from published molecular significances. | [Beatty et al. 2024](https://doi.org/10.3847/2041-8213/ad55e9) |
| GJ 9827 d | Does the measured water feature require a steam-dominated atmosphere? | Add HST and public JWST spectra; measure feature amplitude in scale heights; compare high-mean-molecular-weight steam, cloudy H/He and flat models with identical binning; propagate mass/radius uncertainty into surface gravity and scale height. | [HST water absorption](https://www.ipac.caltech.edu/publication/2023ApJ...954L..52R); [JWST steam-world analysis](https://arxiv.org/abs/2410.03527) |
| HAT-P-11 b | Is the helium absorption kinematically consistent with an escaping wind? | Measure equivalent width, line centroid, blue/red-wing asymmetry and excess depth under multiple continuum windows; bootstrap transit pairs; compute Roche-lobe radius, escape velocity and a mass-loss proxy; test sensitivity to stellar activity. | [Allart et al. 2018](https://doi.org/10.1126/science.aat5879) |
| HAT-P-26 b | How robust are metallicity and sulfur chemistry across wavelength coverage? | Join HST, Spitzer and public JWST bins with instrument offsets; compare flat, equilibrium and photochemical models; calculate metallicity/C/O/S/O sensitivity to bin removal; display leave-one-instrument-out results. | [HST SHEL](https://doi.org/10.3847/1538-3881/adc1c1); [JWST SO2](https://arxiv.org/abs/2509.16082) |
| HAT-P-32 b | Are haze, clouds and escape distinguishable in the available transmission data? | Retrieve the optical/near-IR spectrum; fit a Rayleigh-like slope and grey cloud deck; convert slope to an effective scattering temperature; compare Na/K windows; calculate an escape parameter and show which conclusions depend on unocculted spots. | [NASA Exoplanet Archive system record](https://exoplanetarchive.ipac.caltech.edu/) |
| HD 106315 b | Where does the planet fall between rocky, water-rich and H/He-envelope interiors? | Perform a mass–radius Monte Carlo against simple end-member composition curves; quantify incident flux and escape parameter; jointly examine b/c ephemerides for correlated timing residuals; add injection–recovery limits for additional short-period transits. | [Barros et al. masses and interiors](https://arxiv.org/abs/1709.00865) |
| HD 149026 b | Can its large heavy-element inventory be connected to its atmospheric spectrum? | Convert each emission bin to brightness temperature; fit blackbody versus structured models; infer day-side effective temperature and redistribution range; compare bulk heavy-element estimates with atmospheric metallicity under clearly separated model assumptions. | [Bean et al. 2023](https://doi.org/10.1038/s41586-023-05984-y) |
| HD 189733 b | Are molecular features stable against stellar heterogeneity and reduction choices? | Rebin the public NIRCam spectrum at several resolutions; compare H2S/no-H2S templates with correlated-noise sensitivity; model spot/facula contamination slopes; report leave-one-channel-out evidence and cross-instrument offsets. | [Public NIRCam products](https://doi.org/10.5281/zenodo.11459715) |
| HD 209458 b | Which spectral structures survive all four MIRI reductions? | Build a covariance-aware consensus spectrum; quantify between-pipeline variance per wavelength; compare blackbody/cloud templates; run jackknife analyses and label features that disappear under one valid reduction. | [Public four-reduction products](https://doi.org/10.5281/zenodo.20089901) |
| HD 97658 b | How strongly do the data exclude a clear low-metallicity atmosphere? | Add the HST spectrum; express modulation in atmospheric scale heights; compare flat, cloudy and clear templates; propagate stellar-radius and mass uncertainties; report cloud-top pressure only as model-dependent. | [Guo et al. 2020](https://doi.org/10.3847/1538-3881/ab8815) |
| K2-18 b | Which molecular claims are robust to reduction, binning and noise model? | Create a pre-registered matrix of spectra × binnings × covariance assumptions × molecule sets; report evidences without translating arbitrary Δχ² into sigma; reproduce red-noise and leave-one-bin tests; separate CH4/CO2 robustness from disputed sulfur-bearing species. | [Comprehensive reanalysis](https://doi.org/10.3847/1538-3881/ae019a); [systematic trace-molecule search](https://doi.org/10.3847/2041-8213/ae5dcc) |
| Kepler-51 b | Do public timings require dynamics beyond the original three-planet solution? | Combine Kepler, TESS and published JWST mid-times; fit linear ephemeris and N-body/TTV alternatives; publish O–C residuals and model comparison; propagate timing uncertainty into future transit windows. | [Discovery/TTV system](https://ui.adsabs.harvard.edu/abs/2013MNRAS.428.1077S/abstract) |
| LHS 475 b | Which atmosphere classes are excluded by a flat spectrum, rather than merely undetected? | Reproduce model rejection with the public bins; add covariance and binning sensitivity; translate model amplitudes into scale heights; build an exclusion table for clear H2, CH4-rich, CO2-rich/cloudy and airless cases without turning non-detection into absence. | [Lustig-Yaeger et al. 2023](https://doi.org/10.1038/s41550-023-02064-z) |
| LTT 9779 b | What combination of reflection and heat redistribution explains survival in the hot-Neptune desert? | Combine TESS occultation/phase constraints with published optical and IR measurements; solve a joint geometric-albedo/brightness-temperature grid; compare energy redistribution assumptions; quantify whether the atmosphere is consistent with a reflective cloud deck. | [Discovery paper](https://ui.adsabs.harvard.edu/abs/2020NatAs...4.1148J/abstract) |
| TOI-270 d | How dependent are atmospheric and interior interpretations on the adopted spectrum and temperature profile? | Compare independent reductions; calculate feature amplitudes and molecule-template likelihoods; couple mass/radius draws to simple rock–water–H/He interiors; examine c/d transit timings jointly; distinguish detections, tentative evidence and upper limits. | [Discovery](https://ui.adsabs.harvard.edu/abs/2019NatAs...3.1099G/abstract) |
| TOI-836 b | What does a featureless spectrum quantitatively rule out? | Express residual structure in scale heights; inject clear H2/He models at varying metallicity and cloud pressure; determine rejection boundaries; compare NRS1/NRS2 offsets and multiple reductions; include stellar-heterogeneity alternatives. | [JWST COMPASS data study](https://arxiv.org/abs/2404.00093) |
| TRAPPIST-1 e | Can planetary transmission be separated from visit-dependent stellar contamination? | Fit all four visits jointly and independently; compare contaminated and decontaminated spectra; reproduce the cloudy-H2 exclusion; test plausible secondary atmospheres without calling a flat spectrum airless; publish visit-jackknife results. | [Espinoza et al. 2025](https://arxiv.org/abs/2509.05414); [MAST data DOI](https://doi.org/10.17909/yzwd-vq54) |
| WASP-107 b | Can disequilibrium chemistry, clouds and internal heating be tested with one public spectral comparison? | Join public NIRISS/NIRSpec/MIRI products where available; compare CH4, SO2 and silicate-cloud ablations; estimate quench-pressure sensitivity and scale heights; keep published retrieval evidence separate from repository diagnostics. | [Public NIRISS products](https://doi.org/10.5281/zenodo.17085766) |
| WASP-121 b | Which thermal-inversion and metal signatures are reduction-stable? | Build a multi-pipeline consensus spectrum; convert eclipse depth to brightness temperature; fit monotonic versus inverted temperature profiles; quantify wavelength-dependent pipeline dispersion; examine phase/epoch variability without overinterpreting single-bin features. | [Public JWST products](https://doi.org/10.5281/zenodo.20651891) |
| WASP-127 b | Can low- and high-resolution spectroscopy agree on wind geometry? | Add public spectra where licensing permits; cross-correlate species templates; map line-of-sight velocities against limb; compare high-resolution velocities with low-resolution abundance/cloud constraints; propagate systemic-velocity uncertainty. | [Discovery record](https://ui.adsabs.harvard.edu/abs/2017A%26A...599A...3L/abstract) |
| WASP-12 b | Does the enlarged TESS baseline recover orbital decay independently? | Fit every usable transit midpoint; construct an O–C diagram; compare linear, quadratic-decay and apsidal-precession ephemerides with BIC and posterior predictive residuals; infer period derivative and stellar tidal quality factor with published formulae. | [Yee et al. 2020](https://arxiv.org/abs/1911.09131) |
| WASP-17 b | What do the emission data imply about temperature structure and water opacity? | Convert three independent reductions to brightness temperature; estimate between-pipeline covariance; compare blackbody and molecular templates; quantify whether the inferred structure survives resolution changes and single-channel deletion. | [JWST-TST DREAMS release](https://arxiv.org/abs/2410.08149) |
| WASP-18 b | How strongly do the data require a thermal inversion and inefficient heat redistribution? | Fit blackbody, monotonic and inverted temperature-profile surrogates; calculate band brightness temperatures; integrate dayside flux; map recirculation efficiency; compare all reductions and propagate stellar parameters. | [Coulombe et al. 2023](https://doi.org/10.1038/s41586-023-06230-1) |
| WASP-19 b | How much can the current TESS baseline improve limits on tidal decay? | Fit individual transits in all sectors; compare linear and quadratic ephemerides; include time-correlated timing errors; calculate a period-derivative interval and lower bound on stellar tidal quality factor; check depth/activity correlations. | [Petrucci et al. 2020](https://arxiv.org/abs/1910.11930) |
| WASP-39 b | Are the CO2/SO2 conclusions stable across wavelength, terminator limb and model family? | Combine PRISM/G395H/MIRI public bins; run molecule-ablation comparisons with fitted offsets and correlated-noise sensitivity; compare morning/evening spectra; calculate scale heights and abundance claims only through cited retrievals. | [CO2 identification](https://doi.org/10.1038/s41586-022-05269-w); [MIRI SO2](https://doi.org/10.1038/s41586-024-07040-9) |
| WASP-43 b | What energy budget and circulation pattern are implied by the full phase-resolved spectrum? | Integrate spectra into orbital phase bins; calculate wavelength-dependent brightness temperatures, hotspot offsets and day/night flux ratio; derive recirculation and Bond-albedo grids; test nightside-cloud alternatives. | [Bell et al. 2024](https://doi.org/10.1038/s41550-024-02230-x) |
| WASP-69 b | Is the escaping atmosphere repeatable or controlled by stellar activity? | Retrieve helium time-series spectra; measure equivalent width and velocity asymmetry by epoch; correlate with activity indicators; calculate Roche geometry and mass-loss proxies; compare TESS depth/timing with activity state. | [Discovery](https://ui.adsabs.harvard.edu/abs/2014MNRAS.445.1114A/abstract) |
| WASP-80 b | Do transmission and emission spectra support one methane abundance and thermal structure? | Jointly compare transmission/emission methane and water templates; convert eclipse spectrum to brightness temperature; test chemical-equilibrium versus quenched-chemistry grids; propagate pipeline and stellar uncertainty. | [Bell et al. 2023](https://doi.org/10.1038/s41586-023-06687-0) |
| WASP-96 b | Which sodium/water features survive cross-instrument offsets and spectral binning? | Join VLT and JWST spectra with explicit instrument offsets; measure Na line wings and water-band amplitudes; test resolution and bin-edge sensitivity; compare cloudy/clear templates and report cross-validation residuals. | [Public supplementary products](https://doi.org/10.5281/zenodo.17065171) |

## Shared quantitative layer

The platform should compute the same auditable quantities for all 31 targets, where inputs exist:

- density and surface gravity from Monte Carlo mass/radius draws;
- atmospheric scale height under clearly labelled mean-molecular-weight assumptions;
- one-scale-height transmission amplitude;
- Jeans escape parameter and Roche-lobe filling factor;
- equilibrium-temperature variants for specified albedo and heat redistribution;
- transit ephemeris uncertainty at a future date;
- red-noise time-averaging factor and sector-to-sector depth heterogeneity;
- detection completeness over period–radius or period–depth space.

That shared table enables a publishable comparative question: **which physical regimes produce robust information in public TESS plus spectroscopy data, and which apparent conclusions are dominated by data reduction or model assumptions?**

## Recommended implementation order

1. **Timing pilot:** WASP-12 b, WASP-19 b and Kepler-51 b.
2. **Spectral robustness pilot:** K2-18 b, WASP-39 b, LHS 475 b and TRAPPIST-1 e.
3. **Energy-budget pilot:** 55 Cancri e, GJ 1214 b, WASP-18 b and WASP-43 b.
4. **Escape pilot:** HAT-P-11 b, GJ 3470 b, WASP-69 b and WASP-107 b.
5. Roll the validated analysis patterns into the remaining targets, retaining their different lead questions.

This ordering creates four strong scientific stories before any decision about 20 additional repositories.

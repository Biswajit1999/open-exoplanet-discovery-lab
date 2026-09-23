# Result Interpretation

## Measurement versus inference

A data point from an archive is a measurement. A corrected RV, fitted semi-amplitude, completeness limit, inferred activity coefficient, or extra-scatter term is a derived/model-dependent quantity.

The interface and reports keep those categories separate.

## RV periodicities

A strong periodogram peak means a periodic basis explains variance at that frequency under the chosen noise model. It does not by itself establish a planet.

Interpretation requires checking:
- sampling/window aliases;
- activity indicators;
- instrument eras;
- phase/coherence over time;
- wavelength dependence where available;
- model sensitivity;
- false-alarm calibration.

## Optical/NIR amplitude

An amplitude ratio near unity can support achromatic coherence but is not proof of a Keplerian origin. An amplitude ratio different from unity may be caused by activity, tellurics, line weighting, reduction differences, or evolving stellar surface structure.

The project therefore reports the ratio and its uncertainty rather than converting it into a categorical planet probability.

## Gaussian processes

A GP can model covariance but can also absorb coherent planetary power. Use is conditional on diagnostics, and the fitted planet amplitude must be compared with and without the GP.

## Completeness

A non-detection is meaningful only inside a measured sensitivity surface. Statements use forms such as:

"Under model M and the frozen recovery rule, 90% of injected signals with period P require K ≥ K90 for recovery."

Completeness from one noise model is not automatically transferable to another target or instrument.

## Atmospheric extra scatter

A positive extra-scatter estimate says independent measurements are more dispersed than their reported independent errors predict under the simple random-effects model. It does not identify the cause.

Potential causes include:
- visit-to-visit astrophysical variability;
- reduction choices;
- calibration differences;
- wavelength registration;
- stellar contamination;
- unmodelled covariance.

## Null results

Nulls are retained when they constrain a physically interpretable quantity. They are not hidden because a visual narrative is less dramatic.

## Literature values

Published values are labelled `literature` and linked to their source. They are never presented as measurements produced by this repository.

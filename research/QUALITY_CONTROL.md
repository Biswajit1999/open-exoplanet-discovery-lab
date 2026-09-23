# Quality-Control Contract

## General

No row is silently deleted. Rejected observations remain traceable with an explicit reason.

Mandatory checks:
- finite timestamp;
- explicit time scale;
- finite measurement;
- positive formal uncertainty when uncertainty is required;
- valid instrument and product identifier;
- duplicate-product/duplicate-epoch review;
- pipeline version when precision conclusions depend on it.

## RV-specific

Inspect:
- uncertainty distribution;
- high-leverage epochs;
- per-era offsets;
- repeated same-night measurements;
- instrument-upgrade boundaries;
- activity indicators;
- cadence/window function;
- obvious unit or barycentric-convention mismatches.

Outlier rejection must not be based only on residual size from the final desired model.

## NIRPS

Products in the documented DRS 3.2.6 precision-RV issue window are rejected for sub-10 m/s work unless a corrected DRS 3.2.7 product is verified.

## HARPS

Pre/post fibre-upgrade epochs are tagged. The analysis may fit separate offsets/jitters rather than merge them blindly.

## TESS

Preserve quality flags and state which flags are excluded. Candidate-level work inspects target-pixel/difference-image context when attribution to a source matters.

## Atmospheric spectra

Do not interpolate two spectra onto a common grid until native bin edges, units and covariance information have been inspected. Independent observations and alternate reductions receive different relationship labels.

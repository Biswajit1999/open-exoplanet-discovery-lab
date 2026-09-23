# Result Interpretation Rules

This repository separates measurements, statistical inferences and astrophysical interpretations.

## Allowed statement hierarchy

### Measurement
A value is directly reported by an archive product or publication-native table.

Example:
"The public table contains N accepted RV epochs under the frozen QC rule."

### Derived quantity
A deterministic transformation of measurements.

Example:
"The accepted epochs span X days."

### Fitted quantity
A parameter inferred under a declared model.

Example:
"Under the circular shared-period model, K = ..."

### Robustness statement
A conclusion supported by explicit alternative-model or held-out-data tests.

Example:
"The inferred K is stable to removal of the post-upgrade observing era within the stated uncertainty."

### Astrophysical interpretation
A physical explanation supported by the prior layers and relevant literature.

Example:
"The signal is more consistent with a wavelength-coherent Doppler reflex than with this tested activity model."

The project must not skip directly from a periodogram peak to the final layer.

## Language restrictions

Do not write:
- "planet detected" from GLS alone;
- "activity removed" because RMS decreased;
- "NIR confirms planet" solely because a NIR periodogram has a nearby peak;
- "atmospheric variability" when only reduction-to-reduction disagreement is measured;
- "no planet" when the injection/recovery completeness is poor;
- "first ever" without a dated literature audit.

Prefer:
- "candidate periodicity";
- "model-dependent RV component";
- "consistent/inconsistent within uncertainty";
- "empirical reproducibility scatter";
- "non-detection at quantified sensitivity".

## Null results

A null result is publishable-quality evidence when the analysis demonstrates that:
- the dataset had sensitivity to the effect;
- the null test was specified in advance;
- systematic alternatives were tested;
- the upper limit or completeness surface is reported.

## Precision

Round values according to the uncertainty and model fidelity. Archive timestamps and identifiers may retain machine precision for reproducibility, but prose should not imply unsupported physical precision.

# Literature and Novelty Gate

## Rule

The repository does not use "first", "novel", "new planet", or equivalent priority language merely because a calculation has not appeared in this codebase.

For each scientific claim, add a dated literature note with:
- ADS/SciX or publisher search terms;
- closest papers;
- datasets used by those papers;
- methods already attempted;
- exact incremental question here;
- conditions under which the claim would become non-novel.

## Current programme distinctions

### NETS III
The release paper already publishes the 41-star RV/activity dataset, zero-point discussion, RVSearch analysis, and sensitivity to known planets. This project therefore does not claim novelty for rerunning RVSearch or drawing periodograms.

The distinct test is the sensitivity of completeness and signal recovery to explicitly alternative instrument/activity noise models and held-out-era checks.

### NIRPS × HARPS
Optical/NIR activity discrimination has substantial prior literature across HARPS, CARMENES, SPIRou, HPF and other instruments. The project therefore avoids a generic claim that "NIR separates planets from activity."

The intended contribution is a reproducible public-archive NIRPS/HARPS overlap census plus target-controlled coherence tests with NIRPS reduction provenance encoded explicitly. A target is excluded from novelty claims when substantially equivalent joint analysis already exists.

### SPORES-HWO II
The release already performs a 35-year RVSearch companion/sensitivity analysis. The extension is not another blind search; it is robustness of the published sensitivity boundary to eccentricity, correlated noise and instrument removal.

### Atmospheric spectroscopy
The NASA Exoplanet Archive aggregates published spectra and the Rocky Worlds HLSP contains repeated products. The project does not claim novelty for plotting those spectra.

The analysis target is an empirical repeatability/reproducibility floor with independent observations distinguished from alternate reductions.

## Claim labels

Every result should carry one label:
- REPRODUCTION — confirms a published calculation;
- ROBUSTNESS TEST — changes assumptions around a published result;
- CROSS-ARCHIVE TEST — uses independent data to test a claim;
- METHOD VALIDATION — synthetic or benchmark validation;
- EXPLORATORY — hypothesis-generating only;
- CANDIDATE FOLLOW-UP — requires independent validation;
- SCIENTIFIC RESULT — passed the relevant validation gate.

# Instrument and Reduction Systematics Register

## NEID

The NETS III release explicitly discusses RV zero-point changes, including a post-Contreras-fire offset and a previously unidentified 2021 offset. The analysis therefore treats observing era as a first-class factor and evaluates whether a single-offset model leaves structured residuals.

Required fields:
- BJD/time standard;
- RV and uncertainty;
- observing run/era when available;
- activity indicators;
- any quality flag supplied by the public table.

## NIRPS

The ESO NIRPS Phase-3 release is an open stream and therefore mutable over time.

Critical exclusion:
ESO documented an RV accuracy problem for NIRPS observations from 2025-04-01 12:00 to 2025-07-24 12:00 reduced with DRS 3.2.6. Precision analyses better than 10 m/s must use corrected products reprocessed with DRS 3.2.7 or exclude the affected data.

Record:
- PROCSOFT/DRS version;
- HA/HE mode;
- mask/template;
- telluric correction state;
- calibration/fibre-B configuration where available;
- product identifier and checksum.

## HARPS

Track:
- pre/post fibre-upgrade era;
- reduction/pipeline family;
- zero-point treatment;
- spectral mask/template;
- activity indicators;
- duplicated/reprocessed products.

Optical/NIR comparisons must not attribute an instrumental step to chromatic stellar physics.

## TESS

Track:
- sector;
- cadence/product type;
- SPOC/TESS-SPOC/QLP or other provenance;
- data release/reprocessing state;
- quality-bit handling;
- crowding/contamination diagnostics.

Sector 107 is treated as an evolving release until the required products are complete.

## JWST / HST atmospheric products

Track:
- programme/visit;
- instrument/mode;
- reduction source;
- whether two spectra are independent observations or alternate reductions;
- wavelength binning;
- reported covariance availability;
- source publication.

A cross-study residual is not automatically an atmospheric-variability measurement.

## Gaia

Current analyses use public Gaia products only.

Gaia DR4 remains a versioned future adapter. The final schema and public release state are verified at the time of integration rather than assumed in advance.

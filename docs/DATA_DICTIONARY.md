# Data Dictionary

## Observation identity

| Field | Meaning |
|---|---|
| `target_id` | Stable project identifier |
| `canonical_name` | Preferred astrophysical name |
| `gaia_dr3_source_id` | Gaia DR3 identifier when unambiguous |
| `archive` | Source archive |
| `collection` | Survey / HLSP / Phase-3 collection |
| `instrument` | Instrument name |
| `mode` | Instrument observing mode |
| `product_id` | Archive-native product identifier |
| `provenance_id` | Project lineage identifier |

## Time

| Field | Meaning |
|---|---|
| `observation_time` | Numeric epoch in the stated time system |
| `time_scale` | UTC, TDB, TT, etc. |
| `time_format` | BJD, MJD, JD, ISO |
| `exposure_time_s` | Exposure duration in seconds |

Never compare timestamps across archives before normalising both format and scale.

## Radial velocity

| Field | Meaning |
|---|---|
| `rv_mps` | Radial velocity in m/s |
| `rv_error_mps` | Quoted formal uncertainty |
| `rv_zero_point` | Applied or fitted zero-point term |
| `jitter_mps` | Additional white-noise term |
| `barycentric_convention` | Recorded convention/source where available |
| `pipeline_version` | Reduction software / PROCSOFT |
| `instrument_era` | Hardware/reduction era label |

## Activity / line-shape indicators

The project stores indicators without assuming causality. Examples include:
- BIS / BIS span;
- FWHM;
- chromospheric indices;
- differential line width;
- chromatic index;
- equivalent-width proxies.

Each indicator carries its original units and source pipeline.

## Period search

| Field | Meaning |
|---|---|
| `period_days` | Trial or fitted period |
| `power` | Periodogram statistic |
| `fap` | False-alarm probability with method recorded |
| `window_power` | Spectral-window power |
| `alias_class` | Exact, harmonic, alias, or unresolved |

## Keplerian parameters

Use:
- (P): period;
- (K): stellar RV semi-amplitude;
- (e): eccentricity;
- (omega): argument of periastron;
- (T_p): periastron epoch;
- (gamma_j): instrument/era offset;
- (sigma_{m jit,j}): instrument/era jitter.

Units and reference epoch must accompany every stored fit.

## Injection/recovery

Every injection record includes:
- target;
- period;
- semi-amplitude or transit depth/radius;
- phase;
- eccentricity;
- noise model;
- instrument subset;
- seed;
- detected period;
- FAP;
- recovery classification.

## Optical/NIR comparison

Derived fields:
- `k_optical_mps`;
- `k_nir_mps`;
- `k_ratio_nir_optical`;
- `phase_delta_rad`;
- matched epoch counts at 1 h, 6 h, 1 d, 3 d, 7 d;
- activity-coherence metadata.

No scalar "planet score" is defined.

## Atmospheric spectroscopy

Spectrum-level metadata follow the NASA Exoplanet Archive `spectra` table:
- `pl_name`;
- `spec_type`;
- `bibcode`;
- `authors`;
- `num_datapoints`;
- `instrument`;
- `facility`;
- `minwavelng`;
- `maxwavelng`;
- `mintranmid`;
- `maxtranmid`;
- `note`;
- `spec_path`.

Point-level transmission/eclipse/direct-imaging data retain the units defined by their source products/publications.

## Result state

Every web/report value is explicitly one of:
- measured;
- derived;
- fitted;
- simulated;
- literature;
- provisional.

A visual component may not remove that state label.

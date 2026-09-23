# Data Dictionary

## Observation identity

target_id
: Stable project target identifier.

canonical_name
: Preferred astronomical target name after identity resolution.

archive
: Originating public archive.

collection
: Archive collection or catalogue identifier.

instrument
: Instrument that produced the observation.

mode
: Instrument configuration when relevant.

product_id
: Archive product identifier.

## Time

observation_time
: Numeric observation epoch.

time_scale
: Explicit scale/system, e.g. BJD_TDB. Never inferred silently.

## Measurement

observable
: RV, activity index, flux, eclipse depth, spectral bin or other measured quantity.

value
: Numeric measurement.

uncertainty
: Reported 1-sigma uncertainty unless the source defines otherwise.

unit
: Physical unit string.

## Reduction provenance

pipeline_version
: Reduction software identifier/version.

quality_state
: Accepted, rejected or review.

quality_reason
: Machine-readable reason when not accepted.

source_reference
: DOI, bibcode or archive documentation link.

provenance_id
: Link to the frozen acquisition manifest.

## Derived-product provenance

method_version
: Analysis method/configuration version.

configuration_hash
: Hash of analysis configuration.

input_manifest_hash
: Hash of the source manifest.

software_commit
: Git commit used to generate the output.

output_checksum
: SHA-256 of the generated file.

## Result status

measurement
: Direct archive-reported quantity.

fitted
: Inferred by a declared statistical model.

derived
: Deterministic transformation of measurements.

simulated
: Synthetic/injected quantity.

literature
: Value reported by an external publication.

provisional
: Analysis has not completed the stated validation gate.

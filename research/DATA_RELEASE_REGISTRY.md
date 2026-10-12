# 2026 Data Release Registry

Access-state reference date: **2026-10-12**.

This file records the public datasets that anchor the flagship research programme. It is not a substitute for a frozen machine-readable manifest. Every actual analysis release must create a dated manifest from archive queries and checksums.

## 1. NEID Earth Twin Survey III

Role: core extreme-precision RV benchmark.

Primary science release:
- The NEID Earth Twin Survey. III. Survey Performance After Three Years on Sky
- https://arxiv.org/abs/2506.23704

Verified headline properties from the release:
- 41 bright nearby main-sequence stars;
- public RV measurements and stellar activity indicators;
- documented zero-point behaviour including a post-Contreras-fire offset and an additional 2021 offset;
- published RVSearch sensitivity analysis.

Project use:
- reproduce basic survey diagnostics;
- explicitly encode instrumental eras;
- compare baseline and correlated/activity-aware recovery models;
- quantify changes in completeness rather than repeat the published search.

Status: **READY FOR M0/M1**.

## 2. ESO NIRPS Phase-3 stream

Role: near-infrared RV and chromatic-coherence work.

Official release:
- DOI: https://doi.org/10.18727/archive/92
- ESO science-archive release description: https://www.eso.org/rm/api/v1/public/releaseDescriptions/233

Verified release characteristics:
- open stream beginning with operations on 2023-04-01;
- both HA and HE modes;
- reduced spectra in FITS;
- automatic DRS products;
- wavelength coverage approximately 970–1850 nm;
- cross-correlation RV products included;
- dynamic dataset that grows with time.

Critical precision-RV issue:
- https://archive.eso.org/cms/eso-archive-news/issue-on-reduced-nirps-data.html

ESO states that observations between 2025-04-01 12:00 and 2025-07-24 12:00 reduced with DRS 3.2.6 were affected by an RV-accuracy issue. For science requiring precision better than 10 m/s those products should not be used. Updated Phase-3 products were reprocessed with DRS 3.2.7; PROCSOFT must be checked.

Project use:
- build public NIRPS target census;
- crossmatch to HARPS;
- quantify exact time overlap;
- construct optical/NIR coherence controls;
- preserve DRS version in every observation record.

Status: **READY FOR CENSUS; TARGET SAMPLE MUST BE FROZEN BEFORE SCIENCE FITS**.

## 3. HARPS public archive

Role: optical comparison layer for NIRPS targets and selected long-baseline systems.

Archive:
- ESO Science Archive: https://archive.eso.org/
- Science Portal: https://archive.eso.org/scienceportal/home

Project use:
- optical RV comparison;
- activity indicators where available;
- instrument-era and fibre-upgrade bookkeeping;
- overlap and near-simultaneity calculations with NIRPS.

Gate:
No target enters WP2 until public HARPS epoch counts, baselines, and time-overlap metrics are reproduced from archive queries.

Status: **READY FOR CENSUS**.

## 4. SPORES-HWO II

Role: long-baseline heterogeneous-RV robustness experiment.

VizieR catalogue:
- J/AJ/170/343
- https://cdsarc.cds.unistra.fr/viz-bin/w/VizieR-3?-source=J%2FAJ%2F170%2F343

Catalogue description:
- 35 years of RV information for 141 stars.

Verified public access on 2026-10-12:
- 141 target rows;
- 153,902 raw RV rows;
- 109 catalogued-signal rows;
- 74 trend rows;
- 120 habitable-zone sensitivity rows;
- 28 instrument rows;
- catalogue licence CC-BY-4.0.

The frozen acquisition also queried the NASA Exoplanet Archive
`pscomppars` table for confirmed-planet context linked by HD identifier. The
VizieR and NASA queries, exact row counts, file checksums and access time are
recorded under manifest hash
`07ac357428da385a0a6aa5b7fd72cb51a7f6bcf5520d0f946b86dbec6d8a99f3`.

Primary extension:
- eccentric injection distribution;
- correlated stellar noise;
- leave-one-instrument-out sensitivity;
- revised M50/M90 or K50/K90 where meaningful.

Status: **READY; PUBLIC TABLES VERIFIED AND FROZEN FOR ANALYSIS**.

## 4a. TESS Stellar Variability Catalog v1.0

Role: independent short-timescale photometric-variability context for
SPORES-HWO targets.

MAST HLSP:
- https://archive.stsci.edu/hlsp/tess-svc
- DOI: https://doi.org/10.17909/f8pz-vj63

Verified public access on 2026-10-12:
- 84,046 stars classified as significantly periodic-variable on 0.01–13 d
  timescales;
- TESS Prime Mission sectors 1–26;
- one selected 2-minute-cadence sector per star;
- catalogue licence CC-BY-4.0.

Project use:
- resolve SPORES-HWO stars to TIC identifiers through SIMBAD;
- join by exact TIC identifier;
- retain catalogue solution, period, amplitude, power and sector as context;
- never interpret a match automatically as rotation or a planet;
- never interpret a non-match as evidence that a star is quiet.

Status: **READY; VERSION 1.0 FROZEN WITH SOURCE CHECKSUM**.

## 5. TESS Sector 106 / Sector 107

Role: stellar rotation/activity context, transit context, and temporal validation.

MAST holdings:
- https://outerspace.stsci.edu/spaces/TESS/pages/35094700/TESS%2BHoldings%2BAvailable%2Bby%2BMAST%2BService

Sector 107 observing page:
- https://tess.mit.edu/observations/sector-107/

Verified archive state on 2026-09-23:
- MAST is ingesting TESS FFIs on a roughly weekly basis;
- FFI delivery precedes TP/LC/DV ingest for a sector;
- Sector 107 material is still in an evolving release state.

Project use:
- use Sector 106 as a more mature control;
- measure how signal metrics and transit parameters evolve as a sector becomes complete;
- provide rotation/activity constraints to RV targets when scientifically justified.

Status:
- Sector 106: **CONTROL / READY**
- Sector 107: **ACTIVE INGEST; VERSION EVERY QUERY**

## 6. Rocky Worlds DDT HLSP

Role: repeated-eclipse and stellar-UV reproducibility layer.

MAST HLSP:
- https://archive.stsci.edu/hlsp/rocky-worlds
- DOI: https://doi.org/10.17909/qsyr-ny68

Verified archive state:
- first released 2025-09-17;
- updated repeatedly through 2026;
- GJ 3929 b has four released JWST eclipses plus combined/checkpoint products;
- TOI-771 b has multiple released eclipses;
- LHS 1140 b eclipse 1 released 2026-09-04;
- HST host-star products are also being updated.

Project use:
- repeated-measurement variance;
- reduction-method sensitivity;
- hierarchical between-visit uncertainty;
- host-star UV/activity context.

Guardrail:
Do not present a simple re-reduction of one already-studied target as a new result.

Status: **READY; ACTIVE STREAM REQUIRES VERSIONED MANIFESTS**.

## 7. NASA Exoplanet Archive Atmospheric Spectroscopy

Role: cross-study and cross-instrument spectral reproducibility.

Archive:
- https://exoplanetarchive.ipac.caltech.edu/
- atmosphere documentation: https://exoplanetarchive.ipac.caltech.edu/docs/atmospheres/atmospheres_work.html
- 2026 archive news: https://exoplanetarchive.ipac.caltech.edu/docs/exonews_archive.html

Verified 2026 growth:
- 2026-07-02 archive update added 48 spectra across 21 planets;
- the archive includes transmission, eclipse/emission, and direct-imaging spectra from the literature.

Project use:
- identify planets with independent repeated spectra;
- distinguish separate observations from alternative reductions of the same photons;
- estimate an empirical inter-study or inter-reduction variance term;
- link every spectrum to its original paper.

Status: **READY**.

## 8. Gaia

Current role:
- source identity;
- parallax/distance;
- stellar context;
- currently public astrometric products.

Frozen 2026-09-24 identity product:
- all 41 NETS III survey targets have one exact SIMBAD-linked Gaia DR3 source ID;
- the exact-source Gaia ADQL returns 41 distinct DR3 rows;
- target-table checksum, uploaded target list, query hashes and output checksums are retained in `results/gaia_dr3_identity_2026-09-24/`;
- Gaia astrometric quality fields are context only and are not companion classifications.

Future role:
Gaia DR4 may enable richer orbit constraints and epoch-level astrometry, but no current analysis will assume DR4 products before they are public and the schema is verified.

Official information:
- https://www.cosmos.esa.int/web/gaia/dr4
- https://www.cosmos.esa.int/web/gaia/data-release-4

Status:
- DR3/current public products: **READY**
- DR4: **FUTURE ADAPTER ONLY**

---

# Archive-status rules

Every source has one of four states:

- READY — public and suitable for immediate scripted acquisition;
- CENSUS — public, but the scientifically useful sample is not yet frozen;
- ACTIVE — public but still growing/reprocessing; every analysis requires a dated manifest;
- WAIT — announced/indexed but required products are not yet verified as publicly accessible.

No work package may silently promote a source from ACTIVE or WAIT to READY. The status change must be committed with the evidence link and date.

# Data storage rule

The repository stores:
- manifests;
- queries;
- checksums;
- compact derived tables where licensing permits;
- metadata;
- analysis outputs.

The repository does not automatically mirror:
- large raw FITS collections;
- third-party files with unclear redistribution rights;
- mutable archive payloads without a source identifier.

# Versioning rule

Every published analysis must be able to answer:

1. Which archive state was used?
2. On what date was it queried?
3. Which product IDs were returned?
4. Which products were rejected?
5. Which pipeline versions produced the accepted data?
6. What checksum identifies each local input?

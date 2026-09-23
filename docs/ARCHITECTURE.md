# Software Architecture

## Design

The codebase has four layers.

### Acquisition
Public archive clients fetch metadata and products without scientific filtering.

Modules:
- exolab.vizier
- exolab.tap
- exolab.eso
- exolab.archives

### Provenance and contracts
Every acquired or derived product receives deterministic lineage.

Modules:
- exolab.provenance
- exolab.registry
- JSON schemas under schemas/

### Science
Small numerical primitives support transparent validation before heavier inference frameworks are introduced.

Modules:
- exolab.rv
- exolab.periodogram
- exolab.chromatic
- exolab.completeness
- exolab.atmosphere
- exolab.validation
- existing transit search/vetting modules

### Presentation
Static paper outputs are canonical. The React/Motion web application consumes versioned exports and does not become the source of publication calculations.

## Dependency rule

Archive clients may depend on pandas and the standard library.
Core science may depend on NumPy/SciPy/Astropy.
The web application may not reimplement scientific fitting logic.

## Notebook rule

Notebooks are clients of the package. If a calculation is scientifically important, its implementation belongs in src/exolab with tests.

## Extension points

Full Keplerian MCMC/nested sampling, Gaussian processes and line-by-line spectroscopy are deliberately separate optional layers. They should be introduced only after the transparent baseline models pass validation.

# Open Exoplanet Discovery Lab

An open, Colab-ready laboratory for learning how transiting planets are found and for carrying out a reproducible first-pass search of public TESS data.

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Biswajit1999/open-exoplanet-discovery-lab/blob/main/notebooks/Open_Exoplanet_Discovery_Lab.ipynb)

> A dip in a light curve is **not automatically a planet**. This project finds and ranks signals. A credible planet claim also needs contamination checks, independent vetting, archive cross-matching, and usually follow-up observations.

## Two ways into the project

### Explorer mode

Imagine watching a lighthouse. If a tiny object repeatedly passes in front of its lamp, the light becomes slightly dimmer at regular times. TESS performs a related measurement for thousands of stars. In the notebook you will:

1. choose a public target;
2. download its brightness measurements;
3. remove slow instrumental and stellar trends;
4. search for repeating transit-shaped dips;
5. test whether the signal behaves more like a planet or a false positive;
6. hide artificial planets in the data to measure which ones the search could recover.

Start with [`notebooks/Open_Exoplanet_Discovery_Lab.ipynb`](notebooks/Open_Exoplanet_Discovery_Lab.ipynb) in Google Colab.

### Researcher mode

The package provides a transparent baseline pipeline rather than a black-box classifier:

- live NASA Exoplanet Archive TAP queries for confirmed planets and TOIs;
- MAST/Lightkurve access to SPOC and TESS-SPOC light curves;
- robust cleaning and time-scale-controlled detrending;
- Box Least Squares searches with explicit period and duration grids;
- odd/even, secondary-eclipse, transit-count and signal-to-noise diagnostics;
- injection–recovery experiments and harmonic-aware recovery rules;
- machine-readable candidate scorecards.

The repository deliberately does **not** assign a statistical validation probability. Packages such as `vespa` or `TRICERATOPS`, difference-image centroiding, high-resolution imaging and reconnaissance spectroscopy belong in later validation stages.

The synthetic regression test and a real-data recovery of the catalogued TOI-1204.01 signal are documented in [`research/VALIDATION.md`](research/VALIDATION.md).

## Why this is more useful than another periodogram repository

A periodogram answers “where is the strongest repeating box?” It does not answer “how many planets would this pipeline have missed?” or “could a background eclipsing binary produce this signal?” The lab therefore treats discovery as a sequence:

```text
archive census -> target selection -> light curve -> transit search
               -> automated vetting -> injection/recovery -> human review
               -> independent follow-up
```

Injection–recovery is essential: a non-detection is scientifically interpretable only after the search completeness is measured.

## Quick start

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -e .[tess,test]
pytest -q
```

Run a live archive census without downloading light curves:

```bash
python -m exolab.cli census
python -m exolab.cli candidates --limit 20 --max-tmag 11.5 --max-radius 4
```

Run the synthetic end-to-end demonstration:

```bash
python -m exolab.cli demo --output outputs/demo
```

## Candidate-search guardrails

- Prefer `PDCSAP_FLUX`, but inspect `SAP_FLUX`, quality flags and target pixels when a signal matters.
- Record the TESS sector and pipeline provenance; reprocessed sectors can produce different TCE sets.
- Reject or flag period harmonics, odd/even depth differences, secondary eclipses and too-few-transit events.
- Inspect difference images and nearby Gaia sources before attributing a dip to the intended star.
- Cross-match NASA Exoplanet Archive TOIs/TCEs, ExoFOP and SIMBAD before calling a signal new.
- Publish null results and completeness maps, not only attractive detections.
- Never describe a candidate as a planet without appropriate validation or confirmation.

## Public data foundations

- [NASA Exoplanet Archive TAP](https://exoplanetarchive.ipac.caltech.edu/docs/TAP/usingTAP.html) — confirmed planets and the live TOI table.
- [MAST TESScut API](https://mast.stsci.edu/tesscut/docs/) — cutouts from calibrated TESS full-frame images.
- [TESS data products](https://heasarc.gsfc.nasa.gov/docs/tess/data-products.html) — light curves, target pixels, FFIs and validation products.
- [Lightkurve transit-search tutorial](https://lightkurve.github.io/lightkurve/tutorials/3-science-examples/exoplanets-identifying-transiting-planet-signals.html) — an accessible BLS introduction.
- Hippke & Heller (2019), [Transit Least Squares](https://arxiv.org/abs/1901.02015) — a limb-darkened search algorithm and injection–recovery comparison.
- Jenkins et al. (2016), [TESS SPOC pipeline](https://heasarc.gsfc.nasa.gov/docs/tess/docs/jenkinsSPIE2016-copyright.pdf) — the mission pipeline and its validation diagnostics.

As of 16 August 2026, a live TAP census returned 6,336 confirmed planets, 8,113 TOI rows and 4,927 TOIs with the ExoFOP working-group disposition `PC`. Those counts are snapshots; the notebook queries them again each time it runs.

## Portfolio research programme

[`research/PORTFOLIO_DEEPENING_MATRIX.md`](research/PORTFOLIO_DEEPENING_MATRIX.md) maps each of the existing 31 exoplanet reports to a distinct quantitative extension. The shared comparison layer is intentional, but each target receives a different lead question.

Merged work and the exact cross-session handoff are tracked in
[`research/PORTFOLIO_PROGRESS.md`](research/PORTFOLIO_PROGRESS.md). Five target
upgrades are complete; LHS 475 b is the next recommended spectral-robustness
case.

## Citation and authorship

Developed by **Biswajit Jana** as an independent open-science project. Cite the archive products and papers associated with every dataset in addition to this software.

## License

MIT. Archive data retain their original acknowledgements and citation requirements.

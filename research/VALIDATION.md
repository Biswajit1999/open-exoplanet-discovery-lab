# Validation record

## Synthetic regression test

The deterministic training light curve contains a 0.4% box transit at 3.2 days with a two-hour duration. The automated test requires:

- recovered period within 1%;
- depth signal-to-noise greater than 7;
- at least eight observed transit events;
- no odd/even-depth or secondary-eclipse flag.

This test runs in CI on Python 3.10 and 3.12.

## Live public-data smoke test

Run on 16 August 2026 using the current NASA Exoplanet Archive TOI table and two SPOC light curves from MAST:

| Item | Result |
|---|---:|
| Archive object | TOI-1204.01 / TIC 467666275 |
| ExoFOP working-group disposition | PC (planet candidate) |
| Archive period | 1.3812115 d |
| Independently recovered BLS period | 1.38100696 d |
| Relative period difference | 0.0148% |
| Fitted depth | 90.1 ppm |
| Depth signal-to-noise | 12.17 |
| Transit events in downloaded baseline | 39 |
| Odd/even discrepancy | 0.80σ |
| Phase-0.5 secondary | 1.49σ |
| Automated warning flags | none |

This is a recovery of an already catalogued candidate signal. It is **not a new candidate and not a planet confirmation**. Its role is to verify that the archive query, MAST download, cleaning, search and diagnostic stages work together on real public data.

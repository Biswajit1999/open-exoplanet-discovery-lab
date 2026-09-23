# Contributing

Contributions are welcome when they improve reproducibility, scientific validation, archive access, statistics, documentation or accessibility.

## Scientific changes

A pull request changing a scientific result should include:
- source/manifests affected;
- physical motivation;
- model/configuration change;
- tests;
- comparison with previous output;
- literature impact if interpretation changes.

## Data changes

Do not commit:
- private observations;
- access credentials;
- very large raw archive products without a clear reason;
- data with unclear redistribution rights.

Prefer archive download scripts plus checksums.

## Code changes

Requirements:
- deterministic tests where feasible;
- units and time systems explicit;
- no hidden filtering;
- no silent NaN dropping in headline analyses;
- public functions documented;
- notebooks should call package code rather than duplicate it.

## Claims

Do not add "first", "new discovery", "confirmed", or equivalent language without the evidence required by the literature/validation protocol.

## Web changes

Scientific meaning takes priority over animation. All interactive plots need units, uncertainty context, keyboard accessibility and reduced-motion behaviour.

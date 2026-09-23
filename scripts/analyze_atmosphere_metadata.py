"""Audit repeated atmospheric spectroscopy represented in NEA spectrum metadata."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input",
        default="outputs/public_snapshot/nea_atmospheric_spectra_metadata.csv",
    )
    parser.add_argument("--output", default="outputs/atmosphere_audit")
    args = parser.parse_args()
    source = Path(args.input)
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)

    frame = pd.read_csv(source)
    required = {"pl_name", "spec_type", "bibcode", "instrument", "facility", "spec_path"}
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"atmospheric metadata missing columns {sorted(missing)}")

    grouped = (
        frame.groupby("pl_name", dropna=True)
        .agg(
            n_spectra=("spec_path", "nunique"),
            n_publications=("bibcode", "nunique"),
            n_instruments=("instrument", "nunique"),
            n_facilities=("facility", "nunique"),
            n_types=("spec_type", "nunique"),
        )
        .reset_index()
        .sort_values(["n_spectra", "n_publications"], ascending=False)
    )
    grouped["multi_spectrum"] = grouped["n_spectra"] >= 2
    grouped["multi_publication"] = grouped["n_publications"] >= 2
    grouped["cross_instrument"] = grouped["n_instruments"] >= 2
    grouped.to_csv(output / "atmospheric_reproducibility_candidates.csv", index=False)

    publication_instrument = (
        frame.groupby(["pl_name", "bibcode", "instrument", "facility", "spec_type"], dropna=False)
        .agg(n_spectra=("spec_path", "nunique"))
        .reset_index()
        .sort_values(["pl_name", "n_spectra"], ascending=[True, False])
    )
    publication_instrument.to_csv(
        output / "atmospheric_publication_instrument_matrix.csv",
        index=False,
    )

    summary = {
        "spectrum_metadata_rows": int(len(frame)),
        "unique_planets": int(frame["pl_name"].nunique(dropna=True)),
        "planets_with_multiple_spectra": int(grouped["multi_spectrum"].sum()),
        "planets_with_multiple_publications": int(grouped["multi_publication"].sum()),
        "planets_with_multiple_instruments": int(grouped["cross_instrument"].sum()),
        "interpretation": (
            "Multiplicity identifies candidates for a detailed reproducibility study. "
            "It does not establish independence because alternative reductions of the "
            "same observations can appear as separate spectrum records."
        ),
    }
    (output / "atmosphere_audit_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Summarize exact-TIC TESS-SVC context for the SPORES-HWO control sample.

This is a descriptive cross-archive linkage.  TESS-SVC membership is not a
rotation or planet label, and absence from TESS-SVC is not a null detection.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from exolab.provenance import canonical_json_sha256, sha256_file


def normalized_target(value: object) -> str:
    """Normalize CSV target identifiers without changing component suffixes."""
    text = str(value).strip()
    return text[:-2] if text.endswith(".0") else text


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--robustness", default="results/spores_hwo_robustness_2026-10-12"
    )
    parser.add_argument(
        "--tess-context", default="results/spores_tess_svc_context_2026-10-12"
    )
    parser.add_argument("--output", default="outputs/spores_tess_synthesis")
    parser.add_argument("--software-commit", default="working-tree")
    args = parser.parse_args()

    robustness = Path(args.robustness)
    tess_context = Path(args.tess_context)
    output = Path(args.output)
    figures = output / "figures"
    figures.mkdir(parents=True, exist_ok=True)

    sample = pd.read_csv(robustness / "analysis_sample.csv")
    thresholds = pd.read_csv(robustness / "target_k50_k90.csv")
    context = pd.read_csv(tess_context / "spores_tess_svc_context.csv")
    sample["target"] = sample["target"].map(normalized_target)
    thresholds["target"] = thresholds["target"].map(normalized_target)
    context["target"] = context["target"].map(normalized_target)

    included = sample[sample["selection_status"] == "included"].copy()
    reference = thresholds[
        thresholds["model"] == "instrument_correlated_circular"
    ][
        [
            "target",
            "k50_mps",
            "k90_mps",
            "k50_status",
            "k90_status",
            "residual_rms_mps",
        ]
    ]
    joined = included.merge(reference, on="target", validate="one_to_one").merge(
        context,
        on="target",
        how="left",
        validate="one_to_one",
        suffixes=("_robustness", "_tess"),
    )
    if len(joined) != len(included) or joined["context_state"].isna().any():
        raise RuntimeError("TESS context does not resolve every selected control target")
    joined.to_csv(output / "control_sample_tess_context.csv", index=False)

    full_counts = context["context_state"].value_counts().sort_index().to_dict()
    control_counts = joined["context_state"].value_counts().sort_index().to_dict()
    matched = joined[joined["context_state"] == "tess_svc_variability_match"].copy()
    unmatched = joined[joined["context_state"] != "tess_svc_variability_match"].copy()
    resolved_controls = int((joined["context_state"] != "no_tic_identifier").sum())

    configuration = {
        "identity_match": "exact TIC identifier from SIMBAD identifier list",
        "spores_selection": "analysis_sample.selection_status == included",
        "rv_reference_model": "instrument_correlated_circular",
        "tess_scope": "TESS-SVC v1.0; one selected Prime-Mission sector; 0.01-13 d",
    }
    summary = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "software_commit": args.software_commit,
        "configuration_hash": canonical_json_sha256(configuration),
        "spores_catalog_targets": int(len(context)),
        "full_sample_context_counts": {key: int(value) for key, value in full_counts.items()},
        "control_targets": int(len(joined)),
        "control_resolved_tic_ids": resolved_controls,
        "control_context_counts": {key: int(value) for key, value in control_counts.items()},
        "control_tess_svc_match_fraction_of_resolved": float(len(matched) / resolved_controls),
        "matched_control_targets": matched["target"].tolist(),
        "matched_solution_counts": {
            key: int(value)
            for key, value in matched["Solution"].value_counts().sort_index().to_dict().items()
        },
        "matched_variability_period_days": {
            "minimum": float(matched["period_var_1"].min()),
            "median": float(matched["period_var_1"].median()),
            "maximum": float(matched["period_var_1"].max()),
        },
        "matched_variability_amplitude_ppm": {
            "minimum": float(matched["amp_var_1"].min()),
            "median": float(matched["amp_var_1"].median()),
            "maximum": float(matched["amp_var_1"].max()),
        },
        "reference_k50_mps_by_context": {
            "tess_svc_match_median": float(matched["k50_mps"].median()),
            "other_context_median": float(unmatched["k50_mps"].median()),
        },
        "source_checksums": {
            "analysis_sample": sha256_file(robustness / "analysis_sample.csv"),
            "target_k50_k90": sha256_file(robustness / "target_k50_k90.csv"),
            "spores_tess_svc_context": sha256_file(
                tess_context / "spores_tess_svc_context.csv"
            ),
        },
        "interpretation": (
            "Exact cross-archive variability context only. TESS-SVC membership does not "
            "identify rotation or planets, and a non-match is not evidence of quietness. "
            "The matched/unmatched K50 medians are descriptive and not a causal test."
        ),
    }
    (output / "analysis_configuration.json").write_text(
        json.dumps(configuration, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (output / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    figure, axes = plt.subplots(1, 2, figsize=(10.8, 4.8))
    state_order = [
        "tess_svc_variability_match",
        "no_tess_svc_variability_match",
        "no_tic_identifier",
    ]
    labels = ["TESS-SVC match", "No catalogue match", "No TIC identity"]
    values = [int(full_counts.get(state, 0)) for state in state_order]
    axes[0].barh(labels, values, color=["#0b7785", "#9aa6a6", "#bd7067"])
    for index, value in enumerate(values):
        axes[0].text(value + 1.0, index, str(value), va="center")
    axes[0].set(
        xlabel="SPORES-HWO target rows",
        title="Exact-TIC context across 141 targets",
    )
    axes[0].grid(alpha=0.2, axis="x")

    plot = matched.sort_values("period_var_1")
    sizes = 32 + 90 * np.sqrt(plot["amp_var_1"] / plot["amp_var_1"].max())
    axes[1].scatter(
        plot["period_var_1"],
        plot["amp_var_1"],
        s=sizes,
        color="#d08b2e",
        edgecolor="white",
        linewidth=0.8,
    )
    for row in plot.itertuples():
        axes[1].annotate(
            str(row.target),
            (float(row.period_var_1), float(row.amp_var_1)),
            xytext=(5, 5),
            textcoords="offset points",
            fontsize=8,
        )
    axes[1].set(
        xlabel="TESS-SVC variability period [d]",
        ylabel="Fitted variability amplitude [ppm]",
        yscale="log",
        title="Five matches in the 26-star RV control sample",
    )
    axes[1].grid(alpha=0.2, which="both")
    figure.suptitle("SPORES-HWO × MAST variability context", fontsize=14)
    figure.tight_layout()
    figure.savefig(figures / "spores_tess_variability_context.png", dpi=220)
    plt.close(figure)

    checksums = {
        path.relative_to(output).as_posix(): sha256_file(path)
        for path in sorted(output.rglob("*"))
        if path.is_file() and path.name != "checksums.json"
    }
    (output / "checksums.json").write_text(
        json.dumps(checksums, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

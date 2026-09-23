import numpy as np
import pandas as pd

from exolab.nets import (
    completeness_contours,
    fit_group_jitters,
    project_nuisance,
    projected_signal_transfer,
)


def test_nuisance_projection_removes_offsets_and_activity():
    time = np.linspace(0, 20, 80)
    groups = np.where(np.arange(80) < 40, "A", "B")
    activity = np.sin(time / 4)
    errors = np.full(80, 0.2)
    values = np.where(groups == "A", 3.0, -2.0) + 1.5 * activity
    projected = project_nuisance(
        values, errors, groups=groups, activity=activity
    )
    assert np.std(projected.residuals) < 1e-10


def test_group_jitter_and_transfer_are_finite():
    rng = np.random.default_rng(3)
    time = np.linspace(0, 100, 100)
    groups = np.where(np.arange(100) < 50, "A", "B")
    errors = np.full(100, 0.2)
    residuals = rng.normal(0, np.where(groups == "A", 0.5, 1.0))
    jitters = fit_group_jitters(residuals, errors, groups)
    assert set(jitters) == {"A", "B"}
    assert jitters["B"] > jitters["A"]
    ratio = projected_signal_transfer(
        time, errors, 12.0, [0.0, 1.0], groups=groups
    )
    assert np.isfinite(ratio).all()


def test_completeness_contours_interpolate_thresholds():
    table = pd.DataFrame(
        {
            "period": [10, 10, 10, 20, 20, 20],
            "semi_amplitude": [1, 2, 3, 1, 2, 3],
            "completeness": [0.2, 0.6, 1.0, 0.0, 0.5, 0.8],
        }
    )
    contours = completeness_contours(table)
    assert np.isclose(contours.loc[0, "k50"], 1.75)
    assert np.isclose(contours.loc[0, "k90"], 2.75)
    assert np.isnan(contours.loc[1, "k90"])

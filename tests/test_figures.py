import matplotlib
matplotlib.use("Agg")

import numpy as np
import pandas as pd

from exolab.figures import (
    plot_chromatic_amplitudes,
    plot_completeness,
    plot_periodogram,
    plot_repeatability,
    plot_rv_timeseries,
)


def test_figure_helpers_write_files(tmp_path):
    t = np.linspace(0, 10, 20)
    rv = np.sin(t)
    err = np.full(20, 0.1)
    paths = [
        tmp_path / "rv.png",
        tmp_path / "periodogram.png",
        tmp_path / "completeness.png",
        tmp_path / "chromatic.png",
        tmp_path / "repeatability.png",
    ]
    plot_rv_timeseries(t, rv, err, path=paths[0])
    plot_periodogram(np.logspace(0, 2, 30), np.linspace(0, 1, 30), best_period=10, path=paths[1])
    table = pd.DataFrame({
        "period": [2, 5, 2, 5],
        "semi_amplitude": [1, 1, 2, 2],
        "completeness": [0.1, 0.2, 0.8, 0.9],
    })
    plot_completeness(table, path=paths[2])
    plot_chromatic_amplitudes(["A", "B"], [2, 3], [0.2, 0.2], [1.8, 3.1], [0.3, 0.3], path=paths[3])
    plot_repeatability(["v1", "v2"], [100, 103], [1, 1], mean=101.5, extra_scatter=1.0, path=paths[4])
    assert all(path.exists() and path.stat().st_size > 0 for path in paths)

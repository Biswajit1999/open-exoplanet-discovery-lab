import json

import numpy as np
import pytest

from exolab.atmosphere import random_effects_mean
from exolab.chromatic import compare_bands, simultaneity_counts
from exolab.registry import load_registry, require_source


def test_random_effects_compatibility_surface():
    consistent = random_effects_mean(
        np.array([100.0, 100.05, 99.95, 100.02]), np.ones(4)
    )
    inconsistent = random_effects_mean(
        np.array([90.0, 110.0, 92.0, 108.0]), np.ones(4)
    )
    assert consistent.extra_sigma < 0.1
    assert abs(consistent.mean - 100.0) < 0.1
    assert inconsistent.extra_sigma > 5.0
    assert inconsistent.n == 4


def test_chromatic_compatibility_surface():
    t1 = np.linspace(0, 80, 100)
    t2 = np.linspace(0.3, 80.3, 95)
    period = 9.5
    amplitude = 1.8
    e1 = np.full_like(t1, 0.1)
    e2 = np.full_like(t2, 0.1)
    y1 = amplitude * np.sin(2 * np.pi * (t1 - np.median(t1)) / period + 0.4)
    y2 = amplitude * np.sin(2 * np.pi * (t2 - np.median(t2)) / period + 0.4)
    result = compare_bands(t1, y1, e1, t2, y2, e2, period=period)
    assert abs(result.amplitude_ratio - 1.0) < 1e-6

    counts = simultaneity_counts(
        np.array([1.0, 2.0, 3.0]),
        np.array([1.02, 2.2, 4.0]),
        windows_hours=(1, 6, 24),
    )
    assert counts[1.0] <= counts[6.0] <= counts[24.0]


def test_registry_compatibility_surface(tmp_path):
    path = tmp_path / "registry.json"
    path.write_text(
        json.dumps(
            {
                "sources": [
                    {"id": "public", "name": "Public", "status": "ready"},
                    {"id": "future", "name": "Future", "status": "future"},
                ]
            }
        ),
        encoding="utf-8",
    )
    sources = load_registry(path)
    assert sources["public"].usable_now
    assert not sources["future"].usable_now
    assert require_source("public", path).id == "public"
    with pytest.raises(RuntimeError):
        require_source("future", path)

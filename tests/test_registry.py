import json

import pytest

from exolab.registry import load_registry, require_source


def test_repository_registry_loads_unique_sources():
    sources = load_registry()
    assert "nets3" in sources
    assert "nirps_phase3" in sources
    assert sources["nets3"].status == "ready"


def test_future_or_waiting_sources_are_gated():
    with pytest.raises(RuntimeError):
        require_source("spores_hwo_ii")
    with pytest.raises(RuntimeError):
        require_source("gaia_dr4")

import json

import pytest

from exolab.registry import load_registry, require_source


def test_repository_registry_loads_unique_sources():
    sources = load_registry()
    assert "nets3" in sources
    assert "nirps_phase3" in sources
    assert sources["nets3"].status == "ready"


def test_newly_public_sources_are_ready_and_future_sources_remain_gated():
    assert require_source("spores_hwo_ii").status == "ready"
    assert require_source("tess_svc_v1").status == "ready"
    with pytest.raises(RuntimeError):
        require_source("gaia_dr4")

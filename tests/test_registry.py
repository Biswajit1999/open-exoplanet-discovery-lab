import json

import pytest

from exolab.registry import load_registry, require_source


def test_registry_loads_and_blocks_future(tmp_path):
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

import pandas as pd
import pytest

from exolab.gaia import GaiaTapClient, extract_gaia_dr3_identifier


def test_extract_gaia_dr3_identifier_states():
    unique = extract_gaia_dr3_identifier(
        "HD 10700|Gaia DR2 2452378776434276992|Gaia DR3 2452378776434477184"
    )
    assert unique.source_id == "2452378776434477184"
    assert unique.count == 1
    assert unique.status == "unique"

    assert extract_gaia_dr3_identifier("HD 10700").status == "unmatched"
    ambiguous = extract_gaia_dr3_identifier("Gaia DR3 1|Gaia DR3 2")
    assert ambiguous.source_id is None
    assert ambiguous.count == 2
    assert ambiguous.status == "ambiguous"


def test_gaia_exact_source_query_is_deterministic_and_rejects_text():
    query = GaiaTapClient.exact_source_query(["20", "10", "20"])
    assert "gaiadr3.gaia_source" in query
    assert "source_id in (10,20)" in query
    with pytest.raises(ValueError):
        GaiaTapClient.exact_source_query(["10 OR 1=1"])


def test_gaia_client_preserves_source_ids(monkeypatch):
    payload = (
        ",".join(GaiaTapClient.columns)
        + "\n2452378776434477184,2016.0,26.0,0.1,-15.9,0.1,273.8,0.1,"
        "-1721.7,0.1,855.0,0.1,2.63,false,3.5,0.7,,\n"
    )

    class Response:
        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

        def read(self):
            return payload.encode()

    monkeypatch.setattr("exolab.gaia.urlopen", lambda *_args, **_kwargs: Response())
    frame, query = GaiaTapClient().query_source_ids(["2452378776434477184"])
    assert isinstance(frame, pd.DataFrame)
    assert frame.loc[0, "source_id"] == "2452378776434477184"
    assert "2452378776434477184" in query

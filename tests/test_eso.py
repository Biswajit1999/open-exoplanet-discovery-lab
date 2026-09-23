from exolab.eso import instrument_inventory_query, target_instrument_query


def test_inventory_query_targets_public_instrument_products():
    query = " ".join(instrument_inventory_query("NIRPS").split())
    assert "instrument_name = 'NIRPS'" in query
    assert "data_rights = 'public'" in query
    assert "dp_id" in query


def test_cone_query_has_instrument_and_coordinates():
    query = " ".join(
        target_instrument_query("HARPS", ra_deg=12.34, dec_deg=-45.6).split()
    )
    assert "instrument_name = 'HARPS'" in query
    assert "12.34" in query
    assert "-45.6" in query
    assert "CONTAINS" in query

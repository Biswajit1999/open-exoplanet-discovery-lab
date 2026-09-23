from exolab.instrument import nirps_precision_rv_quality, version_at_least


def test_version_comparison():
    assert version_at_least("NIRPS DRS 3.2.7", "3.2.7")
    assert version_at_least("3.3.0", "3.2.7")
    assert not version_at_least("3.2.6", "3.2.7")


def test_affected_nirps_interval_requires_corrected_pipeline():
    bad = nirps_precision_rv_quality("2025-05-10T00:00:00", "3.2.6")
    corrected = nirps_precision_rv_quality("2025-05-10T00:00:00", "3.2.7")
    outside = nirps_precision_rv_quality("2026-01-10T00:00:00", "3.2.6")
    assert not bad.precision_rv_safe
    assert corrected.precision_rv_safe
    assert outside.precision_rv_safe

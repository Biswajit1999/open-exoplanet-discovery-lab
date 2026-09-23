"""Open Exoplanet Evidence Lab public API."""

from .activity import ActivityRegression, weighted_activity_regression
from .archives import ExoplanetArchiveClient
from .atmosphere import RandomEffectsEstimate, estimate_extra_scatter
from .chromatic import (
    ChromaticSignalComparison,
    compare_fixed_period_signal,
    matched_epoch_pairs,
    simultaneity_counts,
)
from .completeness import (
    InjectionRecovery as RVInjectionRecovery,
    inject_and_recover,
    run_injection_grid,
)
from .crossmatch import angular_separation_arcsec, nearest_match
from .inference import aicc, bic, fit_white_jitter, gaussian_log_likelihood
from .injection import RecoveryResult, inject_box_transit, run_injection_recovery
from .kepler import keplerian_rv, solve_eccentric_anomaly
from .periodogram import generalized_lomb_scargle, spectral_window
from .provenance import (
    DatasetRecord,
    FileRecord,
    canonical_json_sha256,
    sha256_file,
    verify_manifest,
    write_manifest,
)
from .registry import DataSource, load_registry, require_source
from .results import ResultEnvelope, write_result
from .search import TransitSignal, clean_lightcurve, detrend_lightcurve, search_bls
from .timeseries import fit_sinusoid, weighted_mean, weighted_rms
from .vetting import VettingResult, vet_signal

__all__ = [
    "ActivityRegression",
    "ChromaticSignalComparison",
    "DataSource",
    "DatasetRecord",
    "ExoplanetArchiveClient",
    "FileRecord",
    "RVInjectionRecovery",
    "RandomEffectsEstimate",
    "RecoveryResult",
    "ResultEnvelope",
    "TransitSignal",
    "VettingResult",
    "aicc",
    "angular_separation_arcsec",
    "bic",
    "canonical_json_sha256",
    "clean_lightcurve",
    "compare_fixed_period_signal",
    "detrend_lightcurve",
    "estimate_extra_scatter",
    "fit_sinusoid",
    "fit_white_jitter",
    "gaussian_log_likelihood",
    "generalized_lomb_scargle",
    "inject_and_recover",
    "inject_box_transit",
    "keplerian_rv",
    "load_registry",
    "matched_epoch_pairs",
    "nearest_match",
    "require_source",
    "run_injection_grid",
    "run_injection_recovery",
    "search_bls",
    "sha256_file",
    "simultaneity_counts",
    "solve_eccentric_anomaly",
    "spectral_window",
    "verify_manifest",
    "vet_signal",
    "weighted_activity_regression",
    "weighted_mean",
    "weighted_rms",
    "write_manifest",
    "write_result",
]

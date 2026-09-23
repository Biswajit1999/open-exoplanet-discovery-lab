"""Open Exoplanet Evidence Lab public API."""

from .activity import ActivityRegression, weighted_activity_regression
from .archives import ExoplanetArchiveClient
from .atmosphere import (
    BandMean,
    RandomEffectsEstimate,
    RandomEffectsResult,
    estimate_extra_scatter,
    random_effects_mean,
    weighted_band_mean,
)
from .chromatic import (
    ChromaticSignalComparison,
    CoherenceResult,
    compare_bands,
    compare_fixed_period_signal,
    matched_epoch_pairs,
    simultaneity_counts,
)
from .completeness import (
    InjectionOutcome,
    InjectionRecovery as RVInjectionRecovery,
    completeness_table,
    inject_circular,
    inject_and_recover,
    injection_recovery,
    run_injection_grid,
)
from .crossmatch import angular_separation_arcsec, nearest_match
from .eso import ESOTapClient, overlap_census
from .inference import aicc, bic, fit_white_jitter, gaussian_log_likelihood
from .injection import RecoveryResult, inject_box_transit, run_injection_recovery
from .kepler import keplerian_rv, solve_eccentric_anomaly
from .periodogram import generalized_lomb_scargle, gls, spectral_window
from .provenance import (
    DatasetRecord,
    FileRecord,
    canonical_json_sha256,
    sha256_file,
    verify_manifest,
    write_manifest,
)
from .registry import DataSource, SourceSpec, load_registry, require_source
from .rv import SinusoidFit, fit_instrument_offsets, fit_shared_sinusoid
from .results import ResultEnvelope, write_result
from .search import TransitSignal, clean_lightcurve, detrend_lightcurve, search_bls
from .timeseries import fit_sinusoid, weighted_mean, weighted_rms
from .vetting import VettingResult, vet_signal
from .validation import pearson_with_permutation
from .vizier import VizierClient

__all__ = [
    "ActivityRegression",
    "BandMean",
    "ChromaticSignalComparison",
    "CoherenceResult",
    "DataSource",
    "DatasetRecord",
    "ExoplanetArchiveClient",
    "ESOTapClient",
    "FileRecord",
    "InjectionOutcome",
    "RVInjectionRecovery",
    "RandomEffectsEstimate",
    "RandomEffectsResult",
    "RecoveryResult",
    "ResultEnvelope",
    "SinusoidFit",
    "SourceSpec",
    "TransitSignal",
    "VettingResult",
    "VizierClient",
    "aicc",
    "angular_separation_arcsec",
    "bic",
    "canonical_json_sha256",
    "clean_lightcurve",
    "compare_bands",
    "compare_fixed_period_signal",
    "completeness_table",
    "detrend_lightcurve",
    "estimate_extra_scatter",
    "fit_instrument_offsets",
    "fit_shared_sinusoid",
    "fit_sinusoid",
    "fit_white_jitter",
    "gaussian_log_likelihood",
    "generalized_lomb_scargle",
    "gls",
    "inject_circular",
    "inject_and_recover",
    "inject_box_transit",
    "keplerian_rv",
    "load_registry",
    "matched_epoch_pairs",
    "nearest_match",
    "overlap_census",
    "pearson_with_permutation",
    "random_effects_mean",
    "require_source",
    "run_injection_grid",
    "injection_recovery",
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
    "weighted_band_mean",
    "write_manifest",
    "write_result",
]

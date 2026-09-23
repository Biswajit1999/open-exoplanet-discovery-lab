"""Open Exoplanet Evidence Lab public API."""

from .archives import ExoplanetArchiveClient
from .atmosphere import RandomEffectsResult, random_effects_mean
from .chromatic import CoherenceResult, compare_bands, simultaneity_counts
from .completeness import InjectionOutcome, completeness_table, inject_circular, injection_recovery
from .eso import ESOTapClient, overlap_census
from .injection import RecoveryResult, inject_box_transit, run_injection_recovery
from .periodogram import PeriodogramResult, gls, spectral_window
from .provenance import (
    DatasetRecord,
    FileRecord,
    canonical_json_sha256,
    sha256_file,
    verify_manifest,
    write_manifest,
)
from .registry import SourceSpec, load_registry, require_source
from .rv import SinusoidFit, fit_instrument_offsets, fit_shared_sinusoid, weighted_mean
from .search import TransitSignal, clean_lightcurve, detrend_lightcurve, search_bls
from .validation import pearson_with_permutation
from .vetting import VettingResult, vet_signal
from .vizier import VizierClient

__all__ = [
    "CoherenceResult",
    "DatasetRecord",
    "ESOTapClient",
    "ExoplanetArchiveClient",
    "FileRecord",
    "InjectionOutcome",
    "PeriodogramResult",
    "RandomEffectsResult",
    "RecoveryResult",
    "SinusoidFit",
    "SourceSpec",
    "TransitSignal",
    "VettingResult",
    "VizierClient",
    "canonical_json_sha256",
    "clean_lightcurve",
    "compare_bands",
    "completeness_table",
    "detrend_lightcurve",
    "fit_instrument_offsets",
    "fit_shared_sinusoid",
    "gls",
    "inject_box_transit",
    "inject_circular",
    "injection_recovery",
    "load_registry",
    "overlap_census",
    "pearson_with_permutation",
    "random_effects_mean",
    "require_source",
    "run_injection_recovery",
    "search_bls",
    "sha256_file",
    "simultaneity_counts",
    "spectral_window",
    "verify_manifest",
    "vet_signal",
    "weighted_mean",
    "write_manifest",
]

import numpy as np

from exolab.demo import synthetic_lightcurve
from exolab.injection import inject_box_transit, period_matches
from exolab.search import clean_lightcurve, detrend_lightcurve, search_bls
from exolab.vetting import vet_signal


def test_synthetic_planet_is_recovered():
    time, flux, error = synthetic_lightcurve()
    signal, _ = search_bls(
        time,
        flux,
        error,
        minimum_period=1.0,
        maximum_period=8.0,
        durations_hours=(1.5, 2.0, 2.5),
    )
    assert abs(signal.period_days - 3.2) / 3.2 < 0.01
    assert signal.depth_snr > 7
    assert signal.n_transits >= 8


def test_vetting_does_not_flag_balanced_training_signal():
    time, flux, error = synthetic_lightcurve()
    signal, _ = search_bls(time, flux, error, 1.0, 8.0, (2.0,))
    result = vet_signal(time, flux, signal, error)
    assert "odd-even-depth-mismatch" not in result.flags
    assert "significant-secondary-eclipse" not in result.flags


def test_clean_and_detrend_shapes():
    time, flux, error = synthetic_lightcurve()
    time = np.append(time, np.nan)
    flux = np.append(flux, np.nan)
    error = np.append(error, np.nan)
    clean_time, clean_flux, clean_error = clean_lightcurve(time, flux, error)
    flat, trend = detrend_lightcurve(clean_time, clean_flux, 1.0)
    assert clean_time.shape == clean_flux.shape == clean_error.shape
    assert flat.shape == trend.shape == clean_time.shape
    assert np.isfinite(flat).all()


def test_injection_and_alias_matching():
    time = np.linspace(0, 10, 1000)
    flux = inject_box_transit(time, np.ones_like(time), 2.0, 0.5, 0.1, 0.01)
    assert flux.min() == 0.99
    assert period_matches(2.0, 2.01)
    assert period_matches(2.0, 1.0)
    assert not period_matches(2.0, 1.35)

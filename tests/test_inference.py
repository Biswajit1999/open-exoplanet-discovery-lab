import numpy as np

from exolab.inference import aicc, bic, fit_white_jitter, gaussian_log_likelihood


def test_jitter_fit_is_non_negative_and_improves_noisy_residual_likelihood():
    rng = np.random.default_rng(11)
    error = np.full(300, 0.3)
    residual = rng.normal(0.0, 1.2, 300)
    no_jitter = gaussian_log_likelihood(residual, error)
    fit = fit_white_jitter(residual, error)
    assert fit.jitter > 0
    assert fit.log_likelihood > no_jitter


def test_information_criteria_are_finite():
    assert np.isfinite(bic(-100.0, 5, 200))
    assert np.isfinite(aicc(-100.0, 5, 200))

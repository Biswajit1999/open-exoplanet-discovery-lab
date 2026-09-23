"""Small validation and resampling utilities."""

from __future__ import annotations

import numpy as np


def pearson_with_permutation(x, y, *, n_permutations: int = 2000, seed: int = 0):
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    if x.shape != y.shape or x.ndim != 1 or len(x) < 4:
        raise ValueError("x and y must be matching 1D arrays with n >= 4")
    if not np.isfinite(np.r_[x, y]).all():
        raise ValueError("inputs must be finite")
    r = float(np.corrcoef(x, y)[0, 1])
    rng = np.random.default_rng(seed)
    exceed = 0
    for _ in range(int(n_permutations)):
        rp = float(np.corrcoef(x, rng.permutation(y))[0, 1])
        exceed += abs(rp) >= abs(r)
    p = (exceed + 1.0) / (int(n_permutations) + 1.0)
    return {"r": r, "p_permutation": float(p), "n": int(len(x)), "seed": int(seed)}

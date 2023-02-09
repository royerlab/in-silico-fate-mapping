from typing import Callable

import numpy as np
import pytest


def _line(n_samples: int = 5, length: int = 50, dim: int = 3) -> np.ndarray:
    """Generates a random line on the tracks format"""
    rng = np.random.default_rng(42)
    start = rng.uniform(5, 25, size=(1, dim))
    end = rng.uniform(60, 80, size=(1, dim))
    weight = np.linspace(0, 1, num=length)[:, np.newaxis]
    tracks = np.empty((n_samples, length, dim + 2), dtype=float)
    line = start * (1 - weight) + end * weight
    time = np.arange(length)
    for i in range(n_samples):
        tracks[i, :, 0] = i + 1
        tracks[i, :, 1] = time
        tracks[i, :, 2:] = line + rng.normal(size=(length, dim))
    return tracks.reshape((n_samples * length, dim + 2))


@pytest.fixture
def line(**kwargs) -> np.ndarray:
    return _line(**kwargs)


@pytest.fixture
def line_factory() -> Callable:
    def _func(**kwargs) -> np.ndarray:
        return _line(**kwargs)

    return _func

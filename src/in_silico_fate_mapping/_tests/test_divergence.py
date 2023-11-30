from typing import Tuple

import numpy as np

from in_silico_fate_mapping.divergence import Divergence


def _random_tracks(
    mask: np.ndarray,
    length: int,
    offset: int,
    rng: np.random.Generator,
    orientation: float = 1,
) -> np.ndarray:

    coords = np.asarray(np.nonzero(mask)).T
    n_samples, dim = coords.shape
    shift = rng.uniform(0, 50, size=(1, dim)) * orientation
    weights = np.linspace(0, 1, num=length)[:, np.newaxis]
    tracks = np.empty((n_samples, length, dim + 2), dtype=float)
    time = np.arange(length)
    line = shift * weights
    for i in range(n_samples):
        tracks[i, :, 0] = i + offset
        tracks[i, :, 1] = time
        tracks[i, :, 2:] = coords[i] + line + rng.normal(size=(length, dim))

    # sampling half of it
    tracks = tracks[rng.uniform(0, 1, size=n_samples) < 0.5]
    return tracks.reshape((-1, dim + 2))


def _draw_disk(
    grid: np.ndarray, center: np.ndarray, radius: float
) -> np.ndarray:
    disk = grid - center[..., np.newaxis, np.newaxis]
    return np.square(disk).sum(axis=0) < radius * radius


def _simple_divergence_data(
    length: int = 100,
    display: bool = False,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:

    size = 128
    mask = np.zeros((size, size), dtype=bool)

    coords = np.mgrid[:size, :size]

    tracks = []
    offset = 1
    rng = np.random.default_rng(42)

    # first disk
    disk1 = _draw_disk(coords, np.asarray((32, 32)), 5)
    mask |= disk1

    # first track
    tracks.append(_random_tracks(disk1, length, offset, rng))
    offset = tracks[-1][-1, 0] + 1  # last track id

    # second disk
    disk2 = _draw_disk(coords, np.asarray((76, 76)), 5)
    mask |= disk2

    # second track
    tracks.append(_random_tracks(disk2, length, offset, rng))
    offset = tracks[-1][-1, 0] + 1  # last track id

    # third track from same origin
    tracks.append(_random_tracks(disk2, length, offset, rng, orientation=-1))
    offset = tracks[-1][-1, 0] + 1  # last track id

    tracks = np.concatenate(tracks, axis=0)

    if display:
        import napari

        viewer = napari.view_image(mask)
        viewer.add_tracks(tracks)

        napari.run()

    return disk1, disk2, mask, tracks


def test_simple_divergence(length: int = 100, display: bool = False) -> None:

    disk1, disk2, mask, tracks = _simple_divergence_data(length)
    div = Divergence(tracks, radius=5)
    divergence = div(mask, 0)

    if display:
        import napari

        viewer = napari.Viewer()
        viewer.add_image(mask)
        viewer.add_tracks(tracks)
        viewer.add_image(divergence)
        napari.run()

    div1 = divergence[disk1].mean()
    div2 = divergence[disk2].mean()

    assert (
        3 * div1 < div2
    )  # assuming it should be at least 3 times more diverse


if __name__ == "__main__":
    # _simple_divergence_data(display=True)
    test_simple_divergence(display=False)

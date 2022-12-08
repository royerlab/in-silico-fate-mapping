from pathlib import Path
from typing import Callable

import numpy as np
import pandas as pd
import pytest
from napari import Viewer, save_layers

from in_silico_fate_mapping._reader import napari_get_reader

ViewerMaker = Callable[[], Viewer]


@pytest.fixture
def tracks(n_nodes: int = 10) -> pd.DataFrame:
    coordinates = np.random.rand(n_nodes, 3)
    tracks_data = np.zeros((n_nodes, 5))
    tracks_data[:, 2:] = coordinates

    tracks_data[: n_nodes // 2, 0] = 1
    tracks_data[n_nodes // 2 :, 0] = 2
    tracks_data[: n_nodes // 2, 1] = np.arange(n_nodes // 2)
    tracks_data[n_nodes // 2 :, 1] = np.arange(n_nodes - n_nodes // 2)

    return pd.DataFrame(tracks_data, columns=["TrackID", "t", "z", "y", "x"])


def test_get_reader(tmp_path: Path, tracks: pd.DataFrame) -> None:
    path = tmp_path / "good_tracks.csv"
    tracks["NodeID"] = np.arange(len(tracks)) + 1
    tracks["Labels"] = np.random.randint(2, size=len(tracks))
    tracks.to_csv(path, index=False)

    reader = napari_get_reader(path)
    assert callable(reader)

    data, kwargs, type = reader(path)[0]
    assert type == "tracks"

    props = kwargs["properties"]

    assert np.allclose(props["NodeID"], tracks["NodeID"])
    assert np.allclose(props["Labels"], tracks["Labels"])
    assert np.allclose(data, tracks[["TrackID", "t", "z", "y", "x"]])


def test_napari_read(
    make_napari_viewer: ViewerMaker,
    tmp_path: Path,
    tracks: pd.DataFrame,
) -> None:

    path = tmp_path / "good_tracks.csv"
    tracks.to_csv(path, index=False)

    viewer = make_napari_viewer()
    (layer,) = viewer.open(path, plugin="in-silico-fate-mapping")

    assert layer is not None
    assert np.allclose(layer.data, tracks)


def test_napari_write_and_read(
    make_napari_viewer: ViewerMaker,
    tmp_path: Path,
    tracks: pd.DataFrame,
) -> None:

    viewer = make_napari_viewer()
    path = tmp_path / "good_tracks.csv"

    layer = viewer.add_tracks(tracks.values)

    (outpath,) = save_layers(path, [layer])
    assert outpath == path

    viewer.layers.clear()
    (layer,) = viewer.open(outpath, plugin="in-silico-fate-mapping")

    assert np.allclose(layer.data, tracks)


def test_non_existing_track() -> None:
    reader = napari_get_reader("tracks.csv")
    assert reader is None


def test_wrong_columns_track(tmp_path: Path, tracks: pd.DataFrame) -> None:
    path = tmp_path / "bad_tracks.csv"
    tracks.rename(columns={"TrackID": "id"}, inplace=True)
    tracks.to_csv(path, index=False)
    reader = napari_get_reader(path)
    assert reader is None

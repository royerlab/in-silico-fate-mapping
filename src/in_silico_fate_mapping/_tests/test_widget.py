from typing import Callable

import napari
import numpy as np
import pandas as pd
import pytest

from in_silico_fate_mapping import FateMappingWidget


@pytest.mark.parametrize(
    "starting_idx,image_scale,tracks_scale,points_scale",
    [
        (0, 1.0, 1.0, 1.0),
        (5, 1.0, 1.0, 1.0),
        (0, 3.0, 1.0, 1.0),
        (0, 1.0, 1.0, 2.0),
        (0, 1.0, 0.25, 1.0),
        (7, 2.0, 3.0, 0.5),
    ],
)
def test_fate_mapping_widget(
    make_napari_viewer: Callable[[], napari.Viewer],
    line_factory: Callable,
    starting_idx: int,
    image_scale: float,
    tracks_scale: float,
    points_scale: float,
    request,
) -> None:
    # NOTE: Use "--show-napari-viewer" to show viewer, useful when debugging

    viewer = make_napari_viewer()
    widget = FateMappingWidget(viewer)
    viewer.window.add_dock_widget(widget)

    line = line_factory(n_samples=1, length=50, dim=3)

    image_scale = (1.0, image_scale, 1.0, 1.0)
    image_shape = (line[:, 1:].max(axis=0) + 1) / image_scale
    image_shape = np.round(image_shape).astype(int)
    mock_image = np.random.uniform(size=image_shape)

    viewer.add_image(mock_image, scale=image_scale)

    tracks_scale = np.asarray((1, 1, tracks_scale, 1, 1))
    tracks_layer = viewer.add_tracks(
        line / tracks_scale, scale=tracks_scale[1:], colormap="twilight"
    )

    points_scale = np.asarray((1, points_scale, 1, 1))
    points_layer = viewer.add_points(
        line[starting_idx, 1:] / points_scale, scale=points_scale
    )

    assert widget._tracks_layer_w.value == tracks_layer
    assert widget._points_layer_w.value == points_layer

    widget._sigma_w.value = 0.5
    widget._bind_w.value = False
    widget._radius_w.value = 2.5

    widget._run_btn.clicked()

    assert len(viewer.layers) == 4

    if request.config.getoption("--show-napari-viewer"):
        napari.run()
        return

    avg = (
        pd.DataFrame(viewer.layers[-1].data)
        .groupby([1])[[2, 3, 4]]
        .mean()
        .to_numpy()
    )

    max_error = np.abs(avg - line[starting_idx:, 2:]).max()
    assert max_error < 1

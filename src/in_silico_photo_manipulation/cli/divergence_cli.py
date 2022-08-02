from pathlib import Path
from typing import Optional

import click
import napari
import numpy as np
import pandas as pd
from scipy.ndimage import (
    binary_dilation,
    generate_binary_structure,
    iterate_structure,
)
from tifffile import imwrite

from in_silico_photo_manipulation.divergence import Divergence


def disk(rank: int, radius: int) -> np.ndarray:
    struct = generate_binary_structure(rank, 1)
    return iterate_structure(struct, radius)


@click.command()
@click.argument(
    "tracks-path", nargs=1, type=click.Path(exists=True, path_type=Path)
)
@click.option(
    "--time-point", "-t", type=int, default=0, help="Starting time point"
)
@click.option(
    "--radius",
    "-r",
    type=float,
    default=25,
    help="Interpolation neighborhood radius",
)
@click.option(
    "--n-samples",
    "-n",
    type=int,
    default=20,
    help="Number of samples per pixel",
)
@click.option(
    "--dilation",
    "-d",
    type=int,
    default=0,
    help="Dilation radius at starting points.",
)
@click.option("--z-scale", "-z", type=float, default=1.0)
@click.option(
    "--output-path",
    "-o",
    type=click.Path(exists=True, path_type=Path),
    default=None,
)
@click.option("--quiet", "-q", type=bool, default=False, is_flag=True)
@click.option(
    "--downsample",
    type=float,
    default=None,
    help="Downsample result (CUPY required).",
)
@click.option(
    "--max-length",
    "-ml",
    type=int,
    default=None,
    show_default=True,
    help="Length (in time) to stop divergence computation.",
)
def div(
    tracks_path: Path,
    time_point: int,
    radius: float,
    n_samples: int,
    dilation: int,
    z_scale: float,
    output_path: Optional[Path],
    quiet: bool,
    downsample: Optional[float],
    max_length: Optional[int],
) -> None:
    """Computes the divergence of tracks from a given time point"""

    if output_path is None:
        output_path = Path(
            f"output_tp_{time_point:05d}_dilation_{dilation}.tif"
        )

    tracks = pd.read_csv(tracks_path)
    tracks["z"] *= z_scale

    divergence = Divergence(tracks, n_samples=n_samples, radius=radius)

    source = tracks[np.abs(tracks["t"] - time_point) < 1][
        divergence._spatial_columns
    ].values
    source = tuple(np.round(source).astype(int).T)

    shape = (
        np.ceil(tracks[divergence._spatial_columns].max(axis=0)).astype(int)
        + 1
    )
    mask = np.zeros(shape, dtype=bool)
    mask[source] = True

    if dilation > 0:
        struct = disk(mask.ndim, dilation)
        mask = binary_dilation(mask, struct)

    heatmap = divergence(mask, time_point, max_length)

    if downsample is not None:
        import cupy as cp
        from cupyx.scipy.ndimage import zoom

        heatmap = zoom(cp.asarray(heatmap), downsample).get()

    imwrite(output_path, heatmap)

    if not quiet:
        napari.view_image(heatmap, colormap="magma")
        napari.run()

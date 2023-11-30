from pathlib import Path

import numpy as np
import pandas as pd

TRACKS_HEADER = ("TrackID", "t", "z", "y", "x")


def napari_get_reader(path):
    if isinstance(path, list):
        path = path[0]

    if isinstance(path, str):
        path = Path(path)

    if not path.name.endswith(".csv") or not path.exists():
        return None

    header = pd.read_csv(path, nrows=0).columns.tolist()
    for colname in TRACKS_HEADER:
        if colname != "z" and colname not in header:
            return None

    return reader_function


def read_csv(path: str):
    df = pd.read_csv(path)

    data = []
    for colname in TRACKS_HEADER:
        try:
            data.append(df[colname])
        except KeyError:
            if colname != "z":
                raise KeyError(f"{colname} not found in .csv header.")

    data = np.stack(data).T

    props = {
        colname: df[colname]
        for colname in df.columns
        if colname not in TRACKS_HEADER
    }

    kwargs = {"properties": props}
    return (data, kwargs, "tracks")


def reader_function(path):
    paths = [path] if isinstance(path, (str, Path)) else path
    return [read_csv(p) for p in paths]

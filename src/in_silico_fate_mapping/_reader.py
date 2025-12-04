from pathlib import Path

import numpy as np
import pandas as pd

TRACKS_HEADER = (
    ("track_id", "TrackID"),
    ("t", "T"),
    ("z", "Z"),
    ("y", "Y"),
    ("x", "X"),
)


def napari_get_reader(path):
    if isinstance(path, list):
        path = path[0]

    if isinstance(path, str):
        path = Path(path)

    if not path.name.endswith(".csv") or not path.exists():
        return None

    header = pd.read_csv(path, nrows=0).columns.tolist()
    for colnames in TRACKS_HEADER:
        if all(c not in header for c in colnames) and colnames[0] != "z":
            return None

    return reader_function


def read_csv(path: str):
    df = pd.read_csv(path)

    data = []
    for colnames in TRACKS_HEADER:
        found = False
        for c in colnames:
            if c in df.columns:
                data.append(df[c])
                found = True
                break
        if not found and colnames[0] != "z":
            raise KeyError(f"{colnames[0]} not found in .csv header.")

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

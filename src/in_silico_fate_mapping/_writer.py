from typing import List

import numpy as np
import pandas as pd

from in_silico_fate_mapping._reader import TRACKS_HEADER


def napari_write_tracks(path: str, data: np.ndarray, meta: dict) -> List[str]:

    header = list(TRACKS_HEADER)
    if data.shape[1] == 4:
        header.remove("z")

    df = pd.DataFrame(data, columns=header)
    df.to_csv(path, index=False)

    return [path]

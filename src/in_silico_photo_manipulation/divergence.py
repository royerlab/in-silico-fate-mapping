from typing import Optional, Union

import numpy as np
import pandas as pd
from tqdm import tqdm

from in_silico_photo_manipulation.photom import PhotoM, update_fit


class Divergence(PhotoM):
    def __init__(
        self,
        data: Optional[Union[pd.DataFrame, np.ndarray]] = None,
        radius: float = 1,
        reverse: bool = False,
        sigma: float = 0.1,
        weights: str = "distance",
        n_samples: int = 25,
    ) -> None:
        """
        Computes divergence of a given mask using the photo manipulation simulation.

        Parameters
        ----------
        data : Optional[Union[pd.DataFrame, np.ndarray]], optional
            Dataframe with columns TrackID, t, (z), y, x or 2-dim array with length 4 or 5 on 1-axis
        radius : float, optional
            Interpolation neighboord radius
        reverse : bool, optional
            Indicates reverse time step direction
        sigma : float, optional
            Additive gaussian noise sigma
        weights : str, optional
            Interpolation weighting strategy, by default "distance"
        n_samples : int, optional
            Number of samples per individual coordinate, by default 25
        """
        super().__init__(
            data=data,
            radius=radius,
            reverse=reverse,
            sigma=sigma,
            weights=weights,
            heatmap=False,
            n_samples=n_samples,
            bind_to_existing=False,
        )

    @update_fit
    def __call__(self, mask: np.ndarray, time_point: int) -> np.ndarray:
        """Returns divergence measurement of given mask starting from the given time point.

        Parameters
        ----------
        mask : np.ndarray
            Binary array.
        time_point : int
            Time point belonging to training data range.

        Returns
        -------
        np.ndarray
            Divergence heatmap.
        """
        coords = np.asarray(np.nonzero(mask)).T
        source = np.concatenate(
            (np.full((len(coords), 1), time_point), coords), axis=1
        )

        source = self._preprocess_source(source)
        t0 = source[0, 0]

        pos = np.asarray(source[:, 1:])
        shape = pos.shape

        _noise = self._get_noise_function(shape)

        valid = self._valid_rows(pos)

        for t in tqdm(self.time_iter(t0=int(round(t0))), "Computing paths"):
            X = (pos + _noise())[valid]
            if len(X) == 0:
                break
            next_pos = self._models[t].predict(X)
            new_valid = self._valid_rows(next_pos)
            valid[valid] &= new_valid
            pos[valid] = next_pos[new_valid]

        pos = pos.T  # (D, K * N), K = n_samples
        pos = pos.reshape((shape[1], -1, self.n_samples))  # (D, N, K)
        stddev = pos.std(axis=-1)  # (D, N)
        stddev = stddev.sum(axis=0)  # (N,)

        divergence = np.zeros(mask.shape, dtype=np.float32)
        divergence[mask] = stddev

        return divergence

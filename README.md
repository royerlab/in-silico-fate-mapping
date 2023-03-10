# in silico fate mapping

[![License BSD-3](https://img.shields.io/pypi/l/in-silico-fate-mapping.svg?color=green)](https://github.com/royerlab/in-silico-fate-mapping/raw/main/LICENSE)
[![PyPI](https://img.shields.io/pypi/v/in-silico-fate-mapping.svg?color=green)](https://pypi.org/project/in-silico-fate-mapping)
[![Python Version](https://img.shields.io/pypi/pyversions/in-silico-fate-mapping.svg?color=green)](https://python.org)
[![tests](https://github.com/royerlab/in-silico-fate-mapping/workflows/tests/badge.svg)](https://github.com/royerlab/in-silico-fate-mapping/actions)
[![codecov](https://codecov.io/gh/royerlab/in-silico-fate-mapping/branch/main/graph/badge.svg)](https://codecov.io/gh/royerlab/in-silico-fate-mapping)
[![napari hub](https://img.shields.io/endpoint?url=https://api.napari-hub.org/shields/in-silico-fate-mapping)](https://napari-hub.org/plugins/in-silico-fate-mapping)


Interactive in silico fate mapping from tracking data.

This napari plugin estimates the cell fates from tracking data by building a radial regression model per time point. The user can select an area of interest using a `Points` layer; the algorithm will advent the probed coordinates forward (or backward) in time, showing the estimated fate.

Video example below:

https://user-images.githubusercontent.com/21022743/216478216-89c1c35f-2ce4-44e8-adb8-9aeea75b5833.mp4

## Installation

You can install `in-silico-fate-mapping` via [pip]:

    pip install in-silico-fate-mapping


To install the latest development version :

    pip install git+https://github.com/royerlab/in-silico-fate-mapping.git


## IO file format

This plugin does not depend on a specific file format, the only requirement is using a `Track` layer from napari.

Despite this, we ship a reader and writer interface. It supports `.csv` files with the following reader `TrackID, t, (z), y, x`, `z` is optional.
Such that each tracklet has a unique `TrackID` and it's composed of a sequence o time and spatial coordinates.

This is extremely similar to how napari store tracks, more information can be found [here](https://napari.org/stable/howtos/layers/tracks.html).

Divisions are not supported at the moment.

## Usage Example

```python3
import napari
import pandas as pd
from in_silico_fate_mapping.fate_mapping import FateMapping

tracks = pd.read_csv("tracks.csv")

fate_map = FateMapping(radius=5, n_samples=25, bind_to_existing=False, sigma=1)
fate_map.data = tracks[["TrackID", "t", "z", "y", "x"]]

source = tracks[tracks["t"] == 0].sample(n=1)

tracks = fate_map(source[["t", "z", "y", "x"]])

napari.view_tracks(tracks)
napari.run()
```

## Citing

If used please cite:

```
@article{lange2023zebrahub,
  title={Zebrahub-Multimodal Zebrafish Developmental Atlas Reveals the State Transition Dynamics of Late Vertebrate Pluripotent Axial Progenitors},
  author={Lange, Merlin and Granados, Alejandro and VijayKumar, Shruthi and Bragantini, Jordao and Ancheta, Sarah and Santhosh, Sreejith and Borja, Michael and Kobayashi, Hirofumi and McGeever, Erin and Solak, Ahmet Can and others},
  journal={bioRxiv},
  pages={2023--03},
  year={2023},
  publisher={Cold Spring Harbor Laboratory}
}
```

## Issues

If you encounter any problems, please [file an issue] along with a detailed description.

[napari]: https://github.com/napari/napari
[Cookiecutter]: https://github.com/audreyr/cookiecutter
[@napari]: https://github.com/napari
[MIT]: http://opensource.org/licenses/MIT
[BSD-3]: http://opensource.org/licenses/BSD-3-Clause
[GNU GPL v3.0]: http://www.gnu.org/licenses/gpl-3.0.txt
[GNU LGPL v3.0]: http://www.gnu.org/licenses/lgpl-3.0.txt
[Apache Software License 2.0]: http://www.apache.org/licenses/LICENSE-2.0
[Mozilla Public License 2.0]: https://www.mozilla.org/media/MPL/2.0/index.txt
[cookiecutter-napari-plugin]: https://github.com/napari/cookiecutter-napari-plugin

[file an issue]: https://github.com/royerlab/in-silico-fate-mapping/issues

[napari]: https://github.com/napari/napari
[tox]: https://tox.readthedocs.io/en/latest/
[pip]: https://pypi.org/project/pip/
[PyPI]: https://pypi.org/

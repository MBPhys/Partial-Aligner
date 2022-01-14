# Partial-Aligner

[![License](https://img.shields.io/pypi/l/napari-medical-image-formats.svg?color=green)](https://github.com/MBPhys/Partial-Aligner/raw/master/LICENSE)
[![PyPI](https://img.shields.io/pypi/v/Partial-Aligner.svg?color=green)](https://pypi.org/project/Partial-Aligner)
[![Python Version](https://img.shields.io/pypi/pyversions/Partial-Aligner.svg?color=green)](https://python.org)


A plugin to affine transform images and parts of images in 2D and 3D. It was developed in the context of brain slice registration and solves multiple, related problems when working with histology slices.

----------------------------------

## Installation

You can install `Partial-Aligner` via [pip]:

    pip install Partial-Aligner

## Usage

It is important to note that this plugin is part of a group of plugins which are intended to be used together

The principle workflow with this plugin is as follows:

1. Load an image of interest (ioi) using standard napari.
2. Find out meaningful transformation parameters for the ioi (or part of it) based on what you see in the viewer.
3. Save the affine transformation matrix
4. Apply the saved transformation to create a new, altered version of the ioi (use plugin 'World2Data')

Decisions on the parameters (step 2) are made based on the problem at hand:

- Registration: You have a second (fixed) image and you want to align your ioi to that image? Transform your whole ioi! Just play with the transformation parameters until you are happy with the alignment of ioi and fixed image. Continue with steps 3 and 4.
- Histology artifact repair: Parts of your histology slice are misplaced? Transform the misplaced parts! Label them and change the transformation parameters for the misplaced parts until you are happy with their alignment with the rest of the image. Continue with steps 3 and 4.





## Contributing

Contributions are very welcome. Tests can be run with [tox].

## License

Distributed under the terms of the [BSD-3] license,
"Partial-Aligner" is free and open source software.

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
[file an issue]: https://github.com/MBPhys/Partial-Aligner/issues
[napari]: https://github.com/napari/napari
[tox]: https://tox.readthedocs.io/en/latest/
[pip]: https://pypi.org/project/pip/
[PyPI]: https://pypi.org/

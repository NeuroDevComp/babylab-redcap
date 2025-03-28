# babylab-redcap

![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/NeuroDevComp/babylab-redcap/pytest.yml)
![GitHub Issues or Pull Requests](https://img.shields.io/github/issues/NeuroDevComp/babylab-redcap)
![PyPI - License](https://img.shields.io/pypi/l/babylab)
![PyPI - Status](https://img.shields.io/pypi/status/babylab)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/babylab)
![PyPI - Version](https://img.shields.io/pypi/v/babylab)
![GitHub Tag](https://img.shields.io/github/v/tag/NeuroDevComp/babylab-redcap)
![GitHub Release](https://img.shields.io/github/v/release/NeuroDevComp/babylab-redcap)

---

## Table of Contents

- [Installation](#installation)
- [Launch](#launch)
- [Updating](#updating)
- [Feed-back](#feed-back)
- [License](#license)

## Installation

Python >=3.10 is needed. I recommend you install Python 3.12.7 from the [official website](https://www.python.org/downloads/release/python-3127/). Depending on your OS, you may have to download one of these files:

* **Windows**: `Windows installer (64-bit)` file
* **macOS**: `macOS 64-bit universal2 installer` file

Once Python is installed, [open your terminal](https://www.youtube.com/watch?v=8Iyldhkrh7E) and run this command to install the necessary Python modules:

* **Windows**: `python -m pip install flask pywin32 python-dotenv babylab`
* **Linux/macOS**: `python3 -m pip install flask pywin32 python-dotenv babylab`

## Launch

To run the app in your browser, run the following command in your terminal:

* **Windows**: `python -m flask --app babylab.app run`
* **Linux/macOS**: `python3 -m flask --app babylab.app run`

Open your browser and go to [http://127.0.0.1:5000](http://127.0.0.1:5000). Log in with your API authentication token (and maybe your email), and you should be ready to go!

## Updating

To update the app, run the following line of code in your terminal:

* **Windows**: `python -m pip install --upgrade babylab`
* **Linux/macOS**: `python3 -m pip install --upgrade babylab`


## Feed-back

Please, report any issues or feeb-back by opening a [GitHub issue](https://github.com/NeuroDevComp/babylab-redcap/issues/new/choose), or getting in touch at [gonzalo.garcia[at]sjd.es](mailto:gonzalo.garcia@sjd.es).


## License

`babylab-redcap` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.


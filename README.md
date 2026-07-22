# VowSpace: A vowel formant analysis application for phonetic research

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Tests](https://github.com/alicagank/VowSpace/actions/workflows/tests.yml/badge.svg)](https://github.com/alicagank/VowSpace/actions/workflows/tests.yml)
[![Build](https://github.com/alicagank/VowSpace/actions/workflows/build.yml/badge.svg)](https://github.com/alicagank/VowSpace/actions/workflows/build.yml)
[![DOI](https://joss.theoj.org/papers/10.21105/joss.10189/status.svg)](https://doi.org/10.21105/joss.10189)

![VowSpace icon](vowspace/assets/vowspace.ico)

VowSpace is an open-source desktop application for extracting, visualising, normalising, comparing, and analysing vowel formant data from audio recordings and tabular datasets.

It provides an accessible graphical interface for common phonetic and sociophonetic workflows that might otherwise require custom scripts or several separate applications.

**Quick links:** [Download VowSpace](https://github.com/alicagank/VowSpace/releases) · [Tutorials](tutorial/instructions.md) · [Software paper](https://doi.org/10.21105/joss.10189) · [Changelog](CHANGELOG.md) · [Contributing](CONTRIBUTING.md) · [Report an issue](https://github.com/alicagank/VowSpace/issues)

![VowSpace main interface](https://alicagankaya.com/wp-content/uploads/2026/05/vowspace-main.png)

## Key features

- Interactive vowel-space plotting using F1, F2, and other selected measurements
- Acoustic analysis of audio files using Parselmouth and Praat
- Lobanov, Nearey1, Nearey2, and Bark Difference normalisation
- Bark, Mel, ERB, and logarithmic frequency-scale transformations
- Speaker- and vowel-based grouping
- Ellipses, convex hulls, labels, colour palettes, and other plot customisation options
- Built-in DataFrame editor
- CSV and Excel import and export
- Publication-quality PNG, JPG, TIFF, SVG, and PDF plot export
- Built-in IPA keyboard

New to VowSpace? Follow the [step-by-step tutorials](tutorial/instructions.md).

## Software paper

VowSpace has been published in the *Journal of Open Source Software*. The paper describes the motivation behind the project, its main features, and its intended use in phonetic research.

> Kaya, A. Ç. (2026). VowSpace: A vowel formant analysis application for phonetic research. *Journal of Open Source Software, 11*(120), 10189. https://doi.org/10.21105/joss.10189

[Read the software paper](https://joss.theoj.org/papers/10.21105/joss.10189).

## Installation

VowSpace is available as a portable desktop application. Distributable builds are produced with Nuitka through the repository's build workflow.

### macOS

1. Download the latest `.dmg` file from [GitHub Releases](https://github.com/alicagank/VowSpace/releases).
2. Open the downloaded file.
3. Drag **VowSpace** into the **Applications** folder.
4. Launch VowSpace from **Applications**.

If macOS displays a security warning on first launch:

1. Right-click or Control-click the VowSpace application.
2. Select **Open**.
3. Confirm the macOS Gatekeeper prompt.

### Windows

1. Download the latest `.exe` file from [GitHub Releases](https://github.com/alicagank/VowSpace/releases).
2. Open the downloaded file to launch VowSpace.

### Linux

1. Download the latest Linux executable from [GitHub Releases](https://github.com/alicagank/VowSpace/releases).
2. If necessary, make the file executable:

```bash
chmod +x VowSpace
```

3. Launch it from your file manager or terminal.

The current Linux build has primarily been tested on minimal Debian and Fedora. Support for additional distributions and a more polished Linux experience are under active development. The application icon may not display correctly on some systems.

### Run from source

You can also clone the repository and run VowSpace directly from source. This is recommended for developers and researchers who want to inspect or contribute to the code.

```bash
git clone https://github.com/alicagank/VowSpace.git
cd VowSpace
```

VowSpace requires Python 3.10 or later. Its dependencies are declared in `pyproject.toml`.

#### Using uv

[uv](https://docs.astral.sh/uv/) automatically creates a virtual environment and installs the required dependencies on first run:

```bash
uv run vowspace
```

#### Using pip on macOS or Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install .
vowspace
```

#### Using pip on Windows

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install .
vowspace
```

## Input data

The minimum dataset must contain the following columns:

| vowel | f1 | f2 | speaker |
|---|---:|---:|---|
| /æ/ | 123 | 1234 | Özlem |

The required columns are:

- `vowel`
- `f1`
- `f2`
- `speaker`

Additional measurements and derived columns, such as `f0`, `f3`, `f4`, `f5`, `bark_f1`, `log_f1`, and `zsc_f1`, are also supported where needed.

VowSpace can read and write:

- CSV files (`.csv`)
- Excel files (`.xlsx`, `.xls`)

Tabular data are handled with pandas, with Excel support provided through openpyxl.

## Feature overview

### Vowel-space plotting

VowSpace produces conventional vowel-space plots with reversed F2 values on the horizontal axis and reversed F1 values on the vertical axis. However, all of this can be modified. Data from different speakers, sources, or groups can be distinguished using points, labels, colours, ellipses, and convex hulls.

Visualisation settings allow users to customise:

- Colour palettes
- Point size and transparency
- Labels
- Ellipses
- Convex hulls
- Filled, outlined, and circular styles
- Plot titles and other layout options

### Normalisation and scale conversion

Normalisation options are available through the **Normalization Settings** interface. VowSpace preserves the original data and applies one selected method at a time to prevent cumulative transformations.

#### Lobanov normalisation

Lobanov normalisation reduces speaker-dependent anatomical variation by z-scoring each formant:

```text
F_n[V] = (F_n[V] - MEAN_n) / S_n
```

#### Bark Difference Metric

The Bark Difference Metric transforms formant values to the Bark scale and calculates perceptual distances such as Z3–Z1 and Z2–Z1:

```text
Z_i = 26.81 / (1 + (1960 / F_i)) - 0.53
```

#### Nearey1

Nearey1 subtracts the logarithm of a speaker-specific formant mean from each log-transformed value:

```text
F_n[V] = log(F_n[V]) - log(mean(F_n_all_vowels))
```

#### Nearey2

Nearey2 uses a shared log mean across formants:

```text
F_n[V] = log(F_n[V]) - mean(log(F_1, F_2, ..., F_n))
```

#### Frequency-scale transformations

VowSpace also supports the following transformations:

**Log**

```text
F_log = log10(F)
```

**Mel**

```text
F_mel = 2595 × log10(1 + F / 700)
```

**Bark**

```text
Z = 26.81 / (1 + 1960 / F) - 0.53
```

**ERB**

```text
F_erb = 21.4 × log10(1 + 0.00437 × F)
```

The implementations draw on established methods in vowel normalisation and on open resources such as Remirez (2022) and the `phonR` package.

![Raw vowel-space plot](https://alicagankaya.com/wp-content/uploads/2024/03/Gelfer-Bennett-scaled.jpg)

![Bark-transformed vowel-space plot](https://alicagankaya.com/wp-content/uploads/2024/03/Gelfer-Bennett-Bark.png)

![Lobanov-normalised vowel-space plot](https://alicagankaya.com/wp-content/uploads/2024/03/Gelfer-Bennett-Lobanov-Normalized-scaled.jpg)

### Audio Analysis Tools

**Audio Analysis Tools** is a separate window accessible from the main interface. It uses [Parselmouth](https://parselmouth.readthedocs.io/), a Python interface to Praat, to display and measure:

- Intensity
- Pitch
- Vowel formant frequencies from F1 to F5

Users can add measured formant frequencies directly to the main visualiser by right-clicking the plot in the Audio Analysis Tools window.

Higher formants can be unstable in some recordings. Depending on recording quality and environment, F5 may be returned as `NaN`. Measurements can be reviewed and edited in the DataFrame Editor, or repeated when necessary.

Supported audio formats include:

- WAV (`.wav`)
- FLAC (`.flac`)
- AIFF and AIFC (`.aiff`, `.aif`, `.aifc`)
- MP3 (`.mp3`)
- OGG (`.ogg`)

![Intensity display in Audio Analysis Tools](https://alicagankaya.com/wp-content/uploads/2024/07/a3-2048x943.jpg)

*Intensity*

![Pitch display in Audio Analysis Tools](https://alicagankaya.com/wp-content/uploads/2024/07/a2-2048x943.jpg)

*Pitch*

![Formant display in Audio Analysis Tools](https://alicagankaya.com/wp-content/uploads/2024/07/a4-2048x943.jpg)

*Vowel formant frequencies*

### DataFrame Editor

The **DataFrame Editor** allows users to make small adjustments to the current dataset without opening another application. Saving changes automatically updates the plot. Edited data can also be exported as a separate spreadsheet using **Save Data As…**.

![DataFrame Editor interface](https://alicagankaya.com/wp-content/uploads/2024/07/Screenshot-2024-07-30-at-17.41.33.png)

### Export Plot

The **Export Plot** dialog supports PNG, JPG, TIFF, SVG, and PDF output. Its live preview shows how changes to DPI, pixel dimensions, and layout settings affect the exported figure.

![Export Plot dialog](https://alicagankaya.com/wp-content/uploads/2026/05/export.png)

### IPA keyboard

VowSpace includes a dedicated IPA keyboard for entering vowel symbols directly within the application.

![IPA keyboard](https://alicagankaya.com/wp-content/uploads/2025/07/Screenshot-2025-07-02-at-02.55.42.png)

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for detailed release notes.

## Feedback and support

Feedback, bug reports, feature requests, and descriptions of research workflows directly help improve VowSpace.

If you have used the application, you are welcome to complete the [anonymous feedback form](https://forms.gle/D9P6TYfAhiiY4swx8).

For support:

- Read the [tutorials](tutorial/instructions.md).
- Visit the [VowSpace project page](https://alicagankaya.com/vowspace/).
- [Open an issue](https://github.com/alicagank/VowSpace/issues) and include your operating system, Python version, error messages, screenshots, and the expected behaviour where possible.

## Contributing

Contributions, bug fixes, documentation improvements, and feature proposals are welcome. :)
Please read [CONTRIBUTING.md](CONTRIBUTING.md) before submitting a pull request.

VowSpace is independently developed and maintained, so thoughtful issue reports and contributions are especially valuable.

## Validation and disclaimer

VowSpace is actively developed and tested, but users should independently verify its outputs before relying on them in research or publications.

This application is provided **as is**, without warranty of any kind, express or implied. The developer assumes no responsibility for errors, inaccuracies, or consequences arising from the use of the software or its outputs.

## Citation

Please cite VowSpace as:

> Kaya, A. Ç. (2026). VowSpace: A vowel formant analysis application for phonetic research. *Journal of Open Source Software, 11*(120), 10189. https://doi.org/10.21105/joss.10189

BibTeX:

```bibtex
@article{kaya2026vowspace,
  author  = {Kaya, Ali Çağan},
  title   = {VowSpace: A vowel formant analysis application for phonetic research},
  journal = {Journal of Open Source Software},
  year    = {2026},
  volume  = {11},
  number  = {120},
  pages   = {10189},
  doi     = {10.21105/joss.10189}
}
```

## Scientific background

The methodological background and full reference list are available in the [JOSS software paper](https://joss.theoj.org/papers/10.21105/joss.10189). The implementation also draws on established work in vowel plotting, normalisation, auditory scales, Matplotlib, pandas, NumPy, SciPy, Parselmouth, and Praat.

## Licence

VowSpace is distributed under the [GNU General Public License v3.0](LICENSE).

For downloads, examples, and further information, visit the [VowSpace project page](https://alicagankaya.com/vowspace/) or the repository's [Releases](https://github.com/alicagank/VowSpace/releases) page.

# Changelog

All notable changes to VowSpace are documented in this file.

## [1.4.5] — The Visualisation Update

This release gives users greater control over plot customisation, improves the export workflow, and makes the interface cleaner and easier to use.

### Added

* Added a dedicated **Export Plot** dialog with:

  * A live preview of export settings
  * Support for PNG, JPG, TIFF, SVG, and PDF formats
  * Pixel-based dimension controls with DPI scaling
* Added new visualisation customisation options, including:

  * Colour palette selection
  * Point size and transparency controls
  * Ellipse and convex hull styling options, including filled, outlined, and circular styles
* Added a centralised **Visualisation Settings** dialog for a more streamlined workflow.

### Changed

* Refactored the visualisation system:

  * Replaced scattered interface controls with a unified settings window
  * Combined visualisation and normalisation settings in one window
  * Improved the organisation of ellipse, convex hull, label, and related options
* Reworked the normalisation pipeline:

  * Replaced multiple simultaneous selections with a dropdown-based system
  * Limited normalisation to one method at a time
  * Preserved the original data to prevent cumulative transformations
* Improved the export workflow:

  * Unified the saving process within the **Export Plot** dialog
  * Added a quick-save option that uses the current export settings

### Fixed

* Fixed a normalisation-stacking issue that could produce incorrect results after repeated updates.
* Resolved interface inconsistencies in visualisation toggles.

---

## [1.4.2]

### Added

* Added the following normalisation methods:

  * Nearey1
  * Nearey2
  * Bark Difference Metric
* Added the following frequency-scale conversion options:

  * Bark
  * Log
  * Mel
  * ERB
* Enabled the Matplotlib navigation toolbar in **Audio Analysis Tools**, allowing users to:

  * Zoom in and out
  * Change the colour palette
  * Modify visualisation settings
  * Save figures using different configurations
* Introduced a new application icon, drawn specifically for VowSpace. :)

### Changed

* Modularised the previously monolithic codebase into smaller, more maintainable components.
* Significantly improved the overall code organisation.
* Enlarged the **DataFrame Editor** window for improved visibility and usability.

### Documentation

* Added step-by-step tutorials to the GitHub repository to introduce the main features and workflows.

---

## [1.4.1]

### Added

* Added ellipses and convex hulls to connect related data points and improve readability.
* Added a **Group by Vowel** option.

  * Previously, VowSpace connected data belonging to the same speaker.
  * Users can now connect matching vowels across speakers or other groupings.

### Changed

* Enlarged the plotting canvas for improved visualisation.
* Changed the default and minimum application window size to `800 × 800`.
* Increased the default image-export resolution from 600 DPI to 1200 DPI.
* Rearranged the menus for easier navigation.

### Fixed

* Fixed an issue that inverted the axes after importing data.
* Fixed a crash that occurred when the canvas size fell below one pixel.

---

## [1.4.0]

### Added

* Added support for F0, F3, and F4 in both plotting and acoustic measurement.
* Added an option for selecting which formants to plot.
* Added a **DataFrame Editor** for adding, editing, and deleting data through the graphical interface.

### Changed

* Updated the `clear_data`, `read`, and `write` DataFrame methods.
* Updated the Bark and Lobanov normalisation methods to support all available formant frequencies.
* Changed the data-handling logic so that users can select the variables they need through the interface without including unnecessary columns.
* Empty spreadsheet cells are now interpreted as `NaN` values rather than causing the application to crash.

### Fixed

* Fixed a crash caused by empty cells in imported DataFrames.
* Fixed a crash that occurred when applying a convex hull to two-dimensional data.

---

## [1.3.0]

### Added

* Added **Audio Analysis Tools**, a separate window accessible from the main VowSpace interface.
* Added support for reading audio files and displaying:

  * Intensity
  * Pitch
  * Vowel formant frequencies
* Added an IPA keyboard for convenient phonetic-symbol input.
* Added an option to omit the plot title.

---

## [1.2.0]

The initial macOS release. :)

### Added

* Added additional labelling options.

### Fixed

* Fixed an issue affecting the Bark Difference Metric.

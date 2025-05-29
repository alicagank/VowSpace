# VowSpace: A Vowel Formant Analysis Application

VowSpace is an open-source desktop application developed with the aim of acquiring, visualizing, normalizing, and linguistically analyzing vowel sounds from audio files.

![VowSpace UI](https://alicagankaya.com/wp-content/uploads/2024/08/Screenshot-2024-08-04-at-04.23.24.png)

## Version Log

### VowSpace v1.4.1 Release Notes:

**Bug Fixes:**

- Fixed a bug that inverts the axes upon importing data.
- Fixed a bug that made the app crash when the size of the canvas is below 1 pixel.

**New Features:**

- Added Ellipses and Qhulls to connect related data for better readability.
- Group by Vowel option: Normally the application would connect the data that belonged to the same speaker. With this update, the user can now connect the same vowels for different purposes.

**Improvements:**

- Made the canvas bigger for better visualization.
- Made the default and minimum size of the application 800×800.
- Changed the default dpi for saving images from 600 to 1200 for better readability.
- Rearranged the menus for improved navigation.

### VowSpace v1.4.0 Release Notes:

**Bug Fixes:**

- Fixed bug causing program crash when a cell is empty in the dataframe.
- Fixed bug causing program crash when applying a qhull on 2-dimensional data.

**New Features:**

- Added f0 (fundamental freq), f3, and f4 formants for both plotting and acquiring.
- Added option to choose which formants to plot.
- Added a dataframe editor to add, edit, and delete data using a UI.

**Changes:**

- Updated dataframe methods: `clear_data`, `read`, and `write`.
- Modified Bark and Lobanov normalization methods to include all formant frequencies.

### VowSpace v1.3.0 Release Notes:

- Added ‘Audio Analysis Tools’, a separate window that the user can open through the VowSpace’s main user interface. Using this window, the user can read an audio file and get useful information about it such as intensity, pitch and formant frequencies.
- Added an IPA keyboard for convenience.
- Added the option to exclude a title for the plot.

### VowSpace v1.2.0 Release Notes:

- The initial release for Mac.
- Fixed a bug regarding the Bark Difference Metric method.
- Added more labeling options.

## About VowSpace

Vowel plotting and normalization are of utmost importance when dealing with data for many subfields of linguistics, and the absence of a user-friendly application for these specific purposes has led to the emergence of VowSpace as a solution to this gap.

## Vowel Plotting in VowSpace

VowSpace uses the Matplotlib (3.8.2) (Hunter, 2007) library to draw a canvas and visualize the data. When plotting vowel formants, VowSpace utilizes a rectangular template with f1 value on the rightmost side and f2 value on the bottommost side of the screen with rulers on the opposite sides of the values. The vowels that belong to different sources are represented with points with different colors.

## Vowel Normalization in VowSpace

VowSpace also provides options for normalizing the vowel formants under the “Normalization Settings” menu. In the latest stage of development, two normalization methods have been implemented to the application. The first method is an implementation of the Lobanov normalization method put forward by Lobanov (1971) by Nearey (1977) and Adank et al. (2004). The second one is the Bark Difference Metric by Traunmüller (1997). Both methods have been implemented to Python by Remirez (2022).

**Lobanov:**
```
F_n[V] = (F_n[V] – MEAN_n) / S_n
```

**Bark:**
```
Z_i = 26.81 / (1 + (1960 / F_i)) – 0.53
```
![norm](https://alicagankaya.com/wp-content/uploads/2024/03/Gelfer-Bennett-scaled.jpg)

![norm1](https://alicagankaya.com/wp-content/uploads/2024/03/Gelfer-Bennett-Bark.png)

![norm2](https://alicagankaya.com/wp-content/uploads/2024/03/Gelfer-Bennett-Lobanov-Normalized-scaled.jpg)

## Audio Analysis Tools

Audio Analysis Tools is a separate window that the user can access through the VowSpace’s main user interface. Then the user can read an audio file and get useful information about it such as intensity, pitch and vowel formant frequencies.

In the most current stage of development, the user is able to add the formant frequencies on any given t to the VowSpace interface by right-clicking on the plot on the audio analysis window.

![aat](https://alicagankaya.com/wp-content/uploads/2024/07/a3-2048x943.jpg)
Intensity

![aat1](https://alicagankaya.com/wp-content/uploads/2024/07/a2-2048x943.jpg)
Pitch

![aat2](https://alicagankaya.com/wp-content/uploads/2024/07/a4-2048x943.jpg)
Vowel Formant Frequencies

## DataFrame Editor

DataFrame Editor is a separate window to make small adjustments on the data that you’re working on without relying on any other application. When you use the ‘Save Changes’ function, the scatterplot automatically updates with the latest data. The altered data can also be saved as a separate .csv, .xls, or .xlsx file through the ‘Save Data As…’ action.

![dfeditor](https://alicagankaya.com/wp-content/uploads/2024/07/Screenshot-2024-07-30-at-17.41.33.png)
DataFrame Editor UI

## Data Table Format

The minimum data table for any data to be read by VowSpace is as follows:

```
vowel   f1   f2   speaker
/æ/     123  1234 Markus
```

The only necessary rows are ‘vowel’, ‘f1’, ‘f2’, and ‘speaker’. When any data is inputted through the user interface, a dataframe is created with this information. Columns like ‘bark_f1’ for the Bark metric, logarithmic values like ‘log_f1’ and z-scores like ‘zsc_f1’ are also supported.

---

I am not formally trained as a programmer and am the sole developer of this application, so there may be bugs, and the code might appear amateurish. VowSpace is still in development, and I am continuously adding new features as I learn new methods and techniques. I am doing my best to keep VowSpace updated and actively invite researchers to try it out and provide feedback. However, please double-check the output provided by VowSpace before using it in your research.

---

For more information, examples, and to download the application, visit the [VowSpace page](https://alicagankaya.com/vowspace/).

You can also find the source code on [GitHub](https://github.com/alicagank/VowSpace).

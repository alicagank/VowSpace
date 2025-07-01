# VowSpace: A vowel formant analysis application

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

## References

- Aydın, Ö., & Uzun, İ. P. (2020). Ünlü formant normalizasyonu: R programlama dilinde bir uygulama. In İ. P. Uzun (Ed.), *Kuramsal ve uygulamalı sesbilim* (pp. 297–322). Seçkin Yayıncılık.

- Bladon, R. A. W., Henton, C. G., & Pickering, J. B. (1984). Towards an auditory theory of speaker normalization. *Language & Communication, 4*(1), 59–69. [https://doi.org/10.1016/0271-5309(84)90019-3](https://doi.org/10.1016/0271-5309(84)90019-3)

- Boersma, P. (2001). Praat, a system for doing phonetics by computer. *Glot International, 5*(9/10), 341–345.

- Clopper, C. G. (2009). Computational methods for normalizing acoustic vowel data for talker differences. *Language and Linguistics Compass, 3*(6), 1430–1442. [https://doi.org/10.1111/j.1749-818X.2009.00165.x](https://doi.org/10.1111/j.1749-818X.2009.00165.x)

- Fant, G. (1975). Non-uniform vowel normalization. *Speech Transmission Laboratory Quarterly Progress and Status Report, 16*, 1–19.

- Gelfer, M. P., & Bennett, Q. E. (2013). Speaking Fundamental Frequency and Vowel Formant Frequencies: Effects on Perception of Gender. *Journal of Voice, 27*(5), 556–566. [https://doi.org/10.1016/j.jvoice.2012.11.008](https://doi.org/10.1016/j.jvoice.2012.11.008)

- Harris, C. R., et al. (2020). Array programming with NumPy. *Nature, 585*(7825), 357–362. [https://doi.org/10.1038/s41586-020-2649-2](https://doi.org/10.1038/s41586-020-2649-2)

- Heeringa, W., & Van de Velde, H. (2018). Visible Vowels: a Tool for the Visualization of Vowel Variation. In *Proceedings CLARIN Annual Conference 2018*, Pisa, Italy. CLARIN ERIC.

- Hunter, J. D. (2007). Matplotlib: A 2D Graphics Environment. *Computing in Science & Engineering, 9*(3), 90–95. [https://doi.org/10.1109/MCSE.2007.55](https://doi.org/10.1109/MCSE.2007.55)

- Jadoul, Y., Thompson, B., & de Boer, B. (2018). Introducing Parselmouth: A Python interface to Praat. *Journal of Phonetics, 71*, 1–15. [https://doi.org/10.1016/j.wocn.2018.07.001](https://doi.org/10.1016/j.wocn.2018.07.001)

- Jones, D. (1917). Speech sounds: Cardinal vowels. *The Gramophone*.

- Joos, M. (1948). Acoustic phonetics. *Language, 23*, 5–136.

- Klatt, D. H. (1989). Review of selected models of speech perception. In W. Marlsen-Wilson (Ed.), *Lexical representation and process* (pp. 169–226). MIT Press.

- Ladefoged, P., & Broadbent, D. E. (1957). Information conveyed by vowels. *The Journal of the Acoustical Society of America, 29*(1), 98–104. [https://doi.org/10.1121/1.1908694](https://doi.org/10.1121/1.1908694)

- Pfitzinger, H. R., & Niebuhr, O. (2011). Historical development of phonetic vowel systems: The last 400 years. *ICPhS XVII*, 160–163.

- R Core Team. (2021). *R: A language and environment for statistical computing* [Software]. R Foundation for Statistical Computing, Vienna, Austria.

- Remirez, E. (2022, October 20). Vowel plotting in Python. In *Linguistics Methods Hub*. Zenodo. [https://doi.org/10.5281/zenodo.7232005](https://doi.org/10.5281/zenodo.7232005)

- Studdert-Kennedy, M. (1964). The perception of speech. In T. A. Sebeok (Ed.), *Current trends in linguistics* (pp. 2349–2385). Mouton.

- Thomas, E. R., & Kendall, T. (2007). NORM: The vowel normalization and plotting suite. [Online Resource](http://ncslaap.lib.ncsu.edu/tools/norm/)

- The pandas development team. (2024). *pandas-dev/pandas: Pandas (v2.2.2)*. Zenodo. [https://doi.org/10.5281/zenodo.10957263](https://doi.org/10.5281/zenodo.10957263)

- Van Rossum, G., & Drake Jr., F. L. (1995). *Python reference manual*. Centrum voor Wiskunde en Informatica Amsterdam.

- Virtanen, P., et al. (2020). SciPy 1.0: fundamental algorithms for scientific computing in Python. *Nature Methods, 17*(3), 261–272. [https://doi.org/10.1038/s41592-019-0686-2](https://doi.org/10.1038/s41592-019-0686-2)

- Watt, D., Fabricius, A. H., & Kendall, T. (2010). More on vowels: Plotting and normalization. In *Sociophonetics: A Student’s Guide* (pp. 107–118). Routledge.

---

## Acknowledgement

I am not formally trained as a programmer and am the sole developer of this application, so there may be bugs, and the code might appear amateurish. VowSpace is still in development, and I am continuously adding new features as I learn new methods and techniques. I am doing my best to keep VowSpace updated and actively invite researchers to try it out and provide feedback. However, please double-check the output provided by VowSpace before using it in your research.

---

## Citation

You can cite VowSpace as:

- Kaya, A. Ç. (2024). VowSpace: A Vowel Formant Analysis Application [Poster presentation]. 37th National Linguistics Congress, Kocaeli, Türkiye. The Linguistics Association.

---

For more information, examples, and to download the application, visit the [VowSpace page](https://alicagankaya.com/vowspace/).

You can also find the source code on [GitHub](https://github.com/alicagank/VowSpace).

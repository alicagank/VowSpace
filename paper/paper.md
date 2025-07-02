---
title: 'VowSpace: A vowel formant analysis tool for phonetic research'
tags:
  - phonetics
  - formant analysis
  - vowel normalization
  - data visualization
  - linguistics
authors:
  - name: Ali Çağan Kaya
    orcid: 0009-0007-9386-9766
    affiliation: 1
affiliations:
 - name: Hacettepe University, Department of English Linguistics, Ankara, Türkiye
   index: 1
date: 2025-07-03
bibliography: paper.bib
---

# Summary

Vowel formant frequency varies by vowel and speaker, and plays a crucial role in phonological and sociolinguistic analysis. These frequencies reveal language-specific traits. The first and second formants (F1 and F2) relate to vowel height and backness, providing a robust acoustic basis for distinguishing vowel categories [@peterson1952; @ladefoged2014]. Measuring and comparing formant frequencies is key in phonetics, dialectology, sociolinguistics, speech technology, and second language acquisition. 

However, raw formant values are influenced by anatomical factors such as vocal tract length, age, and gender, making direct comparison across speakers problematic. To address this, various normalization techniques have been developed to reduce inter-speaker variability while preserving meaningful linguistic contrasts [@lobanov1971; @adank2004; @disner1980].

Visualizing vowel formants—typically via F1-F2 scatterplots—is a widely used method for exploring vowel inventories, diachronic change, and sociophonetic variation. Yet, most visualization workflows depend on scripting tools or software with steep learning curves, limiting accessibility for non-programmers or students.

# Statement of need

**VowSpace** is an open-source desktop application for acquiring, visualizing, normalizing, comparing and analyzing vowel sounds from audio files and/or spreadsheets. It provides an intuitive graphical interface for exploring vowel spaces across speakers and groups, supporting a variety of normalization methods including the Bark Difference Metric, Lobanov, Nearey 1 and 2, as well as Bark, Log, Mel, and Erb transformations.

VowSpace addresses the limitations of manual plotting and high-barrier scripting environments by offering:

- Simple data import from CSV or Excel spreadsheets,
- Graphical plotting of F1 vs. F2 with speaker metadata,
- Vowel normalization using Lobanov, Bark, and z-score methods,
- Exportable figures suitable for publication,
- A command-line interface (CLI) mode for batch processing,
- Audio analysis tools for acquiring vowel formants through spectrograms.

Existing tools such as `phonR`, `vowelPlot`, or Praat offer similar capabilities, but either require programming knowledge or lack streamlined GUIs for efficient exploration. VowSpace bridges this gap with a user-friendly interface suitable for researchers in phonetics, sociolinguistics, dialectology, and second language research, as well as for teaching applications.

# Acknowledgements

Development of this software was supported by mentorship from:

Dr. Emre Yağlı (Hacettepe University), for guidance on Turkish vowel formant research.

This project was developed independently with dedicated funding from the Scientific and Technological Research Council of Turkey (TÜBİTAK).

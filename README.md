# Vowel Space Visualizer
An application designed for visualizing vowels. With data acquired from tools like Praat, you can visualize a dataset or compare datasets from different sources—whether across languages or individuals (e.g., two different languages, three idiolects).

I developed this program as a creative diversion while getting one of my phonetics homeworks done. The task involved manually inputting data into Excel and adhering to specific guidelines to construct a scatterplot resembling a vowel space.

I've provided two different scripts for your convenience. The first script is a standalone Python application enabling you to generate a scatterplot or compare different vowel spaces by inputting or importing data. The second program (in the Vsv_Python_R folder), consisting of a Python interface, facilitates the creation of a .csv document containing the entered data. Subsequently, an R script reads this dataset, generating a comprehensive scatterplot based on the provided information.

## Overview

A Python-based application that offers a user-friendly interface to work on phonetic data effortlessly. Whether you're a linguistics student or a researcher, this tool provides a convenient way to visualize and analyze the formants of vowels as well as sociolinguistics data.

## Features

- **Reading Data from External Sources**: Read data from any .xlsx file.

- **Data Input**: Easily input new data by pressing the "Add Data" button or using the "Enter" key.

- **Data Correction**: Correct errors by undoing the latest input with the "Undo" button or the "Ctrl (Command) + Z" shortcut.

- **Save Scatterplots**: Save the visualized data as a scatterplot as JPEG or PNG using the "Save Scatterplot" function or the "Ctrl (Command) + S" shortcut.

- **Save Data New Data**: Save a dataset that you worked on as a .xlsx file.

- **Start Fresh**: Use the "Clear Data" function to start over and input or import new data.

- **Data Normalization**: You can use the Data Settings to normalize data or convert Hz values to Bark.

## Usage

1. Clone the repository to your local machine.

2. If you are importing data from a document, it needs to have columns for "F1", "F2" and "speaker".

```bash
git clone https://github.com/alicagank/vowelspacevisualizer.git
```

## License

GNU General Public License v3.0

## Credits

This application was developed by Ali Çağan Kaya as part of a linguistic project at Hacettepe University, Turkey. If you find this tool useful and decide to modify or publish it, kindly give credit to the original author.

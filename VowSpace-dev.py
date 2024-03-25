## This is the development version of VowSpace.
## There might be bugs.
## Beware of the bügs, they bite.
## A büg once bit my sister... No realli!
## Mynd you, büg bites Kan be pretti nasti...

import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from parselmouth import Sound
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib import colormaps
from scipy.spatial import ConvexHull
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout,
    QGridLayout, QFileDialog, QMessageBox, QMenu, QMenuBar, QAction, QCheckBox
)
from PyQt5.QtCore import Qt, QTimer

class VowelSpaceVisualizer(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

        self.resize_timer = QTimer()
        self.resize_timer.timeout.connect(self.delayed_update_scatterplot)

    def initUI(self):
        # Create widgets
        self.create_widgets()

        # Set layout
        self.set_layout()

        # Set initial state
        self.data = pd.DataFrame(columns=["vowel", "F1", "F2", "speaker"])
        self.setWindowTitle("VowSpace V.1.2")

        self.create_menu_bar()

        self.resizeEvent = self.custom_resize_event

    def create_menu_bar(self):
        menubar = QMenuBar(self)

        # File menu
        file_menu = menubar.addMenu('File')

        save_action = self.create_action('Save', self.save_scatterplot_auto, Qt.CTRL + Qt.Key_S)
        save_as_action = self.create_action('Save As...', self.save_scatterplot, Qt.CTRL + Qt.SHIFT + Qt.Key_S)
        save_data_action = self.create_action('Save Data As...', self.save_data_to_excel)
        import_data_action = self.create_action('Import Data from Excel', self.import_data_from_excel)

        file_menu.addAction(save_action)
        file_menu.addAction(save_as_action)
        file_menu.addAction(save_data_action)
        file_menu.addAction(import_data_action)

        # Edit menu
        edit_menu = menubar.addMenu('Edit')

        undo_action = self.create_action('Undo', self.undo_last_data, Qt.CTRL + Qt.Key_Z)
        edit_menu.addAction(undo_action)

        # Settings menu
        settings_menu = menubar.addMenu('Settings')

        # Visualization Settings submenu
        visualization_settings_menu = settings_menu.addMenu('Visualization Settings')

        # Data Settings submenu
        data_settings_menu = settings_menu.addMenu('Data Settings')

        # Connect Data with Polygons action
        self.connect_data_action = self.create_action('Connect Data with Polygons', self.update_scatterplot,
                                                      format='png', checkable=True)
        visualization_settings_menu.addAction(self.connect_data_action)

        # Show labels or not submenu
        labels_submenu = QMenu('Show Labels', self)

        # Choice 1: Show Labels for F Values
        self.checkbox_show_labels_f = self.create_action('Show Labels for F Values', self.update_scatterplot,
                                                              format='png', checkable=True)
        labels_submenu.addAction(self.checkbox_show_labels_f)

        # Choice 2: Show Labels for Vowels
        self.checkbox_show_labels_vowel = self.create_action('Show Labels for Vowels', self.update_scatterplot,
                                                            format='png', checkable=True)
        labels_submenu.addAction(self.checkbox_show_labels_vowel)

        # Choice 3: Show Labels for Speakers
        self.checkbox_show_labels_speaker = self.create_action('Show Labels for Speakers', self.update_scatterplot,
                                                              format='png', checkable=True)
        labels_submenu.addAction(self.checkbox_show_labels_speaker)

        # Adds another submenu under Show Data Labels
        visualization_settings_menu.addMenu(labels_submenu)

        # Show legend or not
        self.checkbox_show_legend = self.create_action('Show Legend', self.update_scatterplot,
                                                       format='png', checkable=True)
        visualization_settings_menu.addAction(self.checkbox_show_legend)

        # Show grids or not
        self.checkbox_show_grids = self.create_action('Show Grids', self.update_scatterplot,
                                                      format='png', checkable=True)
        visualization_settings_menu.addAction(self.checkbox_show_grids)

        # Barkify
        self.checkbox_barkify = self.create_action('Barkify', self.barkify,
                                                   format='png', checkable=True)
        data_settings_menu.addAction(self.checkbox_barkify)

        # Lobanov Normalization
        self.checkbox_normalize_lobanov = self.create_action('Lobanov Normalization', self.lobify,
                                                        format='png', checkable=True)
        data_settings_menu.addAction(self.checkbox_normalize_lobanov)

        self.layout().setMenuBar(menubar)

    def create_action(self, text, function, shortcut=None, format=None, checkable=False):
        action = QAction(text, self)
        action.triggered.connect(lambda: function(format) if format else function())
        action.setCheckable(checkable)
        if shortcut:
            action.setShortcut(shortcut)
        return action

    def create_widgets(self):

        # The input boxes
        self.label_vowel = QLabel('Vowel/Lexset/Word:')
        self.edit_vowel = QLineEdit()

        self.label_F1 = QLabel('F1 Value:')
        self.edit_F1 = QLineEdit()

        self.label_F2 = QLabel('F2 Value:')
        self.edit_F2 = QLineEdit()

        self.label_speaker = QLabel('Speaker:')
        self.edit_speaker = QLineEdit()

        self.label_title = QLabel('Add Title:')
        self.edit_title = QLineEdit()

        self.checkbox_no_title = QCheckBox('No Title')

        # The buttons that trigger those actions
        self.button_add_data = self.create_button('Add Data', self.add_data, Qt.Key_Return)
        self.button_clear_data = self.create_button('Clear Data', self.clear_data)
        self.button_update_scatterplot = self.create_button('Update Scatterplot', self.update_scatterplot)
        # Prosodic Analysis Tools class
        self.button_prosodic_analysis_tools = self.create_button('Prosodic Analysis Tools', self.prosodic_analysis_tools)

        self.figure, self.ax = plt.subplots(figsize=(8, 6))
        self.canvas = FigureCanvas(self.figure)

    def update_input_fields_prosodic(self, f1, f2, speaker_name):
        # Update speaker's name
        self.edit_speaker.setText(str(speaker_name))

        # Update formant values (convert to string with maximum 3 decimal places)
        self.edit_F1.setText("{:.3f}".format(f1))
        self.edit_F2.setText("{:.3f}".format(f2))

        # Activate and bring VowelSpaceVisualizer window to focus
        self.activateWindow()
        self.raise_()

    def set_layout(self):
        layout = QVBoxLayout()

        # The placements of the UI elements
        input_grid_layout = QGridLayout()
        input_grid_layout.addWidget(self.label_vowel, 0, 0)
        input_grid_layout.addWidget(self.edit_vowel, 0, 1)
        input_grid_layout.addWidget(self.label_F1, 1, 0)
        input_grid_layout.addWidget(self.edit_F1, 1, 1)
        input_grid_layout.addWidget(self.label_F2, 2, 0)
        input_grid_layout.addWidget(self.edit_F2, 2, 1)
        input_grid_layout.addWidget(self.label_speaker, 3, 0)
        input_grid_layout.addWidget(self.edit_speaker, 3, 1)

        layout.addLayout(input_grid_layout)

        title_layout = QHBoxLayout()
        title_layout.addWidget(self.label_title)
        title_layout.addWidget(self.edit_title)
        title_layout.addWidget(self.checkbox_no_title)

        layout.addLayout(title_layout)

        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(self.button_add_data)
        buttons_layout.addWidget(self.button_clear_data)
        buttons_layout.addWidget(self.button_update_scatterplot)
        buttons_layout.addWidget(self.button_prosodic_analysis_tools)

        layout.addLayout(buttons_layout)

        layout.addWidget(self.canvas)

        self.setLayout(layout)

    def create_button(self, text, function, shortcut=None):
        button = QPushButton(text, self)
        button.clicked.connect(function)
        if shortcut:
            button.setShortcut(shortcut)
        return button

    # Adding data functionality
    def add_data(self):
        if not self.validate_input_data():
            return

        vowel = self.edit_vowel.text()
        F1 = float(self.edit_F1.text())
        F2 = float(self.edit_F2.text())
        speaker = self.edit_speaker.text() if self.edit_speaker.text() else ''

        new_data = pd.DataFrame({"vowel": [vowel], "F1": [F1], "F2": [F2], "speaker": [speaker]}) if speaker else \
                   pd.DataFrame({"vowel": [vowel], "F1": [F1], "F2": [F2]})

        self.data = pd.concat([self.data, new_data], ignore_index=True)

        self.clear_input_fields()

        self.edit_vowel.setFocus()
        self.update_scatterplot()

    # Automatically clears the input fields after adding data
    def clear_input_fields(self):
        self.edit_vowel.clear()
        self.edit_F1.clear()
        self.edit_F2.clear()
        self.edit_speaker.clear()

    # Validates the data to be added - or else the program crashes.
    def validate_input_data(self):
        if not all([self.edit_vowel.text(), self.edit_F1.text(), self.edit_F2.text()]):
            self.show_error_message("Please fill in all the required fields.")
            return False

        try:
            F1 = float(self.edit_F1.text())
            F2 = float(self.edit_F2.text())
        except ValueError:
            self.show_error_message("Invalid numeric input for F1 or F2.")
            return False

        return True

    # The layout and initiation of the error messages
    def show_error_message(self, message):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setWindowTitle("Happy Accident!")
        msg_box.setText(message)
        msg_box.exec_()

    # Deletes the last inputted data from the dataframe
    def undo_last_data(self):
        if not self.data.empty:
            self.data = self.data.iloc[:-1]
            self.update_scatterplot()

    # Creates the scatterplot
    def update_scatterplot(self, format=None):
        self.ax.clear()

        markers = '.'  # Use a single marker for all vowels (.)
        vowel_markers = {v: markers for i, v in enumerate(self.data['vowel'].unique())}

        speaker_colors = {speaker: colormaps['viridis'](i / len(self.data['speaker'].unique()))
                          for i, speaker in enumerate(self.data['speaker'].unique())}

        # Checks if either the Barkify or Lobanov Normalization are checked on the Data Settings submenu and changes the f1_column and f_2 column accordingly
        if self.checkbox_normalize_lobanov.isChecked() and not self.checkbox_barkify.isChecked():
            f1_column, f2_column = 'zsc_F1', 'zsc_F2'
        elif self.checkbox_barkify.isChecked() and not self.checkbox_normalize_lobanov.isChecked():
            f1_column, f2_column = 'bark_F1', 'bark_F2'
        elif self.checkbox_barkify.isChecked() and self.checkbox_normalize_lobanov.isChecked():
            # Shows an error message if both checkboxes are checked
            self.show_error_message("Cannot apply both Barkify and Lobanov normalizations' transformations simultaneously.")
            return
        else:
            f1_column, f2_column = 'F1', 'F2'

        for v in self.data['vowel'].unique():
            subset = self.data[self.data['vowel'] == v]
            self.ax.scatter(
                subset[f2_column], subset[f1_column],  # Use selected F1 and F2 columns
                marker=vowel_markers[v],
                c=[speaker_colors[s] for s in subset['speaker']],
                label=v,
                alpha=0.8, edgecolors="w", linewidth=1
            )

            # Checks the state of the checkboxes for three choices under "Show Labels"
            show_labels_f = self.checkbox_show_labels_f.isChecked()
            show_labels_vowel = self.checkbox_show_labels_vowel.isChecked()
            show_labels_speaker = self.checkbox_show_labels_speaker.isChecked()

            if show_labels_f or show_labels_vowel or show_labels_speaker:  # Checks the state of the checkboxes
                for index, row in subset.iterrows():
                    label = ''

                    if show_labels_f and not show_labels_vowel and not show_labels_speaker: # Logical arguments for how the label system works
                        label += f"{f1_column}: {row[f1_column]:.2f}\n{f2_column}: {row[f2_column]:.2f}"

                    if show_labels_vowel and not show_labels_f and not show_labels_speaker:
                        label += f"{row['vowel']}"

                    if show_labels_speaker and not show_labels_f and not show_labels_vowel:
                        label += f"{row['speaker']}"

                    if show_labels_f and show_labels_vowel and not show_labels_speaker:
                        label += f"{row['vowel']}\n{f1_column}: {row[f1_column]:.2f}\n{f2_column}: {row[f2_column]:.2f}"

                    if show_labels_f and show_labels_speaker and not show_labels_vowel:
                        label += f"{row['speaker']}\n{f1_column}: {row[f1_column]:.2f}\n{f2_column}: {row[f2_column]:.2f}"

                    if show_labels_vowel and show_labels_speaker and not show_labels_f:
                        label += f"{row['vowel']}\n{row['speaker']}"

                    if show_labels_f and show_labels_vowel and show_labels_speaker:
                        label += f"{row['vowel']}\n{row['speaker']}\n{f1_column}: {row[f1_column]:.2f}\n{f2_column}: {row[f2_column]:.2f}"

                    if label:
                        self.ax.annotate(label, (row[f2_column], row[f1_column]), textcoords="offset points",
                                         xytext=(0, 5),
                                         ha='center', va='bottom', fontsize=8)


        if self.connect_data_action.isChecked() and len(self.data) >= 3: # Groups each and every data on the scatterplot according to the speaker and connects them with a convex hull polygon
            for speaker, group in self.data.groupby("speaker"):
                points = np.array([group[f2_column], group[f1_column]]).T
                if len(points) >= 3:
                    hull = ConvexHull(points)
                    polygon = plt.Polygon(points[hull.vertices], closed=True, alpha=0.2, label=speaker,
                                          facecolor=speaker_colors[speaker])
                    self.ax.add_patch(polygon)

        # Edits the title according to self.edit_title()
        custom_title = self.edit_title.text()
        if self.checkbox_no_title.isChecked():
            self.ax.set_title("", pad=25)  # Set an empty title if the checkbox is checked
        else:
            self.ax.set_title(custom_title if custom_title else "Vowel Space(s)", pad=25)

        show_legend = self.checkbox_show_legend.isChecked() # Checks if self.checkbox_show_legend() is checked and shows the legend accordingly

        if show_legend:
            self.ax.legend(loc='lower left', bbox_to_anchor=(1.05, 0))
        else:
            self.ax.legend().set_visible(False)

        show_grid = self.checkbox_show_grids.isChecked()

        # Set zorder value for the scatter plot
        scatter_zorder = 2

        if show_grid:
            # Draw grid lines behind the scatter plot by setting zorder
            self.ax.grid(True, linestyle='--', linewidth=0.5, zorder=scatter_zorder - 1)
        else:
            self.ax.grid(False)

        # Sets labels for the axes
        self.ax.set_xlabel("F2")
        self.ax.set_ylabel("F1")

        # Sets the position of the rulers
        self.ax.yaxis.tick_right()
        self.ax.xaxis.tick_top()

        # Inverts the axes to resemble vowel space
        plt.gca().invert_xaxis()
        plt.gca().invert_yaxis()

        # Positions them
        self.ax.xaxis.set_label_position("bottom")
        self.ax.xaxis.set_ticks_position("top")
        self.ax.yaxis.set_label_position("left")
        self.ax.yaxis.set_ticks_position("right")

        # Uses the tight_layout(), minimizes the gaps between the window and the scatterplot
        self.figure.tight_layout()
        self.canvas.draw()


    # Bark Difference Metric - Zi = 26.81/(1+1960/Fi) - 0.53 (Traunmüller, 1997)
    def barkify(self, arg):
        formants = ['F1', 'F2']

        bark_formula = lambda y: 26.81 / (1 + 1960 / y) - 0.53

        for formant in formants:
            name = f"bark_{formant}"

            if name not in self.data.columns:  # Check if the column already exists
                col = self.data[formant].apply(bark_formula)
                self.data[name] = col

        self.update_scatterplot()

    # Cite: Remirez, Emily. 2022, October 20. Vowel plotting in Python. Linguistics Methods Hub. (https://lingmethodshub.github.io/content/python/vowel-plotting-py). doi: 10.5281/zenodo.7232005

    # Lobanov's method was one of the earlier vowel-extrinsic formulas to appear, but it remains among the best.
    # Implementation: Following Nearey (1977) and Adank et al. (2004), NORM uses the formula (see the General Note below):
    # Fn[V]N = (Fn[V] - MEANn)/Sn
    def lobify(self, arg):

        formants = ['F1', 'F2']  # Add more formants if needed
        group_column = 'speaker' # or vowel couldn't decide -- it was speaker.

        zscore = lambda x: (x - x.mean()) / x.std()

        for formant in formants:
            name = f"zsc_{formant}"

            if name not in self.data.columns:  # Check if the column already exists
                col = self.data.groupby([group_column])[formant].transform(zscore)
                self.data.insert(len(self.data.columns), name, col)

        self.update_scatterplot()

    # Cite: Remirez, Emily. 2022, October 20. Vowel plotting in Python. Linguistics Methods Hub. (https://lingmethodshub.github.io/content/python/vowel-plotting-py). doi: 10.5281/zenodo.7232005

    # Takes delay event into account when resizing the app to avoid lag
    def custom_resize_event(self, event):
        self.resize_timer.start(200)
        super().resizeEvent(event)

    # Takes delay event into account when resizing the scatterplot to avoid lag
    def delayed_update_scatterplot(self):
        self.resize_timer.stop()  # Stops the timer to ensure it only triggers once
        self.update_scatterplot()

        # Uses the timer to avoid lag - will return to that
        # self.resize_timer.stop()
        # self.update_scatterplot()

    # Clears all the data from the dataframe
    def clear_data(self):
        self.data = pd.DataFrame(columns=["vowel", "F1", "F2", "speaker"])
        self.update_scatterplot()

    # Allows the user to simply save whatever there is on the scatterplot quickly
    def save_scatterplot_auto(self):
        custom_title = self.edit_title.text() or "Vowel Space(s)"
        file_name = f"{custom_title}.jpg"

        if file_name:
            try:
                self.figure.savefig(file_name, format='jpeg', dpi=800)
                QMessageBox.information(self, "Success", "Scatterplot saved successfully.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error saving scatterplot: {str(e)}")

    # Lets the user to make further changes to the file to be saved
    def save_scatterplot(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Scatterplot", "",
                                                   "JPEG Files (*.jpg *.jpeg);;PNG Files (*.png);;All Files (*)",
                                                   options=options)

        if file_name:
            try:
                # Determine file format based on the selected file extension
                file_format = 'jpeg' if file_name.lower().endswith(('.jpg', '.jpeg')) else 'png'

                self.figure.savefig(file_name, format=file_format, dpi=800)
                QMessageBox.information(self, "Success", "Scatterplot saved successfully.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error saving scatterplot: {str(e)}")

    # Saves the current dataframe as an .xlsx file
    def save_data_to_excel(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog

        # Gets the title of the scatterplot
        custom_title = self.edit_title.text() or "Vowel Space(s)"

        # Prompts user for file name and include the scatterplot title
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Data as Excel", f"{custom_title}.xlsx",
                                                   "Excel Files (*.xlsx);;All Files (*)", options=options)

        if file_name:
            try:
                # Determine file format based on the selected file extension
                file_format = 'xls' if file_name.lower().endswith('.xls') else 'xlsx'

                self.data.to_excel(file_name, index=False, sheet_name='Sheet1', engine='openpyxl')
                QMessageBox.information(self, "Success", f"Data saved to {file_format} successfully.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error saving data to {file_format}: {str(e)}")

    # Imports data from an .xls or .xlsx file. The files should have columns named "vowel", "speaker", "F1" and "F2".
    def import_data_from_excel(self):
        self.clear_data() # Clears the already existing data on the dataframe before the importing

        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_name, _ = QFileDialog.getOpenFileName(self, "Import Data from Excel", "",
                                                   "Excel Files (*.xls *.xlsx);;All Files (*)", options=options)

        if file_name:
            try:
                # Leaving the na values as is creates problems
                new_data = pd.read_excel(file_name, na_values=['', 'NaN', 'nan', 'N/A', 'NA', 'n/a'])

                # Converts 'F1' and 'F2' columns to numeric
                new_data['F1'] = pd.to_numeric(new_data['F1'], errors='coerce')
                new_data['F2'] = pd.to_numeric(new_data['F2'], errors='coerce')

                # Sets 'speaker' column to an empty string if it doesn't exist
                if 'speaker' not in new_data.columns:
                    new_data['speaker'] = ''

                # Replaces empty values in 'speaker' column with a space character
                new_data['speaker'] = new_data['speaker'].fillna('N/A')

                # Drops rows with missing values after conversion
                new_data = new_data.dropna()

                self.data = pd.concat([self.data, new_data], ignore_index=True)
                self.update_scatterplot()
                QMessageBox.information(self, "Success", "Data imported from Excel successfully.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error importing data from Excel: {str(e)}")

    # Opens Prosodic Analysis Tools window.
    def prosodic_analysis_tools(self):
        # Create a new instance of ProsodicAnalysisToolsWindow if not open
        self.prosodic_tools_window = ProsodicAnalysisTool()
        self.prosodic_tools_window.show()

class ProsodicAnalysisTool(QWidget):
    def __init__(self):
        super().__init__()

        self.show_pitch = False  # Changed default to unchecked
        self.show_intensity = False  # Changed default to unchecked
        self.show_formants = False  # Changed default to unchecked

        # Store the reference to VowelSpaceVisualizer instance
        self.vowel_space_visualizer = vowel_space_visualizer

        self.initUI()

    def initUI(self):
        # Set up the layout for the Prosodic Analysis Tools window
        layout = QVBoxLayout()

        # Add the matplotlib canvas
        self.figure, self.ax = plt.subplots(figsize=(6, 9))
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

        # Create a QHBoxLayout for the labels in the same row
        labels_layout = QHBoxLayout()

        # Add a QLabel for audio title
        self.audio_title_label = QLabel()
        labels_layout.addWidget(self.audio_title_label)

        # Add a QLabel for sampling rate
        self.sampling_rate_label = QLabel()
        labels_layout.addWidget(self.sampling_rate_label)

        # Add a QLabel for cursor coordinates
        self.coordinates_label = QLabel()
        labels_layout.addWidget(self.coordinates_label)

        # Add the labels layout to the main layout
        layout.addLayout(labels_layout)

        # Add the "Read from Audio File" action to the menu
        self.create_menu_bar()

        # Set the layout
        self.setLayout(layout)
        self.setWindowTitle("Prosodic Analysis Tools")
        self.setGeometry(100, 100, 1200, 600)

        # Connect the motion_notify_event to update_cursor_coordinates
        self.canvas.mpl_connect('motion_notify_event', self.update_cursor_coordinates)
        # Connect the button_press_event to handle_click
        self.canvas.mpl_connect('button_press_event', self.handle_click)

    def create_menu_bar(self):
        menubar = QMenuBar(self)

        # Create File menu
        file_menu = menubar.addMenu('File')

        # Add the "Read from Audio File" action to the file menu
        read_audio_action = self.create_action('Read from Audio File', self.read_audio_file)
        file_menu.addAction(read_audio_action)

        # Create Options menu
        options_menu = menubar.addMenu('Options')

        # Add pitch toggle as a checkable menu item (unchecked by default)
        self.pitch_action = self.create_action('Show Pitch', self.toggle_pitch, checkable=True)
        self.pitch_action.setChecked(self.show_pitch)
        options_menu.addAction(self.pitch_action)

        # Add intensity toggle as a checkable menu item (unchecked by default)
        self.intensity_action = self.create_action('Show Intensity', self.toggle_intensity, checkable=True)
        self.intensity_action.setChecked(self.show_intensity)
        options_menu.addAction(self.intensity_action)

        # Add formatns toggle as a checkable menu item (unchecked by default)
        self.formants_action = self.create_action('Show Formants', self.toggle_formants, checkable=True)
        self.formants_action.setChecked(self.show_formants)
        options_menu.addAction(self.formants_action)

    def create_action(self, text, function, shortcut=None, checkable=False):
        action = QAction(text, self)
        action.triggered.connect(function)
        if shortcut:
            action.setShortcut(shortcut)
        if checkable:
            action.setCheckable(True)
        return action

    def update_cursor_coordinates(self, event):
        if event.inaxes:
            x, y = event.xdata, event.ydata
            self.coordinates_label.setText(f'Cursor Coordinates: x={x:.2f}, y={y:.2f}')

    def handle_click(self, event):
        x, y = event.xdata, event.ydata

        if event.inaxes and event.button == 3:
            # Extract formants and print frequencies for the x-coordinate
            f1_freqs = self.formants.get_value_at_time(1, x)
            f2_freqs = self.formants.get_value_at_time(2, x)

            # Audio title
            audio_title = os.path.splitext(os.path.basename(self.audio_file))[0]

            # print(f"F1: {f1_freqs} Hz, F2: {f2_freqs} Hz")

            # Update VowelSpaceVisualizer with the formant values
            self.vowel_space_visualizer.update_input_fields_prosodic(f1_freqs, f2_freqs, audio_title)

    def toggle_pitch(self):
        self.show_pitch = not self.show_pitch
        self.redraw_plots()

    def toggle_formants(self):
        self.show_formants = not self.show_formants
        self.redraw_plots()

    def toggle_intensity(self):
        self.show_intensity = not self.show_intensity
        self.redraw_plots()

    def redraw_plots(self):
        try:
            # Redraw the spectrogram
            self.draw_spectrogram(self.audio_file)

            # Redraw pitch if it should be shown and pitch data is available
            if self.show_pitch and self.pitch:
                self.draw_pitch(self.pitch)

            # Redraw intensity if it should be shown and intensity data is available
            if self.show_intensity and self.intensity:
                self.draw_intensity(self.intensity)

            # Redraw formants if it should be shown and formant data is available
            if self.show_formants and self.formants:
                self.draw_formants(self.formants)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error redrawing plots: {str(e)}")

    def read_audio_file(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Audio File", "",
                                                   "Audio Files (*.wav *.mp3 *.ogg);;All Files (*)", options=options)

        if file_name:
            try:
                # Store file name for later use.
                self.audio_file = file_name
                self.audio_title_label.setText(f'Audio Title: {os.path.basename(file_name)}')  # Update QLabel

                # Update the existing plot in the Prosodic Analysis Tools window
                self.draw_spectrogram(file_name)

                # Extract pitch information using Parselmouth
                # This has to stay here or it doesn't work for some fucking reason
                # Tried to move it to draw_pitch method without success
                snd = Sound(file_name)
                self.pitch = snd.to_pitch()

                # Extract intensity information using Parselmouth
                self.intensity = snd.to_intensity()

                # Extract formants
                self.formants = snd.to_formant_burg()

                # Display sampling rate information
                sampling_rate = snd.sampling_frequency
                self.sampling_rate_label.setText(f'Sampling Rate: {sampling_rate} Hz')

                # Call redraw_plots after draw_spectrogram
                self.redraw_plots()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error reading audio file: {str(e)}")

    def draw_spectrogram(self, audio_file, spectrogram=None, dynamic_range=70):
        try:
            if spectrogram is None:
                snd = Sound(audio_file)
                spectrogram = snd.to_spectrogram()

            # Plot the spectrogram
            plt.figure(self.figure.number)
            plt.clf()

            # Plot the audio waveform on top of the spectrogram
            plt.plot(snd.xs(), snd.values.T, color='black', alpha=0.5)
            plt.xlim([snd.xmin, snd.xmax])

            X, Y = spectrogram.x_grid(), spectrogram.y_grid()
            sg_db = 10 * np.log10(spectrogram.values)
            plt.pcolormesh(X, Y, sg_db, vmin=sg_db.max() - dynamic_range, cmap='binary')
            plt.ylim([spectrogram.ymin, spectrogram.ymax])
            plt.xlabel("time [s]")
            plt.ylabel("frequency [Hz]")

            self.canvas.draw()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error reading audio file: {str(e)}")

    def draw_intensity(self, intensity=None):
        try:
            if intensity:
                # Twin the axis for intensity
                ax_intensity = plt.gca().twinx()
                ax_intensity.plot(intensity.xs(), intensity.values.T, linewidth=3, color='white', label='Intensity')
                ax_intensity.plot(intensity.xs(), intensity.values.T, linewidth=1, color='black')
                ax_intensity.set_ylabel("intensity [dB]")
                ax_intensity.grid(False)
                ax_intensity.set_ylim(0)

                self.canvas.draw()
            else:
                QMessageBox.critical(self, "Error", f"Intensity data is not available: {str(e)}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error plotting intensity: {str(e)}")

    def draw_formants(self, formants=None):
        try:
            if formants:
                # Basically draws the F1 and F2 formants on the plot.
                plt.plot(formants.xs(), [formants.get_value_at_time(1, x) for x in formants.xs()], 'o', color='w',
                    markersize=3)
                plt.plot(formants.xs(), [formants.get_value_at_time(1, x) for x in formants.xs()], 'o', color='b',
                    markersize=1)
                plt.plot(formants.xs(), [formants.get_value_at_time(2, x) for x in formants.xs()], 'o', color='w',
                    markersize=3)
                plt.plot(formants.xs(), [formants.get_value_at_time(2, x) for x in formants.xs()], 'o', color='c',
                    markersize=1)

                self.canvas.draw()
            else:
                QMessageBox.critical(self, "Error", f"Formant data is not available: {str(e)}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error plotting formants: {str(e)}")

    def draw_pitch(self, pitch):
        try:
            if pitch:
                # Extract selected pitch contour, and replace unvoiced samples by NaN to not plot
                pitch_values = pitch.selected_array['frequency']
                pitch_values[pitch_values == 0] = np.nan

                # Twin the axis for pitch
                ax_pitch = plt.gca().twinx()
                ax_pitch.plot(pitch.xs(), pitch_values, 'o', markersize=2, color='white', label='Pitch')
                ax_pitch.plot(pitch.xs(), pitch_values, 'o', markersize=1)
                ax_pitch.grid(False)
                ax_pitch.set_ylim(0, pitch.ceiling)
                ax_pitch.set_ylabel("fundamental frequency [Hz]")

                self.canvas.draw()
            else:
                QMessageBox.critical(self, "Error", f"Pitch data is not available: {str(e)}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error plotting pitch: {str(e)}")

if __name__ == '__main__':
    app = QApplication(sys.argv)

    # Create an instance of VowelSpaceVisualizer
    vowel_space_visualizer = VowelSpaceVisualizer()

    # Create an instance of ProsodicAnalysisTool
    prosodic_analysis_tool = ProsodicAnalysisTool()

    vowel_space_visualizer.show()

    sys.exit(app.exec_())

    # VowSpace (Vowel Space Visualizer) v.1.3.0
    # Ali Çağan Kaya, under the GPL-3.0 license.
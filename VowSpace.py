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
from matplotlib.patches import Ellipse
from scipy.spatial import ConvexHull
from scipy.stats import chi2
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout,
    QGridLayout, QDialog, QFileDialog, QMessageBox, QGroupBox, QMenu, QMenuBar, QAction, QCheckBox, QTableWidget, QTableWidgetItem, QComboBox
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
        self.data = pd.DataFrame(columns=["vowel", "f0", "f1", "f2", "f3", "f4", "speaker"])
        self.setWindowTitle("VowSpace v1.4.2")

        self.create_menu_bar()

        self.resizeEvent = self.custom_resize_event

        self.resize(800, 800)
        self.setMinimumSize(800, 800)

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

        # Options menu
        options_menu = menubar.addMenu('Options')

        # Visualization Options submenu
        visualization_options_menu = options_menu.addMenu('Visualization Options')

        # Color grouping by speaker or vowel
        self.group_by_vowel_action = self.create_action('Group by Vowel', self.update_scatterplot, format='png',
                                                        checkable=True)
        visualization_options_menu.addAction(self.group_by_vowel_action)

        # Connect submenu under Visualization Options
        connect_menu = visualization_options_menu.addMenu('Connect')

        # actions to Connect submenu
        self.connect_ellipse_action = self.create_action('Connect with Ellipse(s)',
                                                                 self.update_scatterplot, format='png', checkable=True)
        connect_menu.addAction(self.connect_ellipse_action)

        self.connect_qhull_action = self.create_action('Connect with Qhull(s)', self.update_scatterplot,
                                                      format='png', checkable=True)
        connect_menu.addAction(self.connect_qhull_action)

        self.show_center_info_action = self.create_action('Show Center Label(s)', self.update_scatterplot, format='png',
                                                          checkable=True)
        connect_menu.addAction(self.show_center_info_action)

        # Data Options submenu
        data_options_menu = options_menu.addMenu('Data Options')

        # Show labels or not submenu
        labels_submenu = QMenu('Label Options', self)

        # Choice 1: Show Labels for F Values
        self.checkbox_show_labels_f = self.create_action('Show Labels for F Value(s)', self.update_scatterplot,
                                                         format='png', checkable=True)
        labels_submenu.addAction(self.checkbox_show_labels_f)

        # Choice 2: Show Labels for Vowels
        self.checkbox_show_labels_vowel = self.create_action('Show Labels for Vowel(s)', self.update_scatterplot,
                                                             format='png', checkable=True)
        labels_submenu.addAction(self.checkbox_show_labels_vowel)

        # Choice 3: Show Labels for Speakers
        self.checkbox_show_labels_speaker = self.create_action('Show Labels for Speaker(s)', self.update_scatterplot,
                                                               format='png', checkable=True)
        labels_submenu.addAction(self.checkbox_show_labels_speaker)

        # Adds another submenu under Show Data Labels
        visualization_options_menu.addMenu(labels_submenu)

        # Legend Options submenu
        legend_options_menu = visualization_options_menu.addMenu('Legend Options')

        # Show legend or not
        self.checkbox_show_legend = self.create_action('Show Legend', self.update_scatterplot, format='png',
                                                       checkable=True)
        legend_options_menu.addAction(self.checkbox_show_legend)

        # Show grids or not
        self.checkbox_show_grids = self.create_action('Show Grids', self.update_scatterplot, format='png',
                                                      checkable=True)
        visualization_options_menu.addAction(self.checkbox_show_grids)

        # Bark difference metric
        self.checkbox_normalize_bark = self.create_action('Bark Diff', self.diffBark, format='png',
                                                             checkable=True)
        data_options_menu.addAction(self.checkbox_normalize_bark)

        # Lobanov Normalization
        self.checkbox_normalize_lobanov = self.create_action('Lobanov Normalization', self.lobify, format='png',
                                                             checkable=True)
        data_options_menu.addAction(self.checkbox_normalize_lobanov)

        # Nearey1 Normalization
        self.checkbox_normalize_nearey1 = self.create_action('Nearey1 Normalization', self.Nearey1, format='png',
                                                             checkable=True)
        data_options_menu.addAction(self.checkbox_normalize_nearey1)

        # Nearey2 Normalization
        self.checkbox_normalize_nearey2 = self.create_action('Nearey2 Normalization', self.Nearey2, format='png',
                                                             checkable=True)
        data_options_menu.addAction(self.checkbox_normalize_nearey2)

        # Use Bark
        self.checkbox_use_bark = self.create_action('Bark Conversion', self.metricBark, format='png', checkable=True)
        data_options_menu.addAction(self.checkbox_use_bark)

        # Use Log
        self.checkbox_use_log = self.create_action('Log Conversion', self.normLog, format='png', checkable=True)
        data_options_menu.addAction(self.checkbox_use_log)

        # Use Mel
        self.checkbox_use_mel = self.create_action('Mel Conversion', self.normMel, format='png', checkable=True)
        data_options_menu.addAction(self.checkbox_use_mel)

        # Use Erb
        self.checkbox_use_erb = self.create_action('Erb Conversion', self.normErb, format='png', checkable=True)
        data_options_menu.addAction(self.checkbox_use_erb)

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

        self.label_f0 = QLabel('f0 Value:')
        self.edit_f0 = QLineEdit()

        self.label_f1 = QLabel('f1 Value:')
        self.edit_f1 = QLineEdit()

        self.label_f2 = QLabel('f2 Value:')
        self.edit_f2 = QLineEdit()

        self.label_f3 = QLabel('f3 Value:')
        self.edit_f3 = QLineEdit()

        self.label_f4 = QLabel('f4 Value:')
        self.edit_f4 = QLineEdit()

        self.checkbox_show_all_formants = QCheckBox('Show all formant input boxes')
        self.checkbox_show_all_formants.stateChanged.connect(self.toggle_formant_boxes)
        # Initially hide formant input boxes
        self.toggle_formant_boxes(self.checkbox_show_all_formants.checkState())

        self.label_speaker = QLabel('Speaker:')
        self.edit_speaker = QLineEdit()

        self.label_title = QLabel('Add Title:')
        self.edit_title = QLineEdit()

        self.checkbox_no_title = QCheckBox('No Title')
        self.checkbox_no_title.setChecked(True) # Thought this would be more efficient

        # The buttons that trigger those actions
        self.button_add_data = self.create_button('Add Data', self.add_data, Qt.Key_Return)
        self.button_clear_data = self.create_button('Clear Data', self.clear_data)
        self.button_update_scatterplot = self.create_button('Update Scatterplot', self.update_scatterplot)
        # Audio Analysis Tools class
        self.button_audio_analysis_tools = self.create_button('Audio Analysis Tools', self.audio_analysis_tools)
        # IPA keyboard button
        self.button_IPA = self.create_button('Show IPA', self.show_IPA)
        # Dataframe editor button
        self.button_open_df_editor = self.create_button('DataFrame Editor', self.open_df_editor)

        # Dropdown menus for selecting columns
        self.label_x_axis = QLabel('Y Axis:')
        self.dropdown_x_axis = QComboBox()
        self.dropdown_x_axis.addItems(["f0", "f1", "f2", "f3", "f4"])  # Add available columns
        self.dropdown_x_axis.setCurrentText("f1")  # Set default value to F1

        self.label_y_axis = QLabel('X Axis:')
        self.dropdown_y_axis = QComboBox()
        self.dropdown_y_axis.addItems(["f0", "f1", "f2", "f3", "f4"])  # Add available columns
        self.dropdown_y_axis.setCurrentText("f2")  # Set default value to F2

        self.figure, self.ax = plt.subplots(figsize=(8, 6))
        self.canvas = FigureCanvas(self.figure)

    def update_input_fields_audio(self, f1, f2, f3, f4, speaker_name):
        # Update speaker's name
        self.edit_speaker.setText(str(speaker_name))

        # Update formant values (convert to string with maximum 3 decimal places)
        #self.edit_F0.setText("{:.3f}".format(f0)) TODO: here.
        self.edit_f1.setText("{:.3f}".format(f1))
        self.edit_f2.setText("{:.3f}".format(f2))
        self.edit_f3.setText("{:.3f}".format(f3))
        self.edit_f4.setText("{:.3f}".format(f4))

        # Activate and bring VowelSpaceVisualizer window to focus
        self.activateWindow()
        self.raise_()

    def set_layout(self):
        layout = QVBoxLayout()

        # The placements of the UI elements
        input_grid_layout = QGridLayout()
        input_grid_layout.addWidget(self.label_vowel, 0, 0)
        input_grid_layout.addWidget(self.edit_vowel, 0, 1)
        input_grid_layout.addWidget(self.label_f0, 1, 0)
        input_grid_layout.addWidget(self.edit_f0, 1, 1)
        input_grid_layout.addWidget(self.label_f1, 2, 0)
        input_grid_layout.addWidget(self.edit_f1, 2, 1)
        input_grid_layout.addWidget(self.label_f2, 3, 0)
        input_grid_layout.addWidget(self.edit_f2, 3, 1)
        input_grid_layout.addWidget(self.label_f3, 4, 0)
        input_grid_layout.addWidget(self.edit_f3, 4, 1)
        input_grid_layout.addWidget(self.label_f4, 5, 0)
        input_grid_layout.addWidget(self.edit_f4, 5, 1)
        input_grid_layout.addWidget(self.label_speaker, 6, 0)
        input_grid_layout.addWidget(self.edit_speaker, 6, 1)

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
        buttons_layout.addWidget(self.button_audio_analysis_tools)
        buttons_layout.addWidget(self.button_IPA)
        buttons_layout.addWidget(self.button_open_df_editor)

        layout.addLayout(buttons_layout)

        axis_layout = QHBoxLayout()
        axis_layout.addWidget(self.label_x_axis)
        axis_layout.addWidget(self.dropdown_x_axis)
        axis_layout.addWidget(self.label_y_axis)
        axis_layout.addWidget(self.dropdown_y_axis)

        layout.addLayout(axis_layout)

        title_layout.addWidget(self.checkbox_show_all_formants)

        layout.addWidget(self.canvas)

        self.setLayout(layout)

    def create_button(self, text, function, shortcut=None):
        button = QPushButton(text, self)
        button.clicked.connect(function)
        if shortcut:
            button.setShortcut(shortcut)
        return button

    def toggle_formant_boxes(self, state):
        if state == Qt.Checked:
            # Show all formant input boxes
            self.label_f0.show()
            self.edit_f0.show()
            self.label_f3.show()
            self.edit_f3.show()
            self.label_f4.show()
            self.edit_f4.show()
        else:
            # Hide all formant input boxes
            self.label_f0.hide()
            self.edit_f0.hide()
            self.label_f3.hide()
            self.edit_f3.hide()
            self.label_f4.hide()
            self.edit_f4.hide()

    # Adding data functionality
    def add_data(self):
        if not self.validate_input_data():
            return

        vowel = self.edit_vowel.text()

        # Convert F0 to float or set to NaN if empty
        f0 = float(self.edit_f0.text()) if self.edit_f0.text() else np.nan

        # Convert F1 to float or set to NaN if empty
        f1 = float(self.edit_f1.text()) if self.edit_f1.text() else np.nan

        # Convert F2 to float or set to NaN if empty
        f2 = float(self.edit_f2.text()) if self.edit_f2.text() else np.nan

        # Convert F3 to float or set to NaN if empty
        f3 = float(self.edit_f3.text()) if self.edit_f3.text() else np.nan

        # Convert F4 to float or set to NaN if empty
        f4 = float(self.edit_f4.text()) if self.edit_f4.text() else np.nan

        speaker = self.edit_speaker.text() if self.edit_speaker.text() else ''

        new_data = pd.DataFrame(
            {"vowel": [vowel], "f0": [f0], "f1": [f1], "f2": [f2], "f3": [f3], "f4": [f4], "speaker": [speaker]}) if speaker else \
            pd.DataFrame({"vowel": [vowel], "f0": [f0], "f1": [f1], "f2": [f2], "f3": [f3], "f4": [f4]})

        self.data = pd.concat([self.data, new_data], ignore_index=True)

        self.clear_input_fields()

        self.edit_vowel.setFocus()
        self.update_scatterplot()

    # Automatically clears the input fields after adding data
    def clear_input_fields(self):
        self.edit_vowel.clear()
        self.edit_f0.clear()
        self.edit_f1.clear()
        self.edit_f2.clear()
        self.edit_f3.clear()
        self.edit_f4.clear()
        self.edit_speaker.clear()

    # Validates the data to be added - or else the program crashes.
    def validate_input_data(self):
        if not self.edit_vowel.text():
            self.show_error_message("Please enter a vowel.")
            return False

        try:
            f0 = float(self.edit_f0.text()) if self.edit_f0.text() else np.nan
            f1 = float(self.edit_f1.text()) if self.edit_f1.text() else np.nan
            f2 = float(self.edit_f2.text()) if self.edit_f2.text() else np.nan
            f3 = float(self.edit_f3.text()) if self.edit_f3.text() else np.nan
            f4 = float(self.edit_f4.text()) if self.edit_f4.text() else np.nan
        except ValueError:
            self.show_error_message("Invalid numeric input for an F value.")
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
        vowel_markers = {v: markers for v in self.data['vowel'].unique()}

        # Determine if we are coloring by speaker or by vowel
        if self.group_by_vowel_action.isChecked():
            group_by = 'vowel'
            unique_values = self.data['vowel'].unique()
        else:
            group_by = 'speaker'
            unique_values = self.data['speaker'].unique()

        colors = {
            value: plt.cm.viridis(i / len(unique_values))
            for i, value in enumerate(unique_values)
        }

        # Get selected columns from dropdown menus
        x_column = self.dropdown_x_axis.currentText()
        y_column = self.dropdown_y_axis.currentText()

        # Apply transformations if checkboxes are checked
        # Check if more than one normalization method is selected
        if sum([
            self.checkbox_use_bark.isChecked(),
            self.checkbox_normalize_bark.isChecked(),
            self.checkbox_normalize_lobanov.isChecked(),
            self.checkbox_normalize_nearey1.isChecked(),
            self.checkbox_normalize_nearey2.isChecked(),
            self.checkbox_use_log.isChecked(),
            self.checkbox_use_mel.isChecked(),
            self.checkbox_use_erb.isChecked(),
        ]) > 1:
            self.show_error_message(
                "Cannot apply two normalizations' transformations simultaneously.")
            return

        # Determine which normalization to apply
        if self.checkbox_use_bark.isChecked():
            x_column = f"bark_{x_column}"
            y_column = f"bark_{y_column}"
        elif self.checkbox_use_log.isChecked():
            x_column = f"log_{x_column}"
            y_column = f"log_{y_column}"
        elif self.checkbox_use_mel.isChecked():
            x_column = f"mel_{x_column}"
            y_column = f"mel_{y_column}"
        elif self.checkbox_use_erb.isChecked():
            x_column = f"erb_{x_column}"
            y_column = f"erb_{y_column}"
        elif self.checkbox_normalize_bark.isChecked():
            x_column = f"Z3_minus_Z2"
            y_column = f"Z3_minus_Z1"
        elif self.checkbox_normalize_lobanov.isChecked():
            x_column = f"zsc_{x_column}"
            y_column = f"zsc_{y_column}"
        elif self.checkbox_normalize_nearey1.isChecked():
            x_column = f"logmean_{x_column}"
            y_column = f"logmean_{y_column}"
        elif self.checkbox_normalize_nearey2.isChecked():
            x_column = f"slogmean_{x_column}"
            y_column = f"slogmean_{y_column}"

        # Check if selected columns exist in the data
        if x_column not in self.data.columns or y_column not in self.data.columns:
            QMessageBox.critical(self, "Error",
                                 f"Selected column(s) '{x_column}' or '{y_column}' do not exist in the dataset.")
            return

        for v in self.data['vowel'].unique():
            subset = self.data[self.data['vowel'] == v]

            # Check if x_column or y_column exist in subset
            if x_column not in subset.columns or y_column not in subset.columns:
                continue

            # Use the appropriate color mapping based on the selection
            color = [colors[val] for val in subset[group_by]]

            self.ax.scatter(
                subset[y_column], subset[x_column],  # Use selected columns
                marker=vowel_markers[v],
                c=color,
                label=v,
                alpha=0.8, edgecolors="w", linewidth=1
            )

            # Show labels based on checkbox states
            show_labels_f = self.checkbox_show_labels_f.isChecked()
            show_labels_vowel = self.checkbox_show_labels_vowel.isChecked()
            show_labels_speaker = self.checkbox_show_labels_speaker.isChecked()

            for index, row in subset.iterrows():
                label = ''

                if show_labels_f:
                    label += f"{x_column}: {row[x_column]:.2f}\n{y_column}: {row[y_column]:.2f}\n"

                if show_labels_vowel:
                    label += f"{row['vowel']}\n"

                if show_labels_speaker:
                    label += f"{row['speaker']}\n"

                # Add label if any information is present
                if label:
                    self.ax.annotate(label.strip(), (row[y_column], row[x_column]), textcoords="offset points",
                                     xytext=(0, 5), ha='center', va='bottom', fontsize=8)

        if self.connect_ellipse_action.isChecked():
            if self.group_by_vowel_action.isChecked():
                group_by = 'vowel'
            else:
                group_by = 'speaker'

            for key in self.data[group_by].unique():
                subset = self.data[self.data[group_by] == key]

                # Ensure the subset has enough data points and variability
                if len(subset) < 2 or subset[x_column].nunique() < 2 or subset[y_column].nunique() < 2:
                    continue

                # Calculate the mean and covariance of the data
                mean = [np.mean(subset[y_column]), np.mean(subset[x_column])]
                cov = np.cov(subset[y_column], subset[x_column])  # TODO: inverted axes

                # Eigenvalues and eigenvectors of the covariance matrix
                eigvals, eigvecs = np.linalg.eigh(cov)

                # Sort eigenvalues and corresponding eigenvectors
                order = eigvals.argsort()[::-1]
                eigvals, eigvecs = eigvals[order], eigvecs[:, order]

                # Scaling factor for the 67% confidence ellipse
                # https://joeystanley.com/blog/making-vowel-plots-in-r-part-1/#ellipses
                scale_factor = np.sqrt(chi2.ppf(0.67, df=2))

                # Calculate width and height of the ellipse
                width, height = 2 * scale_factor * np.sqrt(eigvals)

                # Calculate the angle of the ellipse
                angle = np.degrees(np.arctan2(*eigvecs[:, 0][::-1]))

                # Determine the color based on the current grouping
                ell_color = colors[key]

                # Define transparency
                alpha = 0.2

                # Create an ellipse
                ell = Ellipse(xy=(mean[0], mean[1]),
                              width=width, height=height,
                              angle=angle,
                              edgecolor=ell_color, fc=ell_color, lw=1, alpha=alpha)
                self.ax.add_patch(ell)

                # Add label to the center of the ellipse
                if self.show_center_info_action.isChecked():
                    self.ax.text(mean[0], mean[1], key, color='black', ha='center', va='center', fontsize=10)

        if self.connect_qhull_action.isChecked() and len(self.data) >= 3:
            if self.group_by_vowel_action.isChecked():
                group_by = 'vowel'
            else:
                group_by = 'speaker'

            for key, group in self.data.groupby(group_by):
                points = np.array([group[y_column], group[x_column]]).T

                if len(points) < 3:
                    continue

                if np.linalg.matrix_rank(points) < 2:
                    QMessageBox.critical(self, "Error",
                                         f"The input data for {group_by} '{key}' is less than 2-dimensional.")
                    continue

                try:
                    hull = ConvexHull(points)
                    polygon = plt.Polygon(points[hull.vertices], closed=True, alpha=0.2, label=key,
                                          facecolor=colors[key])
                    self.ax.add_patch(polygon)

                    # Calculate the centroid of the convex hull
                    centroid = np.mean(points[hull.vertices], axis=0)

                    # Add label to the center of the polygon
                    if self.show_center_info_action.isChecked():
                        self.ax.text(centroid[0], centroid[1], key, color='black', ha='center', va='center',
                                     fontsize=10)
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Qhull error for {group_by} '{key}': {str(e)}")

        custom_title = self.edit_title.text()
        if self.checkbox_no_title.isChecked():
            self.ax.set_title("", pad=25)
        else:
            self.ax.set_title(custom_title if custom_title else "Vowel Space(s)", pad=25)

        show_legend = self.checkbox_show_legend.isChecked()
        if show_legend:
            self.ax.legend(loc='lower left', bbox_to_anchor=(1.05, 0))
        else:
            self.ax.legend().set_visible(False)

        show_grid = self.checkbox_show_grids.isChecked()
        if show_grid:
            self.ax.grid(True, linestyle='--', linewidth=0.5)
        else:
            self.ax.grid(False)

        # Set labels for the axes, inverted
        '''custom_label_x = self.edit_label_x.text()
        custom_label_y = self.edit_label_y.text()
        if self.checkbox_custom_labels.isChecked():
            self.ax.set_xlabel(custom_label_x, pad=25)
            self.ax.set_ylabel(custom_label_y, pad=25)
        else:'''
        self.ax.set_xlabel(y_column)
        self.ax.set_ylabel(x_column)

        # Position the rulers
        self.ax.yaxis.tick_right()
        self.ax.xaxis.tick_top()

        # Invert axes to resemble vowel space
        # plt.gca().invert_xaxis()
        # plt.gca().invert_yaxis() this is very buggy and doesn't work consistently for some reason
        self.ax.invert_xaxis()
        self.ax.invert_yaxis()

        # Position the axes
        self.ax.xaxis.set_label_position("bottom")
        self.ax.xaxis.set_ticks_position("top")
        self.ax.yaxis.set_label_position("left")
        self.ax.yaxis.set_ticks_position("right")

        # Use tight_layout to minimize gaps between the window and the scatterplot
        self.figure.tight_layout()
        self.canvas.draw()

    # Bark Difference Metric - Zi = 26.81/(1+1960/Fi) - 0.53 (Traunmüller, 1997)
    def metricBark(self, arg):
        formants = [self.dropdown_x_axis.currentText(), self.dropdown_y_axis.currentText()]

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

    def diffBark(self, arg):
        # Define the formants
        formants = ['f1', 'f2', 'f3']

        # Ensure required columns are present in the DataFrame
        missing_columns = [formant for formant in formants if formant not in self.data.columns]
        if missing_columns:
            self.show_error_message(f"Missing columns: {', '.join(missing_columns)}")
            return

        # Define Bark conversion function
        def bark_conversion(f):
            return 26.81 / (1 + 1960 / f) - 0.53

        # Compute Bark values and add to DataFrame
        for formant in formants:
            bark_column_name = f"bark_{formant}"
            if bark_column_name not in self.data.columns:  # Create the column if it doesn't exist
                self.data[bark_column_name] = bark_conversion(self.data[formant])

        # Calculate Bark differences
        self.data['Z3_minus_Z1'] = self.data['bark_f3'] - self.data['bark_f1']
        self.data['Z3_minus_Z2'] = self.data['bark_f3'] - self.data['bark_f2']
        self.data['Z2_minus_Z1'] = self.data['bark_f2'] - self.data['bark_f1']

        # Update scatterplot or other UI elements
        self.update_scatterplot()

    def lobify(self, arg):
        formants = [self.dropdown_x_axis.currentText(), self.dropdown_y_axis.currentText()]

        group_column = 'speaker'

        zscore = lambda x: (x - x.mean()) / x.std()

        for formant in formants:
            name = f"zsc_{formant}"

            if name not in self.data.columns:  # Check if the column already exists
                col = self.data.groupby([group_column])[formant].transform(zscore)
                self.data[name] = col

        self.update_scatterplot()

    # Cite: Remirez, Emily. 2022, October 20. Vowel plotting in Python. Linguistics Methods Hub. (https://lingmethodshub.github.io/content/python/vowel-plotting-py). doi: 10.5281/zenodo.7232005


    # Cite: https://github.com/drammock/phonR/blob/master/R/phonR.R
    def Nearey1(self, arg, exp=False):
        formants = [self.dropdown_x_axis.currentText(), self.dropdown_y_axis.currentText()]
        group_column = 'speaker'

        def norm_logmean(f, group=None, exp=False):
            if f.shape[1] < 2:
                raise ValueError("Normalization method 'norm_logmean' requires at least two columns for formants.")

            if group is None:
                logmeans = np.log(f) - np.log(f.mean())
            else:
                grouped = f.groupby(group)
                logmeans = pd.DataFrame()
                for name, group_data in grouped:
                    group_logmeans = np.log(group_data) - np.log(group_data.mean())
                    logmeans = pd.concat([logmeans, group_logmeans], axis=0)
                logmeans = logmeans.sort_index()

            if exp:
                logmeans = np.exp(logmeans)

            return logmeans

        # Check if selected formants are valid
        if any(formant not in self.data.columns for formant in formants):
            raise ValueError("One or more selected formants are not present in the data.")

        # Extract the formant data
        formant_data = self.data[formants].copy()  # Select only the formant columns

        # Check if the DataFrame is empty
        if formant_data.empty:
            # Create columns with NaN values if the DataFrame is empty
            for formant in formants:
                name = f"logmean_{formant}"
                if name not in self.data.columns:
                    self.data[name] = np.nan  # Create the column with NaN values
            self.update_scatterplot()
            return

        # Apply normalization
        norm_data = norm_logmean(formant_data, group=self.data[group_column], exp=exp)

        # Overwrite existing columns with normalized data
        for formant in formants:
            name = f"logmean_{formant}"
            if name in self.data.columns:
                self.data[name] = norm_data[formant]  # Update the column
            else:
                self.data[name] = norm_data[formant]  # Create the column if it does not exist

        # Update scatterplot or other UI elements
        self.update_scatterplot()

    def Nearey2(self, exp=False):
        # Extract formants from dropdowns
        formants = [self.dropdown_x_axis.currentText(), self.dropdown_y_axis.currentText()]
        group_column = 'speaker'

        # Ensure at least two formants are selected
        if len(formants) < 2:
            raise ValueError("Normalization method 'Nearey2' requires at least two formants.")

        # Extract the formant data
        formant_data = self.data[formants]

        # Check if the DataFrame is empty
        if formant_data.empty:
            # Create columns with NaN values if the DataFrame is empty
            for formant in formants:
                name = f"slogmean_{formant}"
                if name not in self.data.columns:
                    self.data[name] = np.nan  # Create the column with NaN values
            self.update_scatterplot()
            return

        # Function to calculate shared log-mean normalization
        def norm_shared_logmean(f, group=None, exp=False):
            if group is None:
                # Implement the shared log-mean normalization
                logmeans = np.log(f) - np.mean(np.log(f), axis=0)
            else:
                f = pd.DataFrame(f)
                groups = f.groupby(group)
                logmeans = groups.apply(lambda x: np.log(x) - np.mean(np.log(x), axis=0))
                logmeans = logmeans.reset_index(drop=True)

            if exp:
                logmeans = np.exp(logmeans)
            return logmeans

        # Apply normalization
        norm_data = norm_shared_logmean(formant_data, group=self.data[group_column], exp=exp)

        # Overwrite existing columns with normalized data
        for i, formant in enumerate(formants):
            name = f"slogmean_{formant}"
            self.data[name] = norm_data.iloc[:, i]  # Update create the column

        # Update scatterplot or other UI elements
        self.update_scatterplot()

    def normLog(self, arg):
        # Extract formants from dropdowns
        formants = [self.dropdown_x_axis.currentText(), self.dropdown_y_axis.currentText()]

        # Check if selected formants are valid
        if any(formant not in self.data.columns for formant in formants):
            raise ValueError("One or more selected formants are not present in the data.")

        # Extract the formant data
        formant_data = self.data[formants].copy()  # Select only the formant columns

        # Apply normalization
        for formant in formants:
            name = f"log_{formant}"
            if name in self.data.columns:
                self.data[name] = np.log10(formant_data[formant])
            else:
                self.data[name] = np.log10(formant_data[formant])  # Create the column if it does not exist

        # Update scatterplot or other UI elements
        self.update_scatterplot()

    def normMel(self, arg):
        # Extract formants from dropdowns
        formants = [self.dropdown_x_axis.currentText(), self.dropdown_y_axis.currentText()]

        # Check if selected formants are valid
        if any(formant not in self.data.columns for formant in formants):
            raise ValueError("One or more selected formants are not present in the data.")

        # Extract the formant data
        formant_data = self.data[formants].copy()  # Select only the formant columns

        # Apply normalization
        for formant in formants:
            name = f"mel_{formant}"
            if name in self.data.columns:
                self.data[name] = 2595 * np.log10(1 + formant_data[formant] / 700)
            else:
                self.data[name] = 2595 * np.log10(
                    1 + formant_data[formant] / 700)  # Create the column if it does not exist

        # Update scatterplot or other UI elements
        self.update_scatterplot()

    def normErb(self, arg):
        # Extract formants from dropdowns
        formants = [self.dropdown_x_axis.currentText(), self.dropdown_y_axis.currentText()]

        # Check if selected formants are valid
        if any(formant not in self.data.columns for formant in formants):
            raise ValueError("One or more selected formants are not present in the data.")

        # Extract the formant data
        formant_data = self.data[formants].copy()  # Select only the formant columns

        # Apply normalization
        for formant in formants:
            name = f"erb_{formant}"
            if name in self.data.columns:
                self.data[name] = 21.4 * np.log10(1 + 0.00437 * formant_data[formant])
            else:
                self.data[name] = 21.4 * np.log10(
                    1 + 0.00437 * formant_data[formant])  # Create the column if it does not exist

        # Update scatterplot or other UI elements
        self.update_scatterplot()

    # Takes delay event into account when resizing the app to avoid lag
    def custom_resize_event(self, event):
        self.resize_timer.start(200)
        super().resizeEvent(event)

    # Takes delay event into account when resizing the scatterplot to avoid lag
    def delayed_update_scatterplot(self):
        self.resize_timer.stop()  # Stops the timer to ensure it only triggers o
        # nce
        self.update_scatterplot()

        # Uses the timer to avoid lag - will return to that
        # self.resize_timer.stop()
        # self.update_scatterplot()

    # Clears all the data from the dataframe
    def clear_data(self):
        # Get a list of all current column names
        existing_columns = list(self.data.columns)

        # Clear existing data in all columns
        for column in existing_columns:
            self.data[column] = pd.Series(dtype=self.data[column].dtype)  # Clear data in each column

        # Reset self.data to an empty DataFrame with original columns
        self.data = pd.DataFrame(columns=existing_columns)

        # Update the scatterplot after clearing data
        self.update_scatterplot()

    # Allows the user to simply save whatever there is on the scatterplot quickly
    def save_scatterplot_auto(self):
        custom_title = self.edit_title.text() or "Vowel Space(s)"
        file_name = f"{custom_title}.jpg"

        if file_name:
            try:
                self.figure.savefig(file_name, format='jpeg', dpi=1200)
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

                self.figure.savefig(file_name, format=file_format, dpi=1200)
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
                # Remove columns that have no data
                columns_to_keep = self.data.columns[self.data.count() > 0]
                self.data = self.data[columns_to_keep]

                # Determine file format based on the selected file extension
                file_format = 'xls' if file_name.lower().endswith('.xls') else 'xlsx'

                self.data.to_excel(file_name, index=False, sheet_name='Sheet1', engine='openpyxl')
                QMessageBox.information(self, "Success", f"Data saved to {file_format} successfully.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error saving data to {file_format}: {str(e)}")

    # Imports data from an .xls or .xlsx file. The files should have columns named "vowel", "speaker", and F values.
    def import_data_from_excel(self):
        self.clear_data()  # Clears the already existing data on the dataframe before the importing

        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_name, _ = QFileDialog.getOpenFileName(self, "Import Data from Excel", "",
                                                   "Excel Files (*.xls *.xlsx);;All Files (*)", options=options)

        if file_name:
            try:
                # Read Excel file with specific na_values to handle various representations of missing values
                na_values = ['', 'NaN', 'nan', 'N/A', 'NA', 'n/a']
                new_data = pd.read_excel(file_name, na_values=na_values)

                # Ensure all formant columns are treated as numeric and handle errors gracefully
                formant_columns = ['f0', 'f1', 'f2', 'f3', 'f4']
                for col in formant_columns:
                    if col in new_data.columns:
                        new_data[col] = pd.to_numeric(new_data[col], errors='coerce')

                # Set 'speaker' column to an empty string if it doesn't exist
                if 'speaker' not in new_data.columns:
                    new_data['speaker'] = ''

                # Fill missing values in 'speaker' column with 'N/A'
                new_data['speaker'] = new_data['speaker'].fillna('N/A')

                # Drop rows with any missing values after conversion
                new_data = new_data.dropna()

                # Concatenate new data with existing data
                self.data = pd.concat([self.data, new_data], ignore_index=True)

                # Open dfEditor window with imported data
                self.df_editor = dfEditor(self.data)
                self.df_editor.show()

                # Update scatterplot after importing data
                self.update_scatterplot()

                QMessageBox.information(self, "Success", "Data imported from Excel successfully.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error importing data from Excel: {str(e)}")

    # Shows an IPA keyboard
    def show_IPA(self):
        self.ipa_window = IPAWindow(self)
        self.ipa_window.exec_()

    # Opens Dataframe editor
    def open_df_editor(self):
        self.df_editor = dfEditor(self.data)  # Assuming you pass data to the editor
        self.df_editor.show()

    # Opens Audio Analysis Tools window.
    def audio_analysis_tools(self):
        # Create a new instance of AudioAnalysisToolsWindow if not open
        self.audio_tools_window = AudioAnalysisTool()
        self.audio_tools_window.show()

class IPAWindow(QDialog):
    def __init__(self, parent=None):
        super(IPAWindow, self).__init__(parent)
        self.setWindowTitle('IPA Keyboard')

        layout = QVBoxLayout()

        grid_layout = QGridLayout()

        # Define the groups of letters and their corresponding labels
        letter_groups = [('ɑæɐ', 'A'), ('əɚɵ', 'E'), ('ɛɜɝ', 'ɜ'),
                         ('ɪɨ', 'I'), ('ɔœɒ', 'O'), ('ø', 'Ö'),
                         ('ʊʉ', 'U'), ('ʕʔ', '2')] #('ː̃̈ʰʲʷ', 'microns')] will get back to that.

        # Add buttons and group boxes for each letter group
        for i, (group, label) in enumerate(letter_groups):
            group_box = QGroupBox(label, self)  # Create a group box for each group with the label
            group_layout = QHBoxLayout()  # Layout for buttons in this group

            # Add buttons for each letter in the group
            for letter in group:
                button = QPushButton(letter, self)
                button.clicked.connect(lambda checked, l=letter: self.button_clicked(l))
                group_layout.addWidget(button)

            group_box.setLayout(group_layout)
            grid_layout.addWidget(group_box, i // 3, i % 3)

        layout.addLayout(grid_layout)
        self.setLayout(layout)

    def button_clicked(self, letter):
        self.parent().edit_vowel.setText(letter)
        self.close() #will get back to that.

class dfEditor(QDialog):
    def __init__(self, data, parent=None):
        super().__init__(parent)
        self.data = data
        self.setWindowTitle("DataFrame Editor")
        self.setGeometry(100, 100, 700, 500)  # 700x500 looks good

        # Store the reference to VowelSpaceVisualizer instance
        self.vowel_space_visualizer = vowel_space_visualizer

        self.initUI()

    def initUI(self):
        # Creating a QTableWidget to display dataframe
        self.create_table_widget()

        # Adding a Save button
        self.save_button = QPushButton('Save Changes', self)
        self.save_button.clicked.connect(self.save_changes)

        # Layout setup
        layout = QVBoxLayout()
        layout.addWidget(self.table_widget)
        layout.addWidget(self.save_button)
        self.setLayout(layout)

    def create_table_widget(self):
        # Creating a QTableWidget and adding data
        self.table_widget = QTableWidget()
        self.table_widget.setRowCount(len(self.data.index))
        self.table_widget.setColumnCount(len(self.data.columns))
        self.table_widget.setHorizontalHeaderLabels(self.data.columns)

        for i in range(len(self.data.index)):
            for j in range(len(self.data.columns)):
                item = QTableWidgetItem(str(self.data.iloc[i, j]))  # Ensure numeric values are converted to str
                self.table_widget.setItem(i, j, item)

    def save_changes(self):
        # Save changes made in the QTableWidget back to the dataframe
        for i in range(self.table_widget.rowCount()):
            for j in range(self.table_widget.columnCount()):
                item = self.table_widget.item(i, j)
                if item is not None:
                    try:
                        # Attempt to convert text back to numeric
                        value = float(item.text())
                    except ValueError:
                        value = item.text()  # Use text as-is if conversion fails
                    self.data.iat[i, j] = value
        self.vowel_space_visualizer.update_scatterplot() # Esentially updates the scatteplot upon any change on the df. TODO: a little laggy.

class AudioAnalysisTool(QWidget):
    def __init__(self):
        super().__init__()

        self.show_pitch = False
        self.show_intensity = False
        self.show_formants = False

        # Store the reference to VowelSpaceVisualizer instance
        self.vowel_space_visualizer = vowel_space_visualizer

        self.initUI()

    def initUI(self):
        # Set up the layout for the Audio Analysis Tools window
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

        # Add the Matplotlib toolbar
        from matplotlib.backends.backend_qt5 import NavigationToolbar2QT as NavigationToolbar
        self.toolbar = NavigationToolbar(self.canvas, self)
        layout.addWidget(self.toolbar)

        # Add the "Read from Audio File" action to the menu
        self.create_menu_bar()

        # Set the layout
        self.setLayout(layout)
        self.setWindowTitle("Audio Analysis Tools")
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

        # Save the graph
        save_graph_action = self.create_action('Save Graph', self.save_graph)
        file_menu.addAction(save_graph_action)

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

        # Create a submenu for formants under Options menu
        formants_submenu = QMenu('Show Formants', self)

        # Add actions for F1, F2, F3, F4 under the formants submenu
        self.formant_f1_action = self.create_action('Show f1', self.toggle_formant_f1, checkable=True)
        formants_submenu.addAction(self.formant_f1_action)

        self.formant_f2_action = self.create_action('Show f2', self.toggle_formant_f2, checkable=True)
        formants_submenu.addAction(self.formant_f2_action)

        self.formant_f3_action = self.create_action('Show f3', self.toggle_formant_f3, checkable=True)
        formants_submenu.addAction(self.formant_f3_action)

        self.formant_f4_action = self.create_action('Show f4', self.toggle_formant_f4, checkable=True)
        formants_submenu.addAction(self.formant_f4_action)

        # Add the formants submenu to the Options menu
        options_menu.addMenu(formants_submenu)

    def create_action(self, text, function, shortcut=None, checkable=False):
        action = QAction(text, self)
        action.triggered.connect(function)
        if shortcut:
            action.setShortcut(shortcut)
        if checkable:
            action.setCheckable(True)
        return action

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

            # Redraw formants based on checked actions
            if self.formant_f1_action.isChecked() and self.formants:
                self.draw_formants(self.formants, 1)
            if self.formant_f2_action.isChecked() and self.formants:
                self.draw_formants(self.formants, 2)
            if self.formant_f3_action.isChecked() and self.formants:
                self.draw_formants(self.formants, 3)
            if self.formant_f4_action.isChecked() and self.formants:
                self.draw_formants(self.formants, 4)
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

                # Update the existing plot in the Audio Analysis Tools window
                self.draw_spectrogram(file_name)

                # Extract pitch information using Parselmouth
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

    def draw_formants(self, formants=None, formant_number=None):
        try:
            if formants and formant_number:
                plt.plot(formants.xs(), [formants.get_value_at_time(formant_number, x) for x in formants.xs()], 'o',
                         color='w', markersize=3)
                plt.plot(formants.xs(), [formants.get_value_at_time(formant_number, x) for x in formants.xs()], 'o',
                         markersize=1)
                self.canvas.draw()
            else:
                QMessageBox.critical(self, "Error", "Formant data or formant number is not available.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error plotting formants: {str(e)}")

    # Define toggle methods for each formant
    def toggle_formant_f1(self):
        self.redraw_plots()

    def toggle_formant_f2(self):
        self.redraw_plots()

    def toggle_formant_f3(self):
        self.redraw_plots()

    def toggle_formant_f4(self):
        self.redraw_plots()

    def update_cursor_coordinates(self, event):
        if event.inaxes:
            x, y = event.xdata, event.ydata
            self.coordinates_label.setText(f'Cursor Coordinates: x={x:.2f}, y={y:.2f}')

    def handle_click(self, event):
        x, y = event.xdata, event.ydata

        if event.inaxes and event.button == 3:
            # Extract formants and print frequencies for the x-coordinate
            f1 = self.formants.get_value_at_time(1, x) if self.formants else None
            f2 = self.formants.get_value_at_time(2, x) if self.formants else None
            f3 = self.formants.get_value_at_time(3, x) if self.formants else None
            f4 = self.formants.get_value_at_time(4, x) if self.formants else None

            # Audio title
            audio_title = os.path.splitext(os.path.basename(self.audio_file))[0]

            # Update VowelSpaceVisualizer with the formant values
            self.vowel_space_visualizer.update_input_fields_audio(f1, f2, f3, f4, audio_title)

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

            self.figure.tight_layout()
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
                QMessageBox.critical(self, "Error", "Intensity data is not available.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error plotting intensity: {str(e)}")

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
                QMessageBox.critical(self, "Error", "Pitch data is not available.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error plotting pitch: {str(e)}")

    def save_graph(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Graph", "",
                                                   "JPEG files (*.jpeg);;All Files (*)", options=options)
        if file_path:
            try:
                # Save the current plot as a .jpeg file with high quality (1400 DPI)
                self.figure.savefig(file_path, format='jpeg', dpi=1400)
                QMessageBox.information(self, "Success", "Graph saved successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error saving graph: {str(e)}")


if __name__ == '__main__':
    app = QApplication(sys.argv)

    vowel_space_visualizer = VowelSpaceVisualizer()

    audio_analysis_tool = AudioAnalysisTool()

    vowel_space_visualizer.show()

    sys.exit(app.exec_())

    # VowSpace (Vowel Space Visualizer) v.1.4.2
    # Ali Çağan Kaya, under the GPL-3.0 license.
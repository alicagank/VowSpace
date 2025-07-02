# vowel_space_visualizer.py
# This is where everything else comes together.

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.patches import Ellipse
from scipy.spatial import ConvexHull
from scipy.stats import chi2
from PyQt5.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout,
    QGridLayout, QFileDialog, QMessageBox, QMenu, QMenuBar, QAction, QCheckBox, QComboBox
)
from PyQt5.QtCore import Qt, QTimer

from components.df_editor import DFEditor
from components.ipa_window import IPAWindow
from components.audio_tool import AudioAnalysisTool

from core.normalization import (
    lobanov_normalization,
    bark_difference,
    nearey1,
    nearey2,
    bark_transform,
    log_transform,
    mel_transform,
    erb_transform
)


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

        # Set labels for the axes, inverted, that is, if needed...
        '''custom_label_x = self.edit_label_x.text()
        custom_label_y = self.edit_label_y.text()
        if self.checkbox_custom_labels.isChecked():
            self.ax.set_xlabel(custom_label_x, pad=25)
            self.ax.set_ylabel(custom_label_y, pad=25)
        else:'''
        self.ax.set_xlabel(y_column)
        self.ax.set_ylabel(x_column)

        # Position of the rulers
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

    # Normalization!
    def lobify(self, arg):
        formants = [self.dropdown_x_axis.currentText(), self.dropdown_y_axis.currentText()]
        self.data = lobanov_normalization(self.data, formants)
        self.update_scatterplot()

    def diffBark(self, arg):
        self.data = bark_difference(self.data)
        self.update_scatterplot()

    def Nearey1(self, arg):
        formants = [self.dropdown_x_axis.currentText(), self.dropdown_y_axis.currentText()]
        self.data = nearey1(self.data, formants)
        self.update_scatterplot()

    def Nearey2(self, exp=False):
        formants = [self.dropdown_x_axis.currentText(), self.dropdown_y_axis.currentText()]
        self.data = nearey2(self.data, formants)
        self.update_scatterplot()

    def metricBark(self, arg):
        formants = [self.dropdown_x_axis.currentText(), self.dropdown_y_axis.currentText()]
        self.data = bark_transform(self.data, formants)
        self.update_scatterplot()

    def normLog(self, arg):
        formants = [self.dropdown_x_axis.currentText(), self.dropdown_y_axis.currentText()]
        self.data = log_transform(self.data, formants)
        self.update_scatterplot()

    def normMel(self, arg):
        formants = [self.dropdown_x_axis.currentText(), self.dropdown_y_axis.currentText()]
        self.data = mel_transform(self.data, formants)
        self.update_scatterplot()

    def normErb(self, arg):
        formants = [self.dropdown_x_axis.currentText(), self.dropdown_y_axis.currentText()]
        self.data = erb_transform(self.data, formants)
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

                # import_data_from_excel
                self.df_editor = DFEditor(self.data, visualizer=self)
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
        self.df_editor = DFEditor(self.data)  # Passinf data to the DFEditor
        self.df_editor.show()

    # Opens Audio Analysis Tools window.
    def audio_analysis_tools(self):
        # Creates a new instance of AudioAnalysisTools if not open
        self.audio_tools_window = AudioAnalysisTool(visualizer=self)
        self.audio_tools_window.show()
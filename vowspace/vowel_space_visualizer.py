# This is where everything else comes together.

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout,
    QGridLayout, QFileDialog, QMessageBox, QMenu, QMenuBar, QAction,
    QCheckBox, QComboBox, QDialog, QGroupBox
)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.patches import Ellipse
from scipy.spatial import ConvexHull
from scipy.stats import chi2

from vowspace.components.audio_tool import AudioAnalysisTool
from vowspace.components.df_editor import DFEditor
from vowspace.components.ipa_window import IPAWindow
from vowspace.core.normalization import (
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
        self.setWindowIcon(QIcon("vowspace/assets/vowspace-1024.png"))
        self.initUI()

        self.resize_timer = QTimer()
        self.resize_timer.timeout.connect(self.delayed_update_plot)

    def initUI(self):
        # Set normalization to normal
        self.current_normalization = "None"

        # Correct booleans
        self.plot_settings = {
            "group_by_vowel": False,
            "show_legend": False,
            "show_grid": False,

            "labels_f": False,
            "labels_vowel": False,
            "labels_speaker": False,

            "ellipse": False,
            "ellipse_outline": False,
            "circular": False,

            "qhull": False,
            "qhull_outline": False,

            "show_center": False
        }

        # Create widgets
        self.create_widgets()

        # Set layout
        self.set_layout()

        # Set initial state
        self.data = pd.DataFrame(columns=["vowel", "f0", "f1", "f2", "f3", "f4", "f5", "speaker"])
        self.setWindowTitle("VowSpace v1.4.4")
        self.setWindowIcon(QIcon("vowspace/assets/vowspace.ico"))

        self.create_menu_bar()

        self.resizeEvent = self.custom_resize_event

        self.resize(800, 800)
        self.setMinimumSize(800, 800)

    def create_menu_bar(self):
        menubar = QMenuBar(self)

        # File menu
        file_menu = menubar.addMenu("File")

        save_action = self.create_action("Save", self.save_scatterplot_auto, Qt.CTRL + Qt.Key_S)
        save_as_action = self.create_action("Save As...", self.save_scatterplot, Qt.CTRL + Qt.SHIFT + Qt.Key_S)
        save_data_action = self.create_action("Save Data As...", self.save_data)
        import_data_action = self.create_action("Import Data from Dataset", self.import_data)

        file_menu.addAction(save_action)
        file_menu.addAction(save_as_action)
        file_menu.addAction(save_data_action)
        file_menu.addAction(import_data_action)

        # Edit menu
        edit_menu = menubar.addMenu("Edit")

        undo_action = self.create_action("Undo", self.undo_last_data, Qt.CTRL + Qt.Key_Z)
        edit_menu.addAction(undo_action)

        # Options menu
        options_menu = menubar.addMenu("Options")

        visualization_settings_action = self.create_action(
            "Visualization Settings...",
            self.open_visualization_settings
        )
        options_menu.addAction(visualization_settings_action)

        # All these are now handled by a new QDialogue

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

        self.label_f0 = QLabel('F0 Value:')
        self.edit_f0 = QLineEdit()

        self.label_f1 = QLabel('F1 Value:')
        self.edit_f1 = QLineEdit()

        self.label_f2 = QLabel('F2 Value:')
        self.edit_f2 = QLineEdit()

        self.label_f3 = QLabel('F3 Value:')
        self.edit_f3 = QLineEdit()

        self.label_f4 = QLabel('F4 Value:')
        self.edit_f4 = QLineEdit()

        self.label_f5 = QLabel('F5 Value:')
        self.edit_f5 = QLineEdit()

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
        self.button_update_plot = self.create_button('Update Plot', self.update_plot)
        # Audio Analysis Tools class
        self.button_audio_analysis_tools = self.create_button('Audio Analysis Tools', self.audio_analysis_tools)
        # IPA keyboard button
        self.button_IPA = self.create_button('Show IPA', self.show_IPA)
        # Dataframe editor button
        self.button_open_df_editor = self.create_button('DataFrame Editor', self.open_df_editor)

        # Dropdown menus for selecting columns
        self.label_x_axis = QLabel('Y Axis:')
        self.dropdown_x_axis = QComboBox()
        self.dropdown_x_axis.addItems(["F0", "F1", "F2", "F3", "F4", "F5"])  # Add available columns
        self.dropdown_x_axis.setCurrentText("F1")  # Set default value to F1

        self.label_y_axis = QLabel('X Axis:')
        self.dropdown_y_axis = QComboBox()
        self.dropdown_y_axis.addItems(["F0", "F1", "F2", "F3", "F4", "F5"])  # Add available columns
        self.dropdown_y_axis.setCurrentText("F2")  # Set default value to F2

        # Visualization customization dropdowns
        self.label_palette = QLabel("Palette:")
        self.dropdown_palette = QComboBox()
        self.dropdown_palette.addItems([
            "viridis",
            "plasma",
            "inferno",
            "magma",
            "cividis",
            "tab10",
            "Set2",
            "Dark2"
        ])
        self.dropdown_palette.setCurrentText("viridis")
        self.dropdown_palette.currentTextChanged.connect(self.update_plot)

        self.label_point_size = QLabel("Point Size:")
        self.dropdown_point_size = QComboBox()
        self.dropdown_point_size.addItems(["20", "40", "60", "80", "100"])
        self.dropdown_point_size.setCurrentText("40")
        self.dropdown_point_size.currentTextChanged.connect(self.update_plot)

        self.label_point_alpha = QLabel("Point Alpha:")
        self.dropdown_point_alpha = QComboBox()
        self.dropdown_point_alpha.addItems(["0.3", "0.5", "0.7", "0.8", "1.0"])
        self.dropdown_point_alpha.setCurrentText("0.8")
        self.dropdown_point_alpha.currentTextChanged.connect(self.update_plot)

        self.figure, self.ax = plt.subplots(figsize=(8, 6))
        self.canvas = FigureCanvas(self.figure)

    def update_input_fields_audio(self, f1, f2, f3, f4, f5, speaker_name):
        # Update speaker's name
        self.edit_speaker.setText(str(speaker_name))

        # Update formant values (convert to string with maximum 3 decimal places)
        #self.edit_F0.setText("{:.3f}".format(f0)) TODO: here.
        self.edit_f1.setText("{:.3f}".format(f1))
        self.edit_f2.setText("{:.3f}".format(f2))
        self.edit_f3.setText("{:.3f}".format(f3))
        self.edit_f4.setText("{:.3f}".format(f4))
        self.edit_f5.setText("{:.3f}".format(f5))

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
        input_grid_layout.addWidget(self.label_f5, 6, 0)
        input_grid_layout.addWidget(self.edit_f5, 6, 1)
        input_grid_layout.addWidget(self.label_speaker, 7, 0)
        input_grid_layout.addWidget(self.edit_speaker, 7, 1)

        layout.addLayout(input_grid_layout)

        title_layout = QHBoxLayout()
        title_layout.addWidget(self.label_title)
        title_layout.addWidget(self.edit_title)
        title_layout.addWidget(self.checkbox_no_title)

        layout.addLayout(title_layout)

        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(self.button_add_data)
        buttons_layout.addWidget(self.button_clear_data)
        buttons_layout.addWidget(self.button_update_plot)
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
            self.label_f5.show()
            self.edit_f5.show()
        else:
            # Hide all formant input boxes
            self.label_f0.hide()
            self.edit_f0.hide()
            self.label_f3.hide()
            self.edit_f3.hide()
            self.label_f4.hide()
            self.edit_f4.hide()
            self.label_f5.hide()
            self.edit_f5.hide()

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

        # Convert F5 to float or set to Nan if empty
        f5 = float(self.edit_f5.text()) if self.edit_f5.text() else np.nan

        speaker = self.edit_speaker.text() if self.edit_speaker.text() else ''

        new_data = pd.DataFrame(
            {"vowel": [vowel], "f0": [f0], "f1": [f1], "f2": [f2], "f3": [f3], "f4": [f4], "f5": [f5], "speaker": [speaker]}) if speaker else \
            pd.DataFrame({"vowel": [vowel], "f0": [f0], "f1": [f1], "f2": [f2], "f3": [f3], "f4": [f4], "f5": [f5]})

        self.data = pd.concat([self.data, new_data], ignore_index=True)

        self.clear_input_fields()

        self.edit_vowel.setFocus()
        self.update_plot()

    # Automatically clears the input fields after adding data
    def clear_input_fields(self):
        self.edit_vowel.clear()
        self.edit_f0.clear()
        self.edit_f1.clear()
        self.edit_f2.clear()
        self.edit_f3.clear()
        self.edit_f4.clear()
        self.edit_f5.clear()
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
            f5 = float(self.edit_f5.text()) if self.edit_f5.text() else np.nan
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
            self.update_plot()

    def open_visualization_settings(self):
        self.visualization_settings_window = VisualizationSettingsDialog(self)
        self.visualization_settings_window.show()

    # Creates the scatterplot
    def update_plot(self, format=None):
        self.ax.clear()

        self.apply_normalization_if_needed()

        config = self.get_plot_config()
        if config is None:
            return

        self.plot_scatter_points(config)

        if self.plot_settings["ellipse"]:
            self.plot_ellipses(config)

        if self.plot_settings["qhull"]:
            self.plot_qhulls(config)

        self.apply_plot_style(config)

        self.figure.tight_layout()
        self.canvas.draw()

    def get_plot_config(self):
        #  Collect all reusable plot settings in one place

        x_column_ui = self.dropdown_x_axis.currentText()
        y_column_ui = self.dropdown_y_axis.currentText()

        x_column = x_column_ui.lower()
        y_column = y_column_ui.lower()

        x_column, y_column = self.apply_selected_normalization_to_columns(
            x_column,
            y_column
        )

        if x_column not in self.data.columns or y_column not in self.data.columns:
            QMessageBox.critical(
                self,
                "Error",
                f"Selected column(s) '{x_column}' or '{y_column}' do not exist in the dataset."
            )
            return None

        group_by = "vowel" if self.plot_settings["group_by_vowel"] else "speaker"

        if group_by not in self.data.columns:
            QMessageBox.critical(
                self,
                "Error",
                f"Grouping column '{group_by}' does not exist in the dataset."
            )
            return None

        unique_values = self.data[group_by].dropna().unique()

        cmap = plt.get_cmap(self.dropdown_palette.currentText())

        colors = {
            value: cmap(i / max(len(unique_values), 1))
            for i, value in enumerate(unique_values)
        }

        return {
            "x_column": x_column,
            "y_column": y_column,
            "group_by": group_by,
            "colors": colors,
        }

    def apply_selected_normalization_to_columns(self, x_column, y_column):
        normalization = self.current_normalization

        if normalization == "Bark Conversion":
            return f"bark_{x_column}", f"bark_{y_column}"

        if normalization == "Log Conversion":
            return f"log_{x_column}", f"log_{y_column}"

        if normalization == "Mel Conversion":
            return f"mel_{x_column}", f"mel_{y_column}"

        if normalization == "ERB Conversion":
            return f"erb_{x_column}", f"erb_{y_column}"

        if normalization == "Bark Difference":
            return "Z3_minus_Z2", "Z3_minus_Z1"

        if normalization == "Lobanov Normalization":
            return f"zsc_{x_column}", f"zsc_{y_column}"

        if normalization == "Nearey1 Normalization":
            return f"logmean_{x_column}", f"logmean_{y_column}"

        if normalization == "Nearey2 Normalization":
            return f"slogmean_{x_column}", f"slogmean_{y_column}"

        return x_column, y_column

    def apply_normalization_if_needed(self):
        normalization = self.current_normalization

        if normalization == "None":
            return

        formants = [
            self.dropdown_x_axis.currentText().lower(),
            self.dropdown_y_axis.currentText().lower()
        ]

        if normalization == "Bark Conversion":
            self.data = bark_transform(self.data, formants)

        elif normalization == "Log Conversion":
            self.data = log_transform(self.data, formants)

        elif normalization == "Mel Conversion":
            self.data = mel_transform(self.data, formants)

        elif normalization == "ERB Conversion":
            self.data = erb_transform(self.data, formants)

        elif normalization == "Bark Difference":
            self.data = bark_difference(self.data)

        elif normalization == "Lobanov Normalization":
            self.data = lobanov_normalization(self.data, formants)

        elif normalization == "Nearey1 Normalization":
            self.data = nearey1(self.data, formants)

        elif normalization == "Nearey2 Normalization":
            self.data = nearey2(self.data, formants)

    def plot_scatter_points(self, config):
        #  Plot the basic vowel space scatter points

        x_column = config["x_column"]
        y_column = config["y_column"]
        group_by = config["group_by"]
        colors = config["colors"]

        markers = "."
        vowel_markers = {
            vowel: markers
            for vowel in self.data["vowel"].dropna().unique()
        }

        for vowel in self.data["vowel"].dropna().unique():
            subset = self.data[self.data["vowel"] == vowel]

            x_num = pd.to_numeric(subset[x_column], errors="coerce")
            y_num = pd.to_numeric(subset[y_column], errors="coerce")
            mask = np.isfinite(x_num) & np.isfinite(y_num)

            if not mask.any():
                continue

            color = [
                colors.get(value, plt.cm.viridis(0.5))
                for value in subset.loc[mask, group_by]
            ]

            self.ax.scatter(
                y_num[mask],
                x_num[mask],
                marker=vowel_markers.get(vowel, "."),
                c=color,
                label=vowel,
                s=float(self.dropdown_point_size.currentText()),
                alpha=float(self.dropdown_point_alpha.currentText()),
                edgecolors="w",
                linewidth=1
            )

            self.plot_point_labels(
                subset.loc[mask],
                x_column,
                y_column
            )

    def plot_point_labels(self, subset, x_column, y_column):
        #  Plot optional labels for formant values, vowels, and speakers

        show_labels_f = self.plot_settings["labels_f"]
        show_labels_vowel = self.plot_settings["labels_vowel"]
        show_labels_speaker = self.plot_settings["labels_speaker"]

        if not any([show_labels_f, show_labels_vowel, show_labels_speaker]):
            return

        for _, row in subset.iterrows():
            label = ""

            if show_labels_f:
                label += f"{x_column.upper()}: {float(row[x_column]):.2f}\n"
                label += f"{y_column.upper()}: {float(row[y_column]):.2f}\n"

            if show_labels_vowel:
                label += f"{row['vowel']}\n"

            if show_labels_speaker and "speaker" in row:
                label += f"{row['speaker']}\n"

            if label:
                self.ax.annotate(
                    label.strip(),
                    (float(row[y_column]), float(row[x_column])),
                    textcoords="offset points",
                    xytext=(0, 5),
                    ha="center",
                    va="bottom",
                    fontsize=8
                )

    def plot_ellipses(self, config):
        #   Plot confidence ellipses around vowel or speaker groups

        x_column = config["x_column"]
        y_column = config["y_column"]
        group_by = config["group_by"]
        colors = config["colors"]

        for key in self.data[group_by].dropna().unique():
            subset = self.data[self.data[group_by] == key]

            x = pd.to_numeric(subset[x_column], errors="coerce")
            y = pd.to_numeric(subset[y_column], errors="coerce")
            mask = np.isfinite(x) & np.isfinite(y)

            if mask.sum() < 2:
                continue

            if x[mask].nunique() < 2 or y[mask].nunique() < 2:
                continue

            yx = np.column_stack([
                y[mask].to_numpy(dtype=float),
                x[mask].to_numpy(dtype=float)
            ])

            mean = yx.mean(axis=0)
            cov = np.cov(yx, rowvar=False)

            eigvals, eigvecs = np.linalg.eigh(cov)
            order = eigvals.argsort()[::-1]
            eigvals = eigvals[order]
            eigvecs = eigvecs[:, order]

            scale_factor = np.sqrt(chi2.ppf(0.67, df=2))

            width, height = 2 * scale_factor * np.sqrt(eigvals)
            angle = np.degrees(np.arctan2(*eigvecs[:, 0][::-1]))

            color = colors.get(key, plt.cm.viridis(0.5))

            if self.plot_settings["circular"]:
                diameter = max(width, height)
                width = diameter
                height = diameter
                angle = 0

            if self.plot_settings["ellipse_outline"]:
                facecolor = "none"
                alpha = 1.0
            else:
                facecolor = color
                alpha = 0.2

            ellipse = Ellipse(
                xy=(mean[0], mean[1]),
                width=width,
                height=height,
                angle=angle,
                edgecolor=color,
                facecolor=facecolor,
                lw=1.5,
                alpha=alpha
            )

            self.ax.add_patch(ellipse)

            if self.plot_settings["show_center"]:
                self.ax.text(
                    mean[0],
                    mean[1],
                    str(key),
                    color="black",
                    ha="center",
                    va="center",
                    fontsize=10
                )

    def plot_qhulls(self, config):
        #   Plot convex hulls around vowel or speaker groups

        x_column = config["x_column"]
        y_column = config["y_column"]
        group_by = config["group_by"]
        colors = config["colors"]

        if len(self.data) < 3:
            return

        for key, group in self.data.groupby(group_by):
            if pd.isna(key):
                continue

            gx = pd.to_numeric(group[x_column], errors="coerce")
            gy = pd.to_numeric(group[y_column], errors="coerce")
            mask = np.isfinite(gx) & np.isfinite(gy)

            points = np.column_stack([
                gy[mask].to_numpy(dtype=np.float64, copy=False),
                gx[mask].to_numpy(dtype=np.float64, copy=False)
            ])

            if points.shape[0] < 3:
                continue

            if np.unique(points, axis=0).shape[0] < 3:
                continue

            if np.linalg.matrix_rank(points) < 2:
                QMessageBox.critical(
                    self,
                    "Error",
                    f"The input data for {group_by} '{key}' is less than 2-dimensional."
                )
                continue

            try:
                hull = ConvexHull(points)
                color = colors.get(key, plt.cm.viridis(0.5))

                if self.plot_settings["qhull_outline"]:
                    facecolor = "none"
                    edgecolor = color
                    alpha = 1.0
                else:
                    facecolor = color
                    edgecolor = color
                    alpha = 0.2

                polygon = plt.Polygon(
                    points[hull.vertices],
                    closed=True,
                    alpha=alpha,
                    label=key,
                    facecolor=facecolor,
                    edgecolor=edgecolor,
                    linewidth=1.5
                )

                self.ax.add_patch(polygon)

                if self.plot_settings["show_center"]:
                    centroid = np.mean(points[hull.vertices], axis=0)
                    self.ax.text(
                        centroid[0],
                        centroid[1],
                        str(key),
                        color="black",
                        ha="center",
                        va="center",
                        fontsize=10
                    )

            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Qhull error for {group_by} '{key}': {str(e)}"
                )

    def apply_plot_style(self, config):
        #   Apply shared title, legend, grid, axes, and vowel space orientation

        x_column = config["x_column"]
        y_column = config["y_column"]

        custom_title = self.edit_title.text()

        if self.checkbox_no_title.isChecked():
            self.ax.set_title("", pad=25)
        else:
            self.ax.set_title(
                custom_title if custom_title else "Vowel Space(s)",
                pad=25
            )

        legend = self.ax.get_legend()
        if legend:
            legend.remove()

        if self.plot_settings["show_legend"]:
            handles, labels = self.ax.get_legend_handles_labels()
            if handles and labels:
                self.ax.legend(loc="lower left", bbox_to_anchor=(1.05, 0))

        if self.plot_settings["show_grid"]:
            self.ax.grid(True, linestyle="--", linewidth=0.5)
        else:
            self.ax.grid(False)

        self.ax.set_xlabel(y_column.upper())
        self.ax.set_ylabel(x_column.upper())

        self.ax.yaxis.tick_right()
        self.ax.xaxis.tick_top()

        self.ax.invert_xaxis()
        self.ax.invert_yaxis()

        self.ax.xaxis.set_label_position("bottom")
        self.ax.xaxis.set_ticks_position("top")
        self.ax.yaxis.set_label_position("left")
        self.ax.yaxis.set_ticks_position("right")

    # Takes delay event into account when resizing the app to avoid lag
    def custom_resize_event(self, event):
        self.resize_timer.start(200)
        super().resizeEvent(event)

    # Takes delay event into account when resizing the scatterplot to avoid lag
    def delayed_update_plot(self):
        self.resize_timer.stop()  # Stops the timer to ensure it only triggers o
        # nce
        self.update_plot()

        # Uses the timer to avoid lag - will return to that
        # self.resize_timer.stop()
        # self.update_plot()

    # Return to the original state of the dataframe
    def clear_data(self):
        # Reset to clean base schema ONLY
        self.data = pd.DataFrame(
            columns=["vowel", "f0", "f1", "f2", "f3", "f4", "f5", "speaker"]
        )

        self.update_plot()

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

    # Saves the current dataframe as an Excel or CSV file
    def save_data(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog

        custom_title = self.edit_title.text() or "Vowel Space(s)"

        file_name, _ = QFileDialog.getSaveFileName(
            self,
            "Save Data",
            f"{custom_title}.xlsx",
            "Excel Files (*.xlsx);;CSV Files (*.csv);;All Files (*)",
            options=options
        )

        if file_name:
            try:
                # Remove empty columns
                columns_to_keep = self.data.columns[self.data.count() > 0]
                data_to_save = self.data[columns_to_keep]

                if file_name.endswith('.csv'):
                    data_to_save.to_csv(file_name, index=False)
                    file_format = 'CSV'
                else:
                    data_to_save.to_excel(
                        file_name,
                        index=False,
                        sheet_name='Sheet1',
                        engine='openpyxl'
                    )
                    file_format = 'Excel'

                QMessageBox.information(self, "Success", f"Data saved to {file_format} successfully.")

            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error saving data: {str(e)}")

    # Imports data from an Excel or CSV file. The files should have columns named "vowel", "speaker", and F values.
    def import_data(self):
        self.clear_data()

        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog

        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Import Data from Dataset",
            "",
            "Data Files (*.xls *.xlsx *.csv);;Excel Files (*.xls *.xlsx);;CSV Files (*.csv);;All Files (*)",
            options=options
        )

        if file_name:
            try:
                na_values = ['', 'NaN', 'nan', 'N/A', 'NA', 'n/a']

                # Detects file type
                if file_name.endswith('.csv'):
                    new_data = pd.read_csv(file_name, na_values=na_values)
                else:
                    new_data = pd.read_excel(file_name, na_values=na_values)

                # Ensure numeric formants
                formant_columns = ['f0', 'f1', 'f2', 'f3', 'f4', 'f5']
                for col in formant_columns:
                    if col in new_data.columns:
                        new_data[col] = pd.to_numeric(new_data[col], errors='coerce')

                # Handle speaker column
                if 'speaker' not in new_data.columns:
                    new_data['speaker'] = ''

                new_data['speaker'] = new_data['speaker'].fillna('N/A')

                # Drop missing
                new_data = new_data.dropna()

                # Merge
                self.data = pd.concat([self.data, new_data], ignore_index=True)

                self.df_editor = DFEditor(self.data, visualizer=self)
                self.df_editor.show()

                self.update_plot()

                QMessageBox.information(self, "Success", "Data imported successfully.")

            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error importing data: {str(e)}")

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

class VisualizationSettingsDialog(QDialog):
    def __init__(self, visualizer):
        super().__init__(visualizer)
        self.visualizer = visualizer

        self.setWindowTitle("Visualization Settings")
        self.setMinimumWidth(360)

        self.create_widgets()
        self.set_layout()
        self.load_current_settings()

    def create_widgets(self):
        self.normalization_dropdown = QComboBox()
        self.normalization_dropdown.addItems([
            "None",
            "Bark Conversion",
            "Log Conversion",
            "Mel Conversion",
            "ERB Conversion",
            "Bark Difference",
            "Lobanov Normalization",
            "Nearey1 Normalization",
            "Nearey2 Normalization"
        ])
        self.group_by_vowel_checkbox = QCheckBox("Group by vowel")
        self.show_legend_checkbox = QCheckBox("Show legend")
        self.show_grid_checkbox = QCheckBox("Show grid")

        self.show_f_labels_checkbox = QCheckBox("Show formant value labels")
        self.show_vowel_labels_checkbox = QCheckBox("Show vowel labels")
        self.show_speaker_labels_checkbox = QCheckBox("Show speaker labels")

        self.connect_ellipse_checkbox = QCheckBox("Connect with ellipse(s)")
        self.ellipse_outline_checkbox = QCheckBox("Ellipse outline only")
        self.circular_boundary_checkbox = QCheckBox("Use circular boundary")
        self.connect_qhull_checkbox = QCheckBox("Connect with Qhull(s)")
        self.qhull_outline_checkbox = QCheckBox("Qhull outline only")
        self.show_center_labels_checkbox = QCheckBox("Show center labels")

        self.palette_dropdown = QComboBox()
        self.palette_dropdown.addItems([
            "viridis", "plasma", "inferno", "magma",
            "cividis", "tab10", "Set2", "Dark2"
        ])

        self.point_size_dropdown = QComboBox()
        self.point_size_dropdown.addItems(["20", "40", "60", "80", "100"])

        self.point_alpha_dropdown = QComboBox()
        self.point_alpha_dropdown.addItems(["0.3", "0.5", "0.7", "0.8", "1.0"])

        self.apply_button = QPushButton("Apply")
        self.reset_button = QPushButton("Reset to Defaults")
        self.close_button = QPushButton("Close")

        self.apply_button.clicked.connect(self.apply_settings)
        self.reset_button.clicked.connect(self.reset_to_defaults)
        self.close_button.clicked.connect(self.close)

    def set_layout(self):
        main_layout = QVBoxLayout()

        normalization_group = QGroupBox("Normalization")
        normalization_layout = QVBoxLayout()
        normalization_layout.addWidget(QLabel("Normalization / Conversion:"))
        normalization_layout.addWidget(self.normalization_dropdown)
        normalization_group.setLayout(normalization_layout)

        main_layout.addWidget(normalization_group)

        general_group = QGroupBox("General")
        general_layout = QVBoxLayout()
        general_layout.addWidget(self.group_by_vowel_checkbox)
        general_layout.addWidget(self.show_legend_checkbox)
        general_layout.addWidget(self.show_grid_checkbox)
        general_group.setLayout(general_layout)

        labels_group = QGroupBox("Labels")
        labels_layout = QVBoxLayout()
        labels_layout.addWidget(self.show_f_labels_checkbox)
        labels_layout.addWidget(self.show_vowel_labels_checkbox)
        labels_layout.addWidget(self.show_speaker_labels_checkbox)
        labels_group.setLayout(labels_layout)

        points_group = QGroupBox("Points")
        points_layout = QGridLayout()
        points_layout.addWidget(QLabel("Palette:"), 0, 0)
        points_layout.addWidget(self.palette_dropdown, 0, 1)
        points_layout.addWidget(QLabel("Point size:"), 1, 0)
        points_layout.addWidget(self.point_size_dropdown, 1, 1)
        points_layout.addWidget(QLabel("Point alpha:"), 2, 0)
        points_layout.addWidget(self.point_alpha_dropdown, 2, 1)
        points_group.setLayout(points_layout)

        boundary_group = QGroupBox("Boundaries")
        boundary_layout = QVBoxLayout()

        ellipse_group = QGroupBox("Ellipses")
        ellipse_layout = QVBoxLayout()
        ellipse_layout.addWidget(self.connect_ellipse_checkbox)
        ellipse_layout.addWidget(self.ellipse_outline_checkbox)
        ellipse_layout.addWidget(self.circular_boundary_checkbox)
        ellipse_group.setLayout(ellipse_layout)

        qhull_group = QGroupBox("Qhulls")
        qhull_layout = QVBoxLayout()
        qhull_layout.addWidget(self.connect_qhull_checkbox)
        qhull_layout.addWidget(self.qhull_outline_checkbox)
        qhull_group.setLayout(qhull_layout)

        shared_boundary_group = QGroupBox("Shared")
        shared_boundary_layout = QVBoxLayout()
        shared_boundary_layout.addWidget(self.show_center_labels_checkbox)
        shared_boundary_group.setLayout(shared_boundary_layout)

        boundary_layout.addWidget(ellipse_group)
        boundary_layout.addWidget(qhull_group)
        boundary_layout.addWidget(shared_boundary_group)

        boundary_group.setLayout(boundary_layout)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.apply_button)
        button_layout.addWidget(self.reset_button)
        button_layout.addWidget(self.close_button)

        main_layout.addWidget(general_group)
        main_layout.addWidget(labels_group)
        main_layout.addWidget(points_group)
        main_layout.addWidget(boundary_group)
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

    def load_current_settings(self):
        v = self.visualizer

        self.normalization_dropdown.setCurrentText(
            self.visualizer.current_normalization
        )

        self.group_by_vowel_checkbox.setChecked(v.plot_settings["group_by_vowel"])
        self.show_legend_checkbox.setChecked(v.plot_settings["show_legend"])
        self.show_grid_checkbox.setChecked(v.plot_settings["show_grid"])

        self.show_f_labels_checkbox.setChecked(v.plot_settings["labels_f"])
        self.show_vowel_labels_checkbox.setChecked(v.plot_settings["labels_vowel"])
        self.show_speaker_labels_checkbox.setChecked(v.plot_settings["labels_speaker"])

        self.connect_ellipse_checkbox.setChecked(v.plot_settings["ellipse"])
        self.ellipse_outline_checkbox.setChecked(v.plot_settings["ellipse_outline"])
        self.circular_boundary_checkbox.setChecked(v.plot_settings["circular"])
        self.connect_qhull_checkbox.setChecked(v.plot_settings["qhull"])
        self.qhull_outline_checkbox.setChecked(v.plot_settings["qhull_outline"])
        self.show_center_labels_checkbox.setChecked(v.plot_settings["show_center"])

        self.palette_dropdown.setCurrentText(v.dropdown_palette.currentText())
        self.point_size_dropdown.setCurrentText(v.dropdown_point_size.currentText())
        self.point_alpha_dropdown.setCurrentText(v.dropdown_point_alpha.currentText())

    def apply_settings(self):
        v = self.visualizer

        v.current_normalization = self.normalization_dropdown.currentText()

        v.plot_settings["group_by_vowel"] = self.group_by_vowel_checkbox.isChecked()
        v.plot_settings["show_legend"] = self.show_legend_checkbox.isChecked()
        v.plot_settings["show_grid"] = self.show_grid_checkbox.isChecked()

        v.plot_settings["labels_f"] = self.show_f_labels_checkbox.isChecked()
        v.plot_settings["labels_vowel"] = self.show_vowel_labels_checkbox.isChecked()
        v.plot_settings["labels_speaker"] = self.show_speaker_labels_checkbox.isChecked()

        v.plot_settings["ellipse"] = self.connect_ellipse_checkbox.isChecked()
        v.plot_settings["ellipse_outline"] = self.ellipse_outline_checkbox.isChecked()
        v.plot_settings["circular"] = self.circular_boundary_checkbox.isChecked()
        v.plot_settings["qhull"] = self.connect_qhull_checkbox.isChecked()
        v.plot_settings["qhull_outline"] = self.qhull_outline_checkbox.isChecked()
        v.plot_settings["show_center"] = self.show_center_labels_checkbox.isChecked()

        v.dropdown_palette.setCurrentText(self.palette_dropdown.currentText())
        v.dropdown_point_size.setCurrentText(self.point_size_dropdown.currentText())
        v.dropdown_point_alpha.setCurrentText(self.point_alpha_dropdown.currentText())

        v.update_plot()

    def reset_to_defaults(self):
        self.group_by_vowel_checkbox.setChecked(False)
        self.show_legend_checkbox.setChecked(False)
        self.show_grid_checkbox.setChecked(False)

        self.show_f_labels_checkbox.setChecked(False)
        self.show_vowel_labels_checkbox.setChecked(False)
        self.show_speaker_labels_checkbox.setChecked(False)

        self.connect_ellipse_checkbox.setChecked(False)
        self.ellipse_outline_checkbox.setChecked(False)
        self.circular_boundary_checkbox.setChecked(False)
        self.connect_qhull_checkbox.setChecked(False)
        self.qhull_outline_checkbox.setChecked(False)
        self.show_center_labels_checkbox.setChecked(False)

        self.palette_dropdown.setCurrentText("viridis")
        self.point_size_dropdown.setCurrentText("40")
        self.point_alpha_dropdown.setCurrentText("0.8")

        self.apply_settings()
# modulation/audio_tools.py

import os
import numpy as np
from parselmouth import Sound
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QMessageBox, QFileDialog, QMenuBar, QMenu, QAction
)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5 import NavigationToolbar2QT as NavigationToolbar


class AudioAnalysisTool(QWidget):
    def __init__(self, visualizer=None):
        super().__init__()

        self.vowel_space_visualizer = visualizer  # link back to VowelSpaceVisualizer
        self.show_pitch = False
        self.show_intensity = False
        self.pitch = None
        self.intensity = None
        self.formants = None

        self.initUI()

    def initUI(self):
        self.setWindowTitle("Audio Analysis Tools")
        self.setGeometry(100, 100, 1200, 600)

        layout = QVBoxLayout()

        self.figure, self.ax = plt.subplots(figsize=(6, 9))
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

        labels_layout = QHBoxLayout()
        self.audio_title_label = QLabel()
        self.sampling_rate_label = QLabel()
        self.coordinates_label = QLabel()

        labels_layout.addWidget(self.audio_title_label)
        labels_layout.addWidget(self.sampling_rate_label)
        labels_layout.addWidget(self.coordinates_label)
        layout.addLayout(labels_layout)

        self.toolbar = NavigationToolbar(self.canvas, self)
        layout.addWidget(self.toolbar)

        self.setLayout(layout)
        self.create_menu_bar()

        self.canvas.mpl_connect('motion_notify_event', self.update_cursor_coordinates)
        self.canvas.mpl_connect('button_press_event', self.handle_click)

    def create_menu_bar(self):
        menubar = QMenuBar(self)
        file_menu = menubar.addMenu('File')

        file_menu.addAction(self.create_action('Read from Audio File', self.read_audio_file))
        file_menu.addAction(self.create_action('Save Graph', self.save_graph))

        options_menu = menubar.addMenu('Options')

        self.pitch_action = self.create_action('Show Pitch', self.toggle_pitch, checkable=True)
        self.intensity_action = self.create_action('Show Intensity', self.toggle_intensity, checkable=True)

        options_menu.addAction(self.pitch_action)
        options_menu.addAction(self.intensity_action)

        formants_submenu = QMenu('Show Formants', self)
        self.formant_actions = []
        for i in range(1, 5):
            action = self.create_action(f'Show f{i}', getattr(self, f'toggle_formant_f{i}'), checkable=True)
            formants_submenu.addAction(action)
            self.formant_actions.append(action)
        options_menu.addMenu(formants_submenu)

        self.layout().setMenuBar(menubar)

    def create_action(self, text, function, shortcut=None, checkable=False):
        action = QAction(text, self)
        action.triggered.connect(function)
        if shortcut:
            action.setShortcut(shortcut)
        action.setCheckable(checkable)
        return action

    def toggle_pitch(self):
        self.show_pitch = not self.show_pitch
        self.redraw_plots()

    def toggle_intensity(self):
        self.show_intensity = not self.show_intensity
        self.redraw_plots()

    def toggle_formant_f1(self):
        self.redraw_plots()

    def toggle_formant_f2(self):
        self.redraw_plots()

    def toggle_formant_f3(self):
        self.redraw_plots()

    def toggle_formant_f4(self):
        self.redraw_plots()

    def redraw_plots(self):
        try:
            self.draw_spectrogram(self.audio_file)

            if self.show_pitch and self.pitch:
                self.draw_pitch(self.pitch)
            if self.show_intensity and self.intensity:
                self.draw_intensity(self.intensity)

            for i, action in enumerate(self.formant_actions, start=1):
                if action.isChecked() and self.formants:
                    self.draw_formants(self.formants, i)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error redrawing plots: {str(e)}")

    def read_audio_file(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Audio File", "", "Audio Files (*.wav *.mp3 *.ogg)")
        if file_name:
            try:
                self.audio_file = file_name
                self.audio_title_label.setText(f'Audio Title: {os.path.basename(file_name)}')
                snd = Sound(file_name)

                self.pitch = snd.to_pitch()
                self.intensity = snd.to_intensity()
                self.formants = snd.to_formant_burg()
                self.sampling_rate_label.setText(f'Sampling Rate: {snd.sampling_frequency} Hz')

                self.redraw_plots()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error reading audio file: {str(e)}")

    def draw_spectrogram(self, audio_file, dynamic_range=70):
        try:
            snd = Sound(audio_file)
            spectrogram = snd.to_spectrogram()

            plt.figure(self.figure.number)
            plt.clf()

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
            QMessageBox.critical(self, "Error", f"Error drawing spectrogram: {str(e)}")

    def draw_pitch(self, pitch):
        try:
            pitch_values = pitch.selected_array['frequency']
            pitch_values[pitch_values == 0] = np.nan
            ax = plt.gca().twinx()
            ax.plot(pitch.xs(), pitch_values, 'o', markersize=2, color='white')
            ax.plot(pitch.xs(), pitch_values, 'o', markersize=1)
            ax.set_ylabel("Pitch [Hz]")
            self.canvas.draw()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error plotting pitch: {str(e)}")

    def draw_intensity(self, intensity):
        try:
            ax = plt.gca().twinx()
            ax.plot(intensity.xs(), intensity.values.T, linewidth=3, color='white')
            ax.plot(intensity.xs(), intensity.values.T, linewidth=1, color='black')
            ax.set_ylabel("Intensity [dB]")
            self.canvas.draw()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error plotting intensity: {str(e)}")

    def draw_formants(self, formants, formant_number):
        try:
            times = formants.xs()
            values = [formants.get_value_at_time(formant_number, t) for t in times]
            plt.plot(times, values, 'o', color='white', markersize=3)
            plt.plot(times, values, 'o', markersize=1)
            self.canvas.draw()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error plotting formants: {str(e)}")

    def update_cursor_coordinates(self, event):
        if event.inaxes:
            x, y = event.xdata, event.ydata
            self.coordinates_label.setText(f'Cursor Coordinates: x={x:.2f}, y={y:.2f}')

    def handle_click(self, event):
        if event.inaxes and event.button == 3 and self.formants:
            x = event.xdata
            f1 = self.formants.get_value_at_time(1, x)
            f2 = self.formants.get_value_at_time(2, x)
            f3 = self.formants.get_value_at_time(3, x)
            f4 = self.formants.get_value_at_time(4, x)

            audio_title = os.path.splitext(os.path.basename(self.audio_file))[0]
            if self.vowel_space_visualizer:
                self.vowel_space_visualizer.update_input_fields_audio(f1, f2, f3, f4, audio_title)

    def save_graph(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Graph", "", "JPEG files (*.jpeg)")
        if file_path:
            try:
                self.figure.savefig(file_path, format='jpeg', dpi=1400)
                QMessageBox.information(self, "Success", "Graph saved successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error saving graph: {str(e)}")
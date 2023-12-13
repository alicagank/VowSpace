import sys
import pandas as pd
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QGridLayout, QComboBox, QFileDialog, QMessageBox, QCheckBox
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import numpy as np
from scipy.spatial import ConvexHull

class ScatterplotVisualizer(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        # Create widgets
        self.label_mode = QLabel('Mode:')
        self.mode_combobox = QComboBox(self)
        self.mode_combobox.addItem('Singular')
        self.mode_combobox.addItem('Multiple')
        self.mode_combobox.currentIndexChanged.connect(self.update_input_fields)

        self.label_vowel = QLabel('Vowel:')
        self.edit_vowel = QLineEdit()

        self.label_F1 = QLabel('F1 Value:')
        self.edit_F1 = QLineEdit()

        self.label_F2 = QLabel('F2 Value:')
        self.edit_F2 = QLineEdit()

        self.label_source = QLabel('Source:')
        self.edit_source = QLineEdit()

        self.checkbox_polygon = QCheckBox('Connect Data with Polygon', self)
        self.checkbox_polygon.stateChanged.connect(self.update_scatterplot)

        self.label_title = QLabel('Add Title:')
        self.edit_title = QLineEdit()
        self.edit_title.textChanged.connect(self.update_title)

        self.button_add_data = QPushButton('Add Data', self)
        self.button_add_data.clicked.connect(self.add_data)
        self.button_add_data.setShortcut(Qt.Key_Return)

        self.button_undo = QPushButton('Undo', self)
        self.button_undo.clicked.connect(self.undo_last_data)

        self.button_clear_data = QPushButton('Clear Data', self)
        self.button_clear_data.clicked.connect(self.clear_data)

        self.button_save_scatterplot = QPushButton('Save Scatterplot', self)
        self.button_save_scatterplot.clicked.connect(self.save_scatterplot)

        self.figure, self.ax = plt.subplots(figsize=(8, 6))
        self.canvas = FigureCanvas(self.figure)

        layout = QVBoxLayout()

        mode_layout = QHBoxLayout()
        mode_layout.addWidget(self.label_mode)
        mode_layout.addWidget(self.mode_combobox)

        layout.addLayout(mode_layout)

        input_grid_layout = QGridLayout()
        input_grid_layout.addWidget(self.label_vowel, 0, 0)
        input_grid_layout.addWidget(self.edit_vowel, 0, 1)
        input_grid_layout.addWidget(self.label_F1, 1, 0)
        input_grid_layout.addWidget(self.edit_F1, 1, 1)
        input_grid_layout.addWidget(self.label_F2, 2, 0)
        input_grid_layout.addWidget(self.edit_F2, 2, 1)
        input_grid_layout.addWidget(self.label_source, 3, 0)
        input_grid_layout.addWidget(self.edit_source, 3, 1)

        layout.addLayout(input_grid_layout)

        title_layout = QHBoxLayout()
        title_layout.addWidget(self.label_title)
        title_layout.addWidget(self.edit_title)

        layout.addLayout(title_layout)

        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(self.button_add_data)
        buttons_layout.addWidget(self.button_undo)
        buttons_layout.addWidget(self.button_clear_data)
        buttons_layout.addWidget(self.button_save_scatterplot)

        layout.addLayout(buttons_layout)

        layout.addWidget(self.checkbox_polygon)

        layout.addWidget(self.canvas)

        self.setLayout(layout)

        self.data = pd.DataFrame(columns=["vowel", "F1", "F2", "source"])

        self.update_input_fields()

        self.setWindowTitle("Vowel Space Visualizer V.1.0")

    def update_input_fields(self):
        mode = self.mode_combobox.currentText()
        self.label_source.setVisible(mode == 'Multiple')
        self.edit_source.setVisible(mode == 'Multiple')

    def add_data(self):
        if not self.validate_input_data():
            return

        mode = self.mode_combobox.currentText()
        vowel = self.edit_vowel.text()
        F1 = float(self.edit_F1.text())
        F2 = float(self.edit_F2.text())

        if mode == 'Singular':
            source = ''
        elif mode == 'Multiple':
            source = self.edit_source.text()
            self.edit_source.clear()

        new_data = pd.DataFrame({"vowel": [vowel], "F1": [F1], "F2": [F2], "source": [source]})
        self.data = pd.concat([self.data, new_data], ignore_index=True)

        self.edit_vowel.clear()
        self.edit_F1.clear()
        self.edit_F2.clear()

        self.edit_vowel.setFocus()

        self.update_scatterplot()

    def validate_input_data(self):
        if not self.edit_vowel.text() or not self.edit_F1.text() or not self.edit_F2.text():
            self.show_error_message("Please fill in all the required fields.")
            return False

        try:
            float(self.edit_F1.text())
            float(self.edit_F2.text())
        except ValueError:
            self.show_error_message("Invalid numeric input for F1 or F2.")
            return False

        return True

    def show_error_message(self, message):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setWindowTitle("Error")
        msg_box.setText(message)
        msg_box.exec_()

    def undo_last_data(self):
        if not self.data.empty:
            self.data = self.data.iloc[:-1]
            self.update_scatterplot()

    def update_scatterplot(self):
        self.ax.clear()

        markers = ['o', 's', '^', 'v', '<', '>', '8', 'p', '*', 'h', '+', 'x', 'D']
        vowel_markers = {v: markers[i % len(markers)] for i, v in enumerate(self.data['vowel'].unique())}

        source_colors = {source: plt.cm.get_cmap('viridis')(i / len(self.data['source'].unique()))
                         for i, source in enumerate(self.data['source'].unique())}

        for v in self.data['vowel'].unique():
            subset = self.data[self.data['vowel'] == v]
            self.ax.scatter(
                subset["F2"], subset["F1"],
                marker=vowel_markers[v],
                c=[source_colors[s] for s in subset["source"]],
                label=v,
                alpha=0.8, edgecolors="w", linewidth=1
            )

            for index, row in subset.iterrows():
                self.ax.annotate(row["vowel"], (row["F2"], row["F1"]), textcoords="offset points", xytext=(0, 5),
                                 ha='center', va='bottom', fontsize=8)

        if self.checkbox_polygon.isChecked() and len(self.data) >= 3:
            for source, group in self.data.groupby("source"):
                points = np.array([group["F2"], group["F1"]]).T
                if len(points) >= 3:
                    hull = ConvexHull(points)
                    polygon = plt.Polygon(points[hull.vertices], closed=True, alpha=0.2, label=source,
                                          facecolor=source_colors[source])
                    self.ax.add_patch(polygon)

        self.ax.yaxis.tick_right()
        self.ax.xaxis.tick_top()

        plt.gca().invert_xaxis()
        plt.gca().invert_yaxis()

        custom_title = self.edit_title.text()
        if custom_title:
            self.ax.set_title(custom_title, pad=20)
        else:
            self.ax.set_title("Vowel Spaces", pad=20)

        self.ax.set_xlabel("F2")
        self.ax.set_ylabel("F1")

        self.ax.legend()

        self.figure.tight_layout()
        self.canvas.draw()

        self.ax.yaxis.set_label_position("right")
        self.ax.xaxis.set_label_position("top")
        self.ax.yaxis.set_ticks_position("right")
        self.ax.xaxis.set_ticks_position("top")

    def clear_data(self):
        self.data = pd.DataFrame(columns=["vowel", "F1", "F2", "source"])
        self.update_scatterplot()

    def save_scatterplot(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Scatterplot", "", "JPEG Files (*.jpg *.jpeg);;All Files (*)", options=options)

        if file_name:
            self.figure.savefig(file_name, format='jpeg', dpi=300)

    def update_title(self):
        custom_title = self.edit_title.text()
        if custom_title:
            self.ax.set_title(custom_title, pad=20)
        else:
            self.ax.set_title("Vowel Spaces", pad=20)

        self.canvas.draw()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    my_app = ScatterplotVisualizer()
    my_app.show()
    sys.exit(app.exec_())

    # Vowel Space Visualizer V.1.0
    # Ali Çağan Kaya, Under MIT lisence
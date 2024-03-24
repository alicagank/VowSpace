from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QComboBox
import os
import subprocess

if os.path.exists('user_dataset.csv'):
    os.remove('user_dataset.csv')
if os.path.exists('vsv.jpg'):
        os.remove('vsv.jpg')
class Vowel_Space_Visualizer(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.setWindowTitle('Vowel Space Visualizer')
        self.setGeometry(100, 100, 400, 200)

        self.label_mode = QLabel('Input Mode:')
        self.mode_combobox = QComboBox()
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

        self.button_add_data = QPushButton('Add Data')
        self.button_add_data.clicked.connect(self.add_data)

        self.button_clear_data = QPushButton('Clear Data')
        self.button_clear_data.clicked.connect(self.clear_data)

        self.button_generate_plot = QPushButton('Generate Scatterplot')
        self.button_generate_plot.clicked.connect(self.generate_scatterplot)

        layout = QVBoxLayout()
        layout.addWidget(self.label_mode)
        layout.addWidget(self.mode_combobox)
        layout.addWidget(self.label_vowel)
        layout.addWidget(self.edit_vowel)
        layout.addWidget(self.label_F1)
        layout.addWidget(self.edit_F1)
        layout.addWidget(self.label_F2)
        layout.addWidget(self.edit_F2)
        layout.addWidget(self.label_source)
        layout.addWidget(self.edit_source)
        layout.addWidget(self.button_add_data)
        layout.addWidget(self.button_clear_data)
        layout.addWidget(self.button_generate_plot)

        self.setLayout(layout)

        # Call the update_input_fields method to ensure correct initial setup
        self.update_input_fields()

    def update_input_fields(self):
        # Show/hide source input based on the selected mode
        mode = self.mode_combobox.currentText()
        self.label_source.setVisible(mode == 'Multiple')
        self.edit_source.setVisible(mode == 'Multiple')

    def add_data(self):
        mode = self.mode_combobox.currentText()

        if mode == 'Singular':
            vowel = self.edit_vowel.text()
            F1 = self.edit_F1.text()
            F2 = self.edit_F2.text()

            if not (vowel and F1 and F2):
                return

            # Create the CSV file if it doesn't exist
            if not os.path.exists('user_dataset.csv'):
                with open('user_dataset.csv', 'w') as file:
                    file.write("vowel,F1,F2\n")

            # Append values to the CSV file
            with open('user_dataset.csv', 'a') as file:
                file.write(f"{vowel},{F1},{F2}\n")

        elif mode == 'Multiple':
            vowel = self.edit_vowel.text()
            F1 = self.edit_F1.text()
            F2 = self.edit_F2.text()
            source = self.edit_source.text()

            if not (vowel and F1 and F2 and source):
                return

            # Create the CSV file if it doesn't exist
            if not os.path.exists('user_dataset.csv'):
                with open('user_dataset.csv', 'w') as file:
                    file.write("vowel,F1,F2,source\n")

            # Append values to the CSV file
            with open('user_dataset.csv', 'a') as file:
                file.write(f"{vowel},{F1},{F2},{source}\n")

        self.edit_vowel.clear()
        self.edit_F1.clear()
        self.edit_F2.clear()
        self.edit_source.clear()

    def generate_scatterplot(self):
        # Run the R script to generate the scatterplot
        subprocess.run(['Rscript', 'scatterplot.R'])
        # Open the JPG file
        subprocess.run(['open', 'vsv.jpg'])

    def clear_data(self):
        # Remove the existing CSV file
        if os.path.exists('user_dataset.csv'):
            os.remove('user_dataset.csv')


def run_app():
    app = QApplication([])
    my_app = Vowel_Space_Visualizer()
    my_app.show()
    app.exec_()


if __name__ == '__main__':
    run_app()

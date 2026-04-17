# components/ipa_window.py

from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QPushButton, QGroupBox

class IPAWindow(QDialog):
    def __init__(self, parent=None):
        super(IPAWindow, self).__init__(parent)
        self.setWindowTitle('IPA Keyboard')
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        grid_layout = QGridLayout()

        # Define IPA letter groups
        letter_groups = [
            ('ɑæɐ', 'A'), ('əɚɵ', 'E'), ('ɛɜɝ', 'ɜ'),
            ('ɪɨ', 'I'), ('ɔœɒ', 'O'), ('ø', 'Ö'),
            ('ʊʉ', 'U'), ('ʕʔ', '2')
        ]

        # Add group boxes with buttons
        for i, (group, label) in enumerate(letter_groups):
            group_box = QGroupBox(label, self)
            group_layout = QHBoxLayout()
            for letter in group:
                button = QPushButton(letter, self)
                button.clicked.connect(lambda checked, l=letter: self.button_clicked(l))
                group_layout.addWidget(button)
            group_box.setLayout(group_layout)
            grid_layout.addWidget(group_box, i // 3, i % 3)

        layout.addLayout(grid_layout)
        self.setLayout(layout)

    def button_clicked(self, letter):
        if hasattr(self.parent(), 'edit_vowel'):
            self.parent().edit_vowel.setText(letter)
        self.close()

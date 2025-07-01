# modulation/df_editor.py

from PyQt5.QtWidgets import QDialog, QTableWidget, QTableWidgetItem, QVBoxLayout, QPushButton

class dfEditor(QDialog):
    def __init__(self, data, parent=None, visualizer=None):
        super().__init__(parent)
        self.data = data
        self.vowel_space_visualizer = visualizer  # Optional reference for updates
        self.setWindowTitle("DataFrame Editor")
        self.setGeometry(100, 100, 700, 500)
        self.initUI()

    def initUI(self):
        self.create_table_widget()
        self.save_button = QPushButton('Save Changes', self)
        self.save_button.clicked.connect(self.save_changes)

        layout = QVBoxLayout()
        layout.addWidget(self.table_widget)
        layout.addWidget(self.save_button)
        self.setLayout(layout)

    def create_table_widget(self):
        self.table_widget = QTableWidget()
        self.table_widget.setRowCount(len(self.data.index))
        self.table_widget.setColumnCount(len(self.data.columns))
        self.table_widget.setHorizontalHeaderLabels(self.data.columns)

        for i in range(len(self.data.index)):
            for j in range(len(self.data.columns)):
                item = QTableWidgetItem(str(self.data.iloc[i, j]))
                self.table_widget.setItem(i, j, item)

    def save_changes(self):
        for i in range(self.table_widget.rowCount()):
            for j in range(self.table_widget.columnCount()):
                item = self.table_widget.item(i, j)
                if item is not None:
                    try:
                        value = float(item.text())
                    except ValueError:
                        value = item.text()
                    self.data.iat[i, j] = value

        # Refresh the scatterplot in VowelSpaceVisualizer if given
        if self.vowel_space_visualizer:
            self.vowel_space_visualizer.update_scatterplot()

"""
This is the development version of VowSpace.
There might be bugs.
Beware of the bügs, they bite.
A büg once bit my sister... No realli!
Mynd you, büg bites Kan be pretti nasti...
"""
import sys
from pathlib import Path

from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon

from vowspace.vowel_space_visualizer import VowelSpaceVisualizer


def resource_path(relative_path):
    # Get absolute path to resource
    if hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS) / relative_path
    return Path(relative_path)


def main():
    app = QApplication(sys.argv)

    icon_path = resource_path("vowspace/assets/vowspace-1024.png")
    app.setWindowIcon(QIcon(str(icon_path)))

    window = VowelSpaceVisualizer()
    window.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()

# VowSpace (Vowel Space Visualizer)
# Ali Çağan Kaya, under the GPL-3.0 license.
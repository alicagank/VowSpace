# main.py

"""
This is the development version of VowSpace.
There might be bugs.
Beware of the bügs, they bite.
A büg once bit my sister... No realli!
Mynd you, büg bites Kan be pretti nasti...
"""
import sys
from PyQt5.QtWidgets import QApplication
from vowel_space_visualizer import VowelSpaceVisualizer


def main():
    app = QApplication(sys.argv)
    window = VowelSpaceVisualizer()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()

# VowSpace (Vowel Space Visualizer) v.1.4.2
# Ali Çağan Kaya, under the GPL-3.0 license.
import sys
from PyQt5.QtWidgets import QApplication
from registerGUI import RegisterGUI


if __name__ == '__main__':
    app = QApplication(sys.argv)
    register_window = RegisterGUI()
    register_window.show()
    sys.exit(app.exec_())

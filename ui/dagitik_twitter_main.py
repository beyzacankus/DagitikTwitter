from PyQt5 import QtWidgets, QtGui, QtCore
import sys

from dagitik_proje_ui import Ui_MainWindow


class Test_Ui(QtWidgets.QMainWindow):
    def __init__(self):
        self.qt_app = QtWidgets.QApplication(sys.argv)
        QtWidgets.QWidget.__init__(self, None)

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)




    def run(self):
        self.show()
        self.qt_app.exec_()


def main():
    app = Test_Ui()
    app.run()


if __name__ == '__main__':
    main()

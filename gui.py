import sys

from PyQt5 import QtWidgets, QtGui

# Giriş Ekranı için UI tasarımı

class LoginWindow(QtWidgets.QWidget):

    def __init__(self):

        super().__init__()

        self.init_ui()

    def init_ui(self):

        self.login_text = QtWidgets.QLabel("Lütfen kullanıcı adınızı girin")

        self.username_space = QtWidgets.QTextEdit()

        self.login_button = QtWidgets.QPushButton("Kaydol / Giriş Yap")

        h_box = QtWidgets.QHBoxLayout()

        h_box.addStretch()

        h_box.addWidget(self.login_text)

        h_box.addWidget(self.username_space)

        h_box.addWidget(self.login_button)



        self.icon = QtWidgets.QLabel()

        self.icon.setPixmap(QtGui.QPixmap("freebird"))



        v_box = QtWidgets.QVBoxLayout()

        v_box.addStretch()

        v_box.addLayout(h_box)

        v_box.addWidget(self.icon)




        self.setLayout(v_box)

        self.login_button.clicked.connect(self.click)

        self.show()

    def click(self):

        pass



app = QtWidgets.QApplication(sys.argv)

pencere = LoginWindow()

sys.exit(app.exec_())


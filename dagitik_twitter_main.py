from PyQt5 import QtWidgets, QtGui, QtCore
import sys
import negotiator
import yayıncı
import util_functions
import protokol
import loggerThread

from ui.dagitik_twitter_ui import Ui_MainWindow


class Test_Ui(QtWidgets.QMainWindow):
    def __init__(self):
        self.qt_app = QtWidgets.QApplication(sys.argv)
        QtWidgets.QWidget.__init__(self, None)

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        #Connect buton fonksiyonu
        self.ui.pushButton.pressed.connect(self.connect_to_twitter)
        self.ui.pushButton_2.pressed.connect(self.log_out)
        self.ui.pushButton_3.pressed.connect(self.unsubscribe)
        self.ui.pushButton_6.pressed.connect(self.block_user)
        self.ui.pushButton_4.pressed.connect(self.unblock_user)
        self.ui.pushButton_7.pressed.connect(self.subscribe)
        self.ui.pushButton_9.pressed.connect(self.send_message)
        self.ui.pushButton_5.pressed.connect(self.share_context)
        self.ui.pushButton_8.pressed.connect(self.refresh_feed)
    def connect_to_twitter(self):
        # girilen nickname ' i al
        user_nickname = self.ui.plainTextEdit.toPlainText()
        print(user_nickname)

        #H


        # Yayıncı peer oluştur veya yayıncı peerına bağlan

        #yayıncı peer

        # Yayıncı peer aracı peer'a bağlanacak

        # Yapılmadıysa kayıt işlemleri yapılacak

        # Feed çekilecek

        # Followerlar çekilecek

        # Followedlar çekilecek

        # Blockedler Çekilecek

        # suggestionlar çekilecek

        # Inbox Çekilecek

        # My shares çekilecek

        # Profile:name yazılacak



    def log_out(self):
        # tüm edit alanları silinecek
        pass

    def unsubscribe(self):

        #takip edilen seçili isimler alınacak

        #takipten çıkarılacak

        pass

    def block_user(self):

        #seçili user alınacak

        #Blocklanacak

        #Blocked yenilenecek

        pass

    def unblock_user(self):
        pass

    def subscribe(self):
        pass

    def share_context(self):
        tweet_data = self.ui.plainTextEdit_4.toPlainText()

        pass

    def send_message(self):
        message_body_data = self.ui.plainTextEdit_5.toPlainText()

        pass

    def refresh_feed(self):
        pass

    def run(self):
        self.show()
        self.qt_app.exec_()


def main():
    app = Test_Ui()
    app.run()


if __name__ == '__main__':
    main()

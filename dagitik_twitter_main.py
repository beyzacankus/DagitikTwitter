from PyQt5 import QtWidgets, QtGui, QtCore
import sys
import negotiator
import loggerThread
import threading
import queue
import socket
import time
import datetime
import uuid

from loggerThread import loggerThread
from util_functions import *
from protokol import *
from blogger import *

from ui.dagitik_twitter_ui import Ui_MainWindow


class Test_Ui(QtWidgets.QMainWindow):
    def __init__(self, my_ip, my_port):
        self.qt_app = QtWidgets.QApplication(sys.argv)
        QtWidgets.QWidget.__init__(self, None)
        self.my_ip = my_ip
        self.my_port = my_port
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
        to_ip = "192.168.1.108"
        to_port = 5662

        data = "HELO " + my_uuid + " " + self.my_ip + " " + str(self.my_port) + " " + tip + " " + user_nickname

        command = {
            "to_ip" : to_ip,
            "to_port" : to_port,
            "data" : data
        }


        out_parser_client(command, my_uuid, tip,logQueue,server_dict, clientSenderQueue, pubkey_dict, block_list,follow_list)
        print(user_nickname)
        self.ui.label_2.setText(user_nickname)
        print(my_uuid)


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
        to_ip = "192.168.1.108"
        to_port = 5662

        data = "PRIV "+message_body_data

        command = {
            "to_ip" : to_ip,
            "to_port" : to_port,
            "data" : data
        }


        out_parser_client(command, my_uuid, tip,logQueue,server_dict, clientSenderQueue, pubkey_dict, block_list,follow_list)

        pass

    def refresh_feed(self):
        pass

    def run(self):
        self.show()
        self.qt_app.exec_()



class OnYuzThread(threading.Thread):
    def __init__(self, ip, port):
        threading.Thread.__init__(self)
        self.ip = ip
        self.port = port

    def run(self):
        app = Test_Ui(self.ip, self.port)
        app.run()

def main():

    logger_thread = loggerThread(logQueue)
    logger_thread.start()

    # Server için soket bağlantıları
    s1 = socket.socket()
    host = "0.0.0.0"
    # port = 4565
    port = int(sys.argv[2])
    s1.bind((host, port))
    s1.listen(5)

    # Kendi ip ve port bilgilerini client alıyor, bunları karşı tarafa atıcak
    # ip = "192.168.0.29"
    ip = str(sys.argv[1])
    # print("Main IP", str(ip))
    port = int(sys.argv[2])

    # Kullanıcı kayıtlarının tutulacağı dictionary
    # write_dictionary ile text dosyası çağırılıp önceki kayıtlar dictionary içerisine yazılıyor

    # list_control(server_dict, logQueue, ip, port, my_uuid)
    # #tüm listenin kontrol edilmesini sağlayan fonksiyon
    # bu kod içerisinde time sleep olduğu için bunu çağıracak thread in başka işi olduğunda bekleme yapıyor

    # --------------------------------------RSA KEYS

    client_thread = clientThread(server_dict, clientSenderQueue, clientReaderQueue, logQueue, ip, port, my_uuid)
    client_thread.start()
    client_dict_thread = clientDictThread(server_dict, logQueue, ip, port, my_uuid)
    client_dict_thread.start()

    OnYuz = OnYuzThread(ip, port)
    OnYuz.start()

    # server name icin
    serverCounter = 0
    while True:
        serverReaderQueue.put(s1.accept())
        server_thread = serverThread("Server Thread - " + str(serverCounter), logQueue, server_dict, my_uuid,
                                     public_key)
        server_thread.start()
        serverCounter += 1


if __name__ == '__main__':
    main()

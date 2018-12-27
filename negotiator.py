import threading
import queue
import socket
import time
import uuid

from loggerThread import loggerThread
from util_functions import *
from protokol import *

#  Bir peer icin hem client hem de server var.

#  Peer'in client tarafi tanimlaniyor.
class clientThread(threading.Thread):
    def __init__(self, clientSenderQueue, clientReaderQueue, logq, ip, port, c_uuid):
        threading.Thread.__init__(self)
        self.clientReaderQueue = clientReaderQueue
        self.clientSenderQueue = clientSenderQueue
        self.logq = logq
        self.ip = ip
        self.port = port
        self.c_uuid = c_uuid
        
    def run(self):
        s = socket.socket()

        log = "Aracı client çalışmaya başladı.\n"
        self.logq.put(log)

        while True:
            my_dict = {
                "ip": self.ip,
                "server_port": "12345",  # server portu
                "c_uuid": self.c_uuid
            }

            peer_dict = {}
            writeToPeerDictionary(peer_dict, self.logq, "araci")

            while True:
                # peer_dict'te kayitli her kullanici ile iletisim baslatma
                for key in peer_dict:
                    # Kullaniciya ait bilgiler ayristiriliyor
                    ip, port, type, nick = split_HELO_parametres(peer_dict[key])
                    # Kullaniciyla baglanti baslatiliyor
                    port = int(port)
                    try:
                        s.connect((ip, port))

                        senderThread = clientSender(self.logq, self.clientSenderQueue, s)
                        senderThread.start()
                        readerThread = clientReader(self.logq, self.clientReaderQueue, s)
                        readerThread.start()

                        log = "Aracıdan IP: " + str(ip) + " Port: " + str(port) + " ile bağlantı kuruldu.\n"
                        self.logq.put(log)

                        msg = "HELO " + str(self.c_uuid) + " " + str(self.ip) + " " + "12345" + " " + "A" + ""  # Burada araci kendi ipsini ve server taradinin portunu yolluyor. Nick de aracida onemli olmadigi icin bos.
                        self.clientSenderQueue.put(msg)
                    except ConnectionRefusedError:
                        continue
                time.sleep(60)


# Client için sender thread
class clientSender(threading.Thread):
    def __init__(self, logq, clientSenderQueue, s):
        threading.Thread.__init__(self)
        self.logq = logq
        self.clientSenderQueue = clientSenderQueue
        self.s = s

    def run(self):
        log = "Aracı Client Sender Thread çalışmaya başladı.\n"
        self.logq.put(log)

        while True:
            # Client queue'den alınanlar servera yollanıyor
            while not self.clientSenderQueue.empty():
                data = self.clientSenderQueue.get()
                self.s.send(data.encode())

class clientReader(threading.Thread):
    def __init__(self, logq, clientReaderQueue, s):
        threading.Thread.__init__(self)
        self.logq = logq
        self.clientReaderQueue = clientReaderQueue
        self.s = s

    def run(self):
        log = "Aracı Client Reader Thread çalışmaya başladı.\n"
        self.logq.put(log)

        while True:
            msg = self.s.recv(1024).decode()
            x = inc_parser_client(msg, "A", self.clientReaderQueue)


# Server için thread
class serverThread(threading.Thread):
    def __init__(self, serverq, logq, soket, peer_dict):
        threading.Thread.__init__(self)
        self.serverq = serverq
        self.logq = logq
        self.soket = soket
        self.peer_dict = peer_dict # uuid ve baglanti adreslerinin oldugu dictionary

    def run(self):
        log = "Aracı Server Thread çalışmaya başladı.\n"
        self.logq.put(log)

        while True:
            c, addr = self.soket.accept()
            log = "Aracı şu adresle bağlantı sağlandı: " + str(addr)
            self.logq.put(log)

            # Kullanıcı kayıt olup olmadığı flag ile tutuluyor
            flag = 0
            c_uuid = ""

            while True:
                rps = c.recv(1024).decode()

                # Bağlanıldı mesajı
                if rps[:4] == "HELO":
                    c_uuid = rps[5:19]
                    # Eğer önceden kayıtlıysa "WLCM" cevabı veriliyor
                    if c_uuid in self.peer_dict:
                        send = "WLCM " + c_uuid
                        c.send(send.encode())
                    # Kayıtlı değilse yeni kayıt oluşturup WAIT cevabı veriliyor
                    else:
                        self.peer_dict[c_uuid] = rps[20:len(rps)]
                        data = c_uuid + " -" + rps[19:len(rps)]
                        appendToPeerDictionary(data, self.logq, "araci")
                        send = "WAIT " + c_uuid
                        c.send(send.encode())

                        log = "Aracıda " + str(c_uuid) + " bilgileri sözlüğe kaydedildi.\n"
                        self.logq.put(log)

                    c.send('\nThank you for connecting!\n'.encode())

                # Dictionary'deki kayıtlar yollanıyor
                elif rps[:4] == "LIST":
                    if flag == 1:
                        c.send(str(self.peer_dict).encode())
                    else:
                        c.send("AUTH".encode())

                # Bağlantı testi, eğer UUID aynıysa flag = 1 olur ve kullanıcı kaydolunur.
                elif rps[:4] == "SUID":
                    rps = "AUID " + c_uuid
                    c.send(rps.encode())
                    flag = 1

                # Hata mesajı
                else:
                    c.send("ERRO".encode())


def main():
    logQueue = queue.Queue()
    logger_thread = loggerThread(logQueue)
    logger_thread.start()

    # Server için soket bağlantıları
    s1 = socket.socket()
    host = "0.0.0.0"
    port = 12345
    s1.bind((host, port))
    s1.listen(5)
    
    # Kendi ip ve port bilgilerini client alıyor, bunları karşı tarafa atıcak
    ip = socket.gethostbyname(socket.gethostname())
    port = 12345

    # Kullanıcı kayıtlarının tutulacağı dictionary
    # write_dictionary ile text dosyası çağırılıp önceki kayıtlar dictionary içerisine yazılıyor
    server_dict = {}
    writeToPeerDictionary(server_dict, logQueue, "araci")

    # MAC adresiyle UUID
    client_uuid = uuid.getnode()

    ServerQueue = queue.Queue()
    clientSenderQueue = queue.Queue()
    clientReaderQueue = queue.Queue()

    server_thread = serverThread(ServerQueue, logQueue, s1, server_dict)
    server_thread.start()
    client_thread = clientThread(clientSenderQueue, clientReaderQueue, logQueue, ip, port, client_uuid)
    client_thread.start()





if __name__ == '__main__':
    main()

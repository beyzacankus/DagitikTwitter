import threading
import queue
import socket
import time
import uuid

from loggerThread import loggerThread
from util_functions import *

#  Bir peer icin hem client hem de server var.

#  Peer'in client tarafi tanimlaniyor.
class clientThread(threading.Thread):
    def __init__(self, clientq, logq, ip, port, c_uuid):
        threading.Thread.__init__(self)
        self.clientq = clientq
        self.logq = logq
        self.ip = ip
        self.port = port
        self.c_uuid = c_uuid
        
    def run(self):
        s = socket.socket()

        log = "Aracı client çalışmaya başladı.\n"
        self.logq.put(log)

        # Mesajları soketin diğer ucuna yollamak için sender Thread oluşturuluyor
        sender = clientSender(self.logq, self.clientq, s)
        sender.start()

        while True:
            inp = input()
            inp = inp.strip("\n")

            if inp[:4] == "HELO":

                # Mesajla gelen parametreler parse_input metoduyla ayrıştırılıyor
                # Buradaki ip ve port bağlanılan server'ın ipleri
                server_ip, server_port, nick = parse_input(inp)
                host = server_ip
                port = int(server_port)

                # Alınan port ve input bilgileri ile bağlantı kuruluyor
                s.connect((host, port))
                type = "A"

                log = "Aracıdan IP: "+ str(host) + " Port: " + str(port) + " ile bağlantı kuruldu.\n"
                self.logq.put(log)

                # Client oluşturulduğu zaman atanan UUID ve tip bilgileri de eklenip HELO mesajı
                # tüm parametreler ile yollanıyor. HELO mesajına kendi ip ve portu koyuluyor,
                # çünkü karşı tarafın listesine kendi ip ve portunu vermek zorunda. 
                data = inp[:4] + " " + str(self.c_uuid) + " " + self.ip + " " + str(self.port) + " " + type + " " + nick
                self.clientq.put(data)

            else:
                self.clientq.put(inp)

            time.sleep(1)
            print(s.recv(1024).decode())

        
# Client için sender thread
class clientSender(threading.Thread):
    def __init__(self, logq, clientq, s):
        threading.Thread.__init__(self)
        self.logq = logq
        self.clientq = clientq
        self.s = s

    def run(self):
        log = "Aracı Client Sender Thread çalışmaya başladı.\n"
        self.logq.put(log)

        while True:
            # Client queue'den alınanlar servera yollanıyor
            while not self.clientq.empty():
                data = self.clientq.get()
                self.s.send(data.encode())


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
                        data = c_uuid + " -" + rps[19:len(rps)] + " NB"  # Sonradan ozellikle yayincilarda hangi kullanıcının engellendigini gormemizi saglayacak: NB (Engelli Degil) - B (Engelli)
                        appendToPeerDictionary(data, self.logq)
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
    writeToPeerDictionary(server_dict, logQueue)

    # MAC adresiyle UUID
    client_uuid = uuid.getnode()

    ServerQueue = queue.Queue()
    ClientQueue = queue.Queue()

    server_thread = serverThread(ServerQueue, logQueue, s1, server_dict)
    server_thread.start()
    client_thread = clientThread(ClientQueue, logQueue, ip, port, client_uuid)
    client_thread.start()





# HELO mesajıyla alınan input ip,port ve nick parametrelerine ayrıştırılıyor
def parse_input(inp):
    inp = str(inp)
    nick = ""
    ip = ""
    port = ""
    bann = ""
    delimiter = " "
    list = inp.split(delimiter)
    ip = list[0]
    port = list[1]
    type = list[2]
    nick = list[3]
    bann = list[4]

    return ip, port, nick


if __name__ == '__main__':
    main()

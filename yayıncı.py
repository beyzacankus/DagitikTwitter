import threading
import queue
import socket
import time
import uuid
import chardet

from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto import Random

from loggerThread import loggerThread
from util_functions import *

#  Bir peer icin hem client hem de server var.
#  Peer'in client tarafi tanimlaniyor.
class clientThread(threading.Thread):
    def __init__(self, clientq, logq, ip, port, c_uuid, public_key, private_key):
        threading.Thread.__init__(self)
        self.clientq = clientq
        self.logq = logq
        self.ip = ip
        self.port = port
        self.c_uuid = c_uuid
        self.public_key = public_key
        self.private_key = private_key

    def run(self):
        s = socket.socket()

        log = "Yayıncı Client çalışmaya başladı.\n"
        self.logq.put(log)
        
        # Mesajları soketin diğer ucuna yollamak için sender Thread oluşturuluyor
        sender = clientSender(self.logq, self.clientq, s)
        sender.start()

        # Karşı tarafın public keyini tutmak için
        public_key = ""

        while True:
            inp = input()
            inp = inp.strip("\n")

            # HELO <ip> <port> <nick>
            if inp[:4] == "HELO":
                # Mesajla gelen parametreler parse_input metoduyla ayrıştırılıyor
                server_ip, server_port, nick = parse_input(inp[5:])
                host = server_ip
                port = int(server_port)

                # Alınan port ve input bilgileri ile bağlantı kuruluyor
                s.connect((host, port))
                type = "Y"

                log = "Yayıncıdan IP: "+ str(host) + " Port: " + str(port) + " ile bağlantı kuruldu.\n"
                self.logq.put(log)
                
                # Client oluşturulduğu zaman atanan UUID ve tip bilgileri de eklenip HELO mesajı
                # tüm parametreler ile yollanıyor.
                data = inp[:4] + " " + str(self.c_uuid) + " " + str(self.ip) + " " + str(self.port) + " " + type + " " + nick
                self.clientq.put(data)

            elif inp[:4] == "SUID" or "LIST" or "PUBR":
                self.clientq.put(inp)

            # Diğer mesajlar şifrelenip öyle gönderiliyor.
            else:
                encryptor = PKCS1_OAEP.new(public_key)
                encrypted = encryptor.encrypt(inp.encode())
                self.clientq.put(encrypted)

            time.sleep(1)

            rps = s.recv(1024).decode()
            if rps[:4] == "PUBO":
                public_key = RSA.import_key(rps[5:len(rps)])
            print(rps)


# Client için sender thread
class clientSender(threading.Thread):
    def __init__(self, logq, clientq, s):
        threading.Thread.__init__(self)
        self.logq = logq
        self.clientq = clientq
        self.s = s

    def run(self):
        
        log = "Yayıncı Client Sender Thread çalışmaya başladı.\n"
        self.logq.put(log)
        
        while True:
            # Client queue'den alınanlar servera yollanıyor
            while not self.clientq.empty():
                data = self.clientq.get()
                # Eğer şifrelenmiş bir mesajsa zaten byte şeklinde geleceğinden direk yollanıyor
                if type(data) is bytes:
                    self.s.send(data)
                # Diğer mesajlar encode edilip yollanıyor
                else:
                    self.s.send(data.encode())


# Server için thread
class serverThread(threading.Thread):
    def __init__(self, serverq, logq, soket, dict, public_key, private_key):
        threading.Thread.__init__(self)
        self.serverq = serverq
        self.logq = logq
        self.soket = soket
        self.dict = dict
        self.public_key = public_key
        self.private_key = private_key

    def run(self):
        log = "Yayıncı Server Thread çalışmaya başladı.\n"
        self.logq.put(log)
        
        while True:
            c, addr = self.soket.accept()
            
            log = "Yayıncı şu adresle bağlantı sağlandı: " + str(addr)
            self.logq.put(log)
            
            # Kullanıcı kayıt olup olmadığı flag ile tutuluyor
            flag = 0
            c_uuid = ""
            # gelen mesajları decrypt etmek için kendi private key'i ile decryptor oluşturuyor
            decryptor = PKCS1_OAEP.new(self.private_key)

            while True:
                # byte olarak alınıyor
                rps = c.recv(1024)

                # Eğer şifrelenmemiş bir mesajsa ascii encodingi ile geliyor
                if chardet.detect(rps)['encoding'] == 'ascii':
                    # decode edilip bytetan string formatına çevriliyor
                    rps = rps.decode()
                else:
                    # şifrelenmiş bir mesajsa decrypt edilip öyle decode ediliyor
                    rps = decryptor.decrypt(rps)
                    rps = rps.decode()

                # Bağlanıldı mesajı
                if rps[:4] == "HELO":
                    c_uuid = rps[5:19]
                    # Eğer önceden kayıtlıysa "WLCM" cevabı veriliyor
                    if c_uuid in self.dict:
                        send = "WLCM " + c_uuid
                        c.send(send.encode())
                    # Kayıtlı değilse yeni kayıt oluşturup WAIT cevabı veriliyor
                    else:
                        self.dict[c_uuid] = rps[20:len(rps)]
                        data = c_uuid + " -" + rps[19:len(rps)]
                        appendToPeerDictionary(data, self.logq, "yayinci")
                        send = "WAIT " + c_uuid
                        c.send(send.encode())
                    c.send('\nThank you for connecting!'.encode())

                # Dictionary'deki kayıtlar yollanıyor
                elif rps[:4] == "LIST":
                    if flag == 1:
                        c.send(str(self.dict).encode())
                    else:
                        c.send("AUTH".encode())

                # Bağlantı testi
                elif rps[:4] == "SUID":
                    rps = "AUID " + c_uuid
                    c.send(rps.encode())
                    flag = 1

                # Public Key yollama
                elif rps[:4] == "PUBR":
                    if flag == 1:
                        rps = "PUBO " + self.public_key.exportKey("PEM").decode()
                        c.send(rps.encode())
                    else:
                        c.send("AUTH".encode())

                # Özel mesaj
                elif rps[:4] == "PRIV":
                    if flag == 1:
                        rps = rps[5:]
                        self.logq.put(rps)
                        c.send(("PRIO " + rps).encode())
                    else:
                        c.send("AUTH".encode())

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

    ip = socket.gethostbyname(socket.gethostname())
    port = 12345

    # Kullanıcı kayıtlarının tutulacağı dictionary
    peer_dict = {}
    # writeToPeerDictionary ile text dosyası çağırılıp önceki kayıtlar dictionary içerisine yazılıyor
    writeToPeerDictionary(peer_dict, logQueue, "yayinci")

    # Public ve private keyler
    random_generator = Random.new().read
    new_key = RSA.generate(2048, randfunc=random_generator)
    public_key = new_key.publickey()
    private_key = new_key

    # MAC adresiyle UUID
    client_uuid = uuid.getnode()

    ServerQueue = queue.Queue()
    ClientQueue = queue.Queue()

    server_thread = serverThread(ServerQueue, logQueue, s1, peer_dict, public_key, private_key)
    server_thread.start()
    client_thread = clientThread(ClientQueue, logQueue,  ip, port, client_uuid, public_key, private_key)
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
#    type = list[2]
    nick = list[2]
 #   bann = list[4]

    return ip, port, nick


if __name__ == '__main__':
    main()

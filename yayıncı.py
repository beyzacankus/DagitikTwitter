import threading
import queue
import socket
import time
import uuid
import chardet
from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto import Random


class loggerThread(threading.Thread):
    def __init__(self, logq):
        threading.Thread.__init__(self)
        self.logq = logq

    def run(self):
        while True:
            data = self.logq.get()
            print(data)


#  Bir peer icin hem client hem de server var.

#  Peer'in client tarafi tanimlaniyor.
class clientThread(threading.Thread):
    def __init__(self, clientq, serverq, logq, ip, port, c_uuid, public_key, private_key):
        threading.Thread.__init__(self)
        self.clientq = clientq
        self.serverq = serverq
        self.logq = logq
        self.ip = ip
        self.port = port
        self.c_uuid = c_uuid
        self.public_key = public_key
        self.private_key = private_key

    def run(self):
        s = socket.socket()

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
                server_ip, server_port, nick = parse_input(inp)
                host = server_ip
                port = int(server_port)

                # Alınan port ve input bilgileri ile bağlantı kuruluyor
                s.connect((host, port))
                type = "Y"

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
    def __init__(self, serverq, clientq, logq, soket, dict, public_key, private_key):
        threading.Thread.__init__(self)
        self.serverq = serverq
        self.clientq = clientq
        self.logq = logq
        self.soket = soket
        self.dict = dict
        self.public_key = public_key
        self.private_key = private_key

    def run(self):
        while True:
            c, addr = self.soket.accept()
            log = "Got connection from " + str(addr)
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
                        append_dictionary(data)
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

    # Server için soket bağlantıları
    s1 = socket.socket()
    host = "0.0.0.0"
    port = 12345
    s1.bind((host, port))
    s1.listen(5)

    ip = socket.gethostbyname(socket.gethostname())
    port = 12345

    # Kullanıcı kayıtlarının tutulacağı dictionary
    # write_dictionary ile text dosyası çağırılıp önceki kayıtlar dictionary içerisine yazılıyor
    server_dict = {}
    write_dictionary(server_dict)

    # Public ve private keyler
    random_generator = Random.new().read
    new_key = RSA.generate(2048, randfunc=random_generator)
    public_key = new_key.publickey()
    private_key = new_key

    # MAC adresiyle UUID
    client_uuid = uuid.getnode()

    queueLock = threading.Lock()
    logQueue = queue.Queue()
    ServerQueue = queue.Queue()
    ClientQueue = queue.Queue()
    threads = []

    server_thread = serverThread(ServerQueue, ClientQueue, logQueue, s1, server_dict, public_key, private_key)
    server_thread.start()
    client_thread = clientThread(ClientQueue, ServerQueue, logQueue,  ip, port, client_uuid, public_key, private_key)
    client_thread.start()
    logger_thread = loggerThread(logQueue)
    logger_thread.start()


# text dosyasındaki kayıtlar dictionary'e yazılıyor.UUID key değeri, geri kalan bilgiler(ip,port,tip,nick) valuelar
def write_dictionary(server_dict):
    fid = open("dictionary.txt", "r+")
    for line in fid:
        listedline = line.strip().split('-')
        if len(listedline) > 1:
            server_dict[listedline[0].strip()] = listedline[1].strip()
    fid.close()


# yeni kaydı text dosyasına ekleme
def append_dictionary(data):
    f = open("dictionary.txt", "a+")
    f.write("%s" % data)
    f.close()


# HELO mesajıyla alınan input ip,port ve nick parametrelerine ayrıştırılıyor
def parse_input(inp):
    inp = str(inp)
    i = 6
    j = 0
    nick = ""
    ip = ""
    port = ""
    while i < len(inp):
        if inp[i - 1] == " ":
            ip = inp[5:i - 1]
            j = i
            while i < len(inp):
                if inp[i - 1] == " ":
                    port = inp[j:i - 1]
                    j = i
                    nick = inp[j:len(inp)]
                i += 1
        i += 1
    return ip, port, nick


if __name__ == '__main__':
    main()
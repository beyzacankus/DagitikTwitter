import threading
import queue
import socket
import time
import uuid


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
    def __init__(self, clientq, serverq, logq, ip, port, c_uuid):
        threading.Thread.__init__(self)
        self.clientq = clientq
        self.serverq = serverq
        self.logq = logq
        self.ip = ip
        self.port = port
        self.c_uuid = c_uuid

    def run(self):
        s = socket.socket()

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
        while True:
            # Client queue'den alınanlar servera yollanıyor
            while not self.clientq.empty():
                data = self.clientq.get()
                self.s.send(data.encode())


# Server için thread
class serverThread(threading.Thread):
    def __init__(self, serverq, clientq, logq, soket, dict):
        threading.Thread.__init__(self)
        self.serverq = serverq
        self.clientq = clientq
        self.logq = logq
        self.soket = soket
        self.dict = dict

    def run(self):
        while True:
            c, addr = self.soket.accept()
            log = "Got connection from " + str(addr)
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
                    c.send('\nThank you for connecting!\n'.encode())

                # Dictionary'deki kayıtlar yollanıyor
                elif rps[:4] == "LIST":
                    if flag == 1:
                        c.send(str(self.dict).encode())
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
    write_dictionary(server_dict)

    # MAC adresiyle UUID
    client_uuid = uuid.getnode()

    queueLock = threading.Lock()
    logQueue = queue.Queue()
    ServerQueue = queue.Queue()
    ClientQueue = queue.Queue()
    threads = []

    server_thread = serverThread(ServerQueue, ClientQueue, logQueue, s1, server_dict)
    server_thread.start()
    client_thread = clientThread(ClientQueue, ServerQueue, logQueue,ip,port, client_uuid)
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

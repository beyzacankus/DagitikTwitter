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
            if data == "Quit":
                data = "Quit received " + " - " + time.ctime(time.time())
                print(data)
                break
            print(data)


#  Bir peer icin hem client hem de server var.

#  Peer'in client tarafi tanimlaniyor.
class clientThread(threading.Thread):
    def __init__(self, clientq, serverq, logq, c_uuid):
        threading.Thread.__init__(self)
        self.clientq = clientq
        self.serverq = serverq
        self.logq = logq
        self.c_uuid = c_uuid

    def run(self):
        host = socket.gethostbyname(socket.gethostname())
        port = 12345
        s = socket.socket()
        s.connect((host, port))
        type = "A"
        # Kullanıcı bilgileri datanın içine yazılıyor
        data = str(self.c_uuid) + " " + host + " " + str(port) + " " + type
        # Client icin hem reader hem de writer thread calisir
        reader = clientReader(self.logq, self.clientq, s, data)
        sender = clientSender(self.clientq, s)

        reader.start()
        sender.start()


# Client için sender thread
class clientSender(threading.Thread):
    def __init__(self, clientq, s):
        threading.Thread.__init__(self)
        self.clientq = clientq
        self.s = s

    def run(self):
        print("Sender Thread Active")
        while True:

            # Client queue'den alınanlar servera yollanıyor
            while not self.clientq.empty():
                data = self.clientq.get()
                data = data.strip("\n")
                self.s.send(data.encode())


# Client için reader thread
class clientReader(threading.Thread):
    def __init__(self, logq, clientq, s, data):
        threading.Thread.__init__(self)
        self.logq = logq
        self.clientq = clientq
        self.s = s
        self.data = data

    def run(self):
        print("Reader Thread Active")
        # Alınan input Client queue'ye koyuluyor
        while True:
            inp = input()
            inp = inp.strip("\n")
            # Eğer "HELO" mesajıysa kullanıcı bilgileri eklenip yollanıyor
            if inp[:4] == "HELO":
                data = inp[:4] + " " + self.data + inp[4:len(self.data)]
                self.clientq.put(data)
            else:
                self.clientq.put(inp)
            time.sleep(2)
            print(self.s.recv(1024).decode())


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
            print('Got connection from', addr)
            # Kullanıcı kayıt olduğu zaman flag=1 olur
            # Eğer kayıt olmadan LIST komutu verilirse AUTH hatası
            flag = 0
            while True:
                rps = c.recv(1024).decode()
                if rps[:4] == "HELO":
                    c_uuid = rps[5:19]
                    # Eğer önceden kayıtlıysa "WLCM" cevabı veriliyor
                    if c_uuid in self.dict:
                        send = "WLCM " + c_uuid
                        c.send(send.encode())
                        flag = 1
                    # Kayıtlı değilse yeni kayıt oluşturup WAIT cevabı veriliyor
                    else:
                        self.dict[c_uuid] = rps[20:len(rps)]
                        data = c_uuid + " -" + rps[19:len(rps)]
                        append_dictionary(data)
                        send = "WAIT " + c_uuid
                        c.send(send.encode())
                        flag = 1
                    c.send('\nThank you for connecting!\n'.encode())

                # Dictionary'deki kayıtlar yollanıyor
                elif rps[:4] == "LIST":
                    if flag == 1:
                        c.send(str(self.dict).encode())
                    else:
                        c.send("AUTH".encode())

                # Bağlantı testi
                elif rps[:4] == "SUID":
                    rps = "AUID "
                    c.send(rps.encode())

                else:
                    c.send("ERRO".encode())


def main():

    # Server için soket bağlantıları
    s1 = socket.socket()
    host = "0.0.0.0"
    port = 12345
    s1.bind((host, port))
    s1.listen(5)

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
    client_thread = clientThread(ClientQueue, ServerQueue, logQueue, client_uuid)
    client_thread.start()


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


if __name__ == '__main__':
    main()

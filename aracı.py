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
    def __init__(self, clientq, logq, c_uuid):
        threading.Thread.__init__(self)
        self.clientq = clientq
        self.logq = logq
        self.c_uuid = c_uuid

    def run(self):
        host = socket.gethostbyname(socket.gethostname())
        port = 12345
        s = socket.socket()
        s.connect((host, port))
        type = "A"

        # Kullanici bilgileri datanin içine yaziliyor
        data = str(self.c_uuid) + " " + host + " " + str(port) + " " + type

        # Client icin hem reader hem de writer thread calisir
        reader = clientReader(self.logq, self.clientq, s, data)
        sender = clientSender(self.clientq, s)

        reader.start()
        sender.start()


# Client icin sender thread
class clientSender(threading.Thread):
    def __init__(self, clientq, soket):
        threading.Thread.__init__(self)
        self.clientq = clientq
        self.soket = soket

    def run(self):
        print("Client Sender Thread Active")
        while True:
            # Client queue'den alinanlar diger peer'in serverina yollaniyor
            while not self.clientq.empty():
                data = self.clientq.get()
                data = data.strip("\n")
                self.soket.send(data.encode())


# Client icin reader thread
class clientReader(threading.Thread):
    def __init__(self, logq, clientq, soket, data):
        threading.Thread.__init__(self)
        self.logq = logq
        self.clientq = clientq
        self.soket = soket
        self.data = data

    def run(self):
        print("Client Reader Thread Active")
        # Alinan input Client queue'ye koyuluyor
        while True:
            inp = input()
            inp = inp.strip("\n")
            # Eger "HELO" mesajiysa kullanici bilgileri eklenip yollaniyor
            if inp[:4] == "HELO":
                data = inp[:4] + " " + self.data + inp[4:len(self.data)]
                self.clientq.put(data)
            else:
                self.clientq.put(inp)
            time.sleep(2)
            print(self.soket.recv(1024).decode())


# Server icin thread
class serverThread(threading.Thread):
    def __init__(self, serverq, logq, soket, dict):
        threading.Thread.__init__(self)
        self.serverq = serverq
        self.logq = logq
        self.soket = soket
        self.dict = dict

    def run(self):
        while True:
            c, addr = self.soket.accept()
            print('Got connection from', addr)
            # Kullanici kayit oldugu zaman flag=1 olur
            # Eger kayit olmadan LIST komutu verilirse AUTH hatasi
            flag = 0
            while True:
                rps = c.recv(1024).decode()
                if rps[:4] == "HELO":
                    c_uuid = rps[5:19]
                    # Eger onceden kayitliysa "WLCM" cevabi veriliyor
                    if c_uuid in self.dict:
                        send = "WLCM " + c_uuid
                        c.send(send.encode())
                        flag = 1
                    # Kayitli degilse yeni kayit olusturup WAIT cevabi veriliyor
                    else:
                        self.dict[c_uuid] = rps[20:len(rps)]
                        data = c_uuid + " -" + rps[19:len(rps)]
                        append_dictionary(data)
                        send = "WAIT " + c_uuid
                        c.send(send.encode())
                        flag = 1
                    c.send('\nThank you for connecting!\n'.encode())

                # Dictionary'deki kayitlar yollaniyor
                elif rps[:4] == "LIST":
                    if flag == 1:
                        c.send(str(self.dict).encode())
                    else:
                        c.send("AUTH".encode())

                # Baglanti testi
                elif rps[:4] == "SUID":
                    rps = "AUID "
                    c.send(rps.encode())

                else:
                    c.send("ERRO".encode())


def main():

    # Server icin soket baglantilari
    s1 = socket.socket()
    host = "0.0.0.0"
    port = 12345
    s1.bind((host, port))
    s1.listen(5)

    # Kullanici kayitlarinin tutulacagi dictionary
    # write_dictionary ile text dosyasi çagirilip onceki kayitlar dictionary icerisine yaziliyor
    server_dict = {}
    write_dictionary(server_dict)

    # MAC adresiyle UUID
    client_uuid = uuid.getnode()
    logQueue = queue.Queue()
    ServerQueue = queue.Queue()
    ClientQueue = queue.Queue()
    threads = []

    server_thread = serverThread(ServerQueue, logQueue, s1, server_dict)
    server_thread.start()
    client_thread = clientThread(ClientQueue, logQueue, client_uuid)
    client_thread.start()


# text dosyasındaki kayitlar dictionary'e yazıliyor. UUID key degeri, geri kalan bilgiler(ip,port,tip,nick) valuelar
def write_dictionary(server_dict):
    fid = open("dictionary.txt", "r+")
    for line in fid:
        listedline = line.strip().split('-')
        if len(listedline) > 1:
            server_dict[listedline[0].strip()] = listedline[1].strip()
    fid.close()

# yeni kaydi text dosyasina ekleme
def append_dictionary(data):
    f = open("dictionary.txt", "a+")
    f.write("%s" % data)
    f.close()


if __name__ == '__main__':
    main()

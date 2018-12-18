import threading
import queue
import socket
import time
import uuid


class loggerThread(threading.Thread):
    def __init__(self, q):
        threading.Thread.__init__(self)
        self.q = q

    def run(self):
        log_runner(self.q)


def log_runner(logq):
    while True:
        queueLock.acquire()
        data = logq.get()
        if data == "Quit":
            data = "Quit received " + " - " + time.ctime(time.time())
            print(data)
            break
        print(data)
        queueLock.release()


class senderThread(threading.Thread):
    def __init__(self, clientq, s):
        threading.Thread.__init__(self)
        self.clientq = clientq
        self.server = s

    def run(self):
        outgoing_parser(self.clientq, self.server)


def outgoing_parser(clientq, s):
    print("Sender Thread Active")
    while True:
        while not clientq.empty():
            data = clientq.get()
            data = data.strip("\n")
            if data[:4] == "HELO":
                s.send(data.encode())


class readerThread(threading.Thread):
    def __init__(self, logq, clientq, server, data):
        threading.Thread.__init__(self)
        self.logq = logq
        self.clientq = clientq
        self.server = server
        self.data = data

    def run(self):
        incoming_parser(self.logq, self.clientq, self.server, self.data)


def incoming_parser(logq, clientq, s, data):
    print("Reader Thread Active")
    while True:
        inp = input()
        inp = inp.strip("\n")
        data = inp[:4] + " " + data + inp[4:len(data)]
        clientq.put(data)
        time.sleep(2)
        print(s.recv(1024).decode())


class serverThread(threading.Thread):
    def __init__(self, serverq, clientq, logq, soket, dict):
        threading.Thread.__init__(self)
        self.serverq = serverq
        self.clientq = clientq
        self.logq = logq
        self.soket = soket
        self.dict = dict

    def run(self):
        server_parser(self.serverq, self.clientq, self.logq, self.soket, self.dict)


def server_parser(serverq, clientq, logq, soket, dict):
    while True:
        c, addr = soket.accept()
        print('Got connection from', addr)
        c.send('Thank you for connecting!\n'.encode())
        while True:
            rps = c.recv(1024).decode()
            if rps[:4] == "HELO":
                c_uuid = rps[5:19]
                if c_uuid in dict:
                    c.send("WLCM".encode())
                else:
                    dict[c_uuid] = rps[20:len(rps)]
                    print(c_uuid)
                    print(dict[c_uuid])
                    data = c_uuid + " -" + rps[19:len(rps)]
                    append_dictionary(data)
                    c.send("WAIT".encode())


class clientThread(threading.Thread):
    def __init__(self, clientq, serverq, logq, c_uuid):
        threading.Thread.__init__(self)
        self.clientq = clientq
        self.serverq = serverq
        self.logq = logq
        self.c_uuid = c_uuid

    def run(self):
        client_parser(self.clientq, self.serverq, self.logq, self.c_uuid)


def client_parser(clientq, serverq, logq, c_uuid):
    host = socket.gethostbyname(socket.gethostname())
    port = 12345
    s = socket.socket()
    s.connect((host, port))
    type = "aracı"
    data = str(c_uuid) + " " + host + " " + str(port) + " " + type
    reader = readerThread(logq, clientq, s, data)
    sender = senderThread(clientq, s)
    reader.start()
    sender.start()


def main():

    s1 = socket.socket()
    host = "0.0.0.0"
    port = 12345
    s1.bind((host, port))
    s1.listen(5)

    server_dict = {}


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


def append_dictionary(data):
    f = open("dictionary.txt", "a+")
    f.write("%s\r\n" % data)
    f.close()


if __name__ == '__main__':
    main()
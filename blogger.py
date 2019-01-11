import threading
import queue
import socket
import time
import datetime
import uuid

from loggerThread import loggerThread
from util_functions import *
from protokol import *

# Kuyruklar
logQueue = queue.Queue()
clientSenderQueue = queue.Queue()
clientReaderQueue = queue.Queue()
clientToServerQueue = queue.Queue()

# ser
serverSenderQueue = queue.Queue()
serverReaderQueue = queue.Queue()

tip = "yayinci"
server_dict = readFromDictionaryFile(logQueue, tip, "_peer_dictionary.txt")
pubkey_dict = readFromDictionaryFile(logQueue, tip, "_pubkey_dict.txt")
follow_list = readFromDictionaryFile(logQueue, tip, "_follow_list.txt")
mikro_blog = readFromDictionaryFile(logQueue, tip, "_mikroblog_dic.txt")
follower_list = readFromDictionaryFile(logQueue, tip, "_follower_list.txt")
block_list = readFromDictionaryFile(logQueue, tip, "_block_list.txt")
pm_dict = readFromDictionaryFile(logQueue, tip, "_ozel_mesaj.txt")
feeds = readFromDictionaryFile(logQueue, tip, "_all_feeds.txt")

# MAC adresiyle UUID
my_uuid = str(uuid.getnode())
print(my_uuid)

# Public ve private keyler
# Burada her şekilde yeni key oluşturuluyor ancak eğer daha önceden oluşmuş key var ise
# Write_Read_RSAKeys fonskiyonu tarafından okunup rsa_key dict ine yazılıyor.
rsa_keys = Write_Read_RSAKeys(logQueue, my_uuid)
private_key = rsa_keys[ 'privKey' ]
public_key = rsa_keys[ 'pubKey' ]
#print(private_key.exportKey("PEM").decode())
#print(public_key.exportKey("PEM").decode())
#  Bir peer icin hem client hem de server var.

#  Peer'in client tarafi tanimlaniyor.
class clientThread(
    threading.Thread):  # Bu client yayinci için çalıştığında kendi listsinde olan herkesten gidip liste ister
    def __init__(self, server_dict, clientSenderQueue, clientReaderQueue, logq, ip, port, c_uuid):
        threading.Thread.__init__(self)
        self.clientReaderQueue = clientReaderQueue
        self.clientSenderQueue = clientSenderQueue
        self.server_dict = server_dict
        self.logq = logq
        self.ip = ip
        self.port = port
        self.c_uuid = c_uuid

    def run(self):
        log = "Yayinci client çalışmaya başladı.\n"
        self.logq.put(log)
        print(log)

        # clientReader ve clientSender'ı isimlendirmek icin
        counter = 0
        while True:
            if (clientSenderQueue.empty() == False):
                data_dict = clientSenderQueue.get()
                client_sender_thread = clientSender("Client Sender - " + str(counter), self.logq, data_dict, counter)
                client_sender_thread.start()
                counter += 1
                print("Yayıncı sender çalıştı")

#class OzelMesajThread(threading.Thread):


class clientDictThread(threading.Thread):
    def __init__(self, server_dict, logq, ip, port, c_uuid):
        threading.Thread.__init__(self)
        self.server_dict = server_dict
        self.logq = logq
        self.ip = ip
        self.port = port
        self.c_uuid = c_uuid

    def run(self):
        log = "Yayıncı Client Dict kontrolu basladi\n"
        self.logq.put(log)
        print(log)

        while True:
            list_control(self.server_dict, self.logq, self.ip, self.port, self.c_uuid)
            server_dict = readFromDictionaryFile(logQueue, tip, "_peer_dictionary.txt")
            self.server_dict = server_dict
            time.sleep(60)


def list_control(peer_dict, logq, my_ip, my_port,
                 my_uuid, ):  # bu kod içerisinde time sleep olduğu için bunu çağıracak thread in başka işi olduğunda bekleme yapıyor
    # peer_dict'te kayitli her kullanici ile iletisim baslatma
    for key in peer_dict:
        # Kullaniciya ait bilgiler ayristiriliyor
        ip, port, type, nick, last_login = split_HELO_parametres(peer_dict[key])
        # Kullaniciyla baglanti baslatiliyor
        try:
            log = "Yayıncıdan IP: " + str(ip) + " Port: " + str(port) + " ile bağlantı kuruldu.\n"
            logq.put(log)

            msg = "HELO " + str(my_uuid) + " " + str(my_ip) + " " + str(my_port) + " " + str(tip) + " " + str(
                tip + "" + str(
                    my_uuid))  # Burada yayıncı kendi ipsini ve server taradinin portunu yolluyor. Nick de aracida onemli olmadigi icin bos.
            sender_dict = {
                'server_flag': "0",
                'ip': ip,
                'port': port,
                'cmd': msg,
                'cuuid': key,
                'last_login': last_login
            }
            clientSenderQueue.put(sender_dict)
        except Exception as e:
            logq.put(e)
            print(e)
            continue


# Client için sender thread
class clientSender(threading.Thread):
    def __init__(self, name, logq, data_dict, counter):
        threading.Thread.__init__(self)
        self.name = name
        self.logq = logq
        self.data_dict = data_dict
        self.counter = counter

    def run(self):
        log = tip + " " + self.name + "thread çalışmaya başladı.\n"
        self.logq.put(log)
        try:  # senderqueue dan gelen soket kontrolü
            data = self.data_dict
            print("ClientSenderCalisti - " + str(data))
            log = "Yayıncı Client SenderQue gelen data : " + str(data) + "\n"
            self.logq.put(log)

            skt = socket.socket()
            ip = data['ip']
            port = int(data['port'])
            skt.connect((ip, port))
            skt.send((data['cmd'] + "\n").encode())
            command = {
                'skt': skt,
                'ip':ip
            }
            if (data['server_flag'] == "1"):
                command['server_soket'] = data['soket']
                command['data_dict'] = data['data_dict']

            command['server_flag'] = data['server_flag']
            clientReaderQueue.put(command)
            client_reader = clientReader("Client Reader - " + str(self.counter), self.logq)
            client_reader.start()

        except Exception as e:
            log = "client sender - " + str(self.counter) + " hata - " + str(e)
            self.logq.put(log)
            print(log)


class clientReader(threading.Thread):
    def __init__(self, name, logq):
        threading.Thread.__init__(self)
        self.name = name
        self.logq = logq

    def run(self):
        log = tip + " " + self.name + " thread çalışmaya başladı.\n"
        self.logq.put(log)
        print(log)

        csCounter = 0
        while not clientReaderQueue.empty():
            data_queue = clientReaderQueue.get()
            skt = data_queue['skt']
            msg = skt.recv(1024).decode()
            print(msg)
            data = parser(msg, tip)
            if (data_queue['server_flag'] == "1"):
                data['server_soket'] = data_queue['server_soket']
                data['data_dict'] = data_queue['data_dict']
            print(data)
            if (data[ 'cmd' ] == "AUID" or data[ 'cmd' ] == "WAIT" or data[ 'cmd' ] == "WLCM" or data[
                'cmd' ] == "LSTO" or data['cmd'] == "PUBO"):
                if (data[ 'cmd' ] == "AUID"):
                    clientToServerQueue.put(data)
                    client_toserver = clientToServer("Client to Server - " + str(csCounter), self.logq)
                    client_toserver.start()
                    csCounter += 1
                if (data[ 'cmd' ] == "WAIT"):
                    log = "Waiting for HELO connection."
                    self.logq.put(log)
                    print(log)
                    msg = skt.recv(1024).decode()
                    data = parser(msg, tip)
                if (data[ 'cmd' ] == "WLCM"):
                    log = "WLCM received"
                    self.logq.put(log)
                    print(log)
                    skt.send(("LIST\r\n").encode())
                    msg = skt.recv(1024).decode()
                    data = parser(msg, tip)
                if (data[ 'cmd' ] == "LSTO"):
                    list = eval(data[ "list" ])  # Parametre olarak gelen dict alınıyor
                    mergeTwoDict(server_dict, list)  # server_dict'e gelen dict ekleniyor
                    log = "Gelen peer listesi asıl listeye eklendi"
                    self.logq.put(log)
                    appendToDictionaryFile(server_dict, self.logq, tip, "_peer_dictionary.txt")
                    print("Peerdan alınan liste sözlüğe eklendi\n")
                    skt.send(("PUBR "+str(public_key.exportKey("PEM").decode()) +"\r\n").encode())
                    log = "PUBR mesajı gönderildi."
                    self.logq.put(log)
                    msg = skt.recv(1024).decode()
                    data = parser(msg, tip)
                if(data['cmd'] == "PUBO"):
                    cuuid = iptouid(data_queue['ip'], server_dict)
                    pubkey_dict[ cuuid ]={
                            'pubKey' : data[ 'spubkey' ]
                    }

                    appendToDictionaryFile(pubkey_dict, self.logq, tip, "_pubkey_dict.txt")
                    log = str(cuuid) + " public Key eklendi."
                    self.logq.put(log)
                    print(log)
                    skt.send(str("PUBC " + str(my_uuid) + " " + str(sign_message(str(my_uuid), private_key))).encode())
                    log = "PUBC mesajı gönderildi."
                    self.logq.put(log)
                    msg = skt.recv(1024).decode()
                    data = parser(msg, tip)
                    if(data['cmd'] == "PUBV"):
                        pubkey_dict[cuuid]['verified'] = "True"
                    if (data['cmd'] == "PUBD"):
                        pubkey_dict[cuuid]['verified'] = "False"
                    appendToDictionaryFile(pubkey_dict, self.logq, tip, "_pubkey_dict.txt")
            else:
                inc_parser_client(data, data_queue['ip'],tip, logQueue, server_dict, clientReaderQueue,
                                  clientSenderQueue, private_key, feeds, follow_list, pubkey_dict)
            #

# Server için thread
class serverThread(threading.Thread):
    def __init__(self, name, logq, peer_dict, my_uuid, pub_key):
        threading.Thread.__init__(self)
        self.pub_key = pub_key
        self.logq = logq
        self.my_uuid = my_uuid
        self.peer_dict = peer_dict  # uuid ve baglanti adreslerinin oldugu dictionary
        self.name = name

    def run(self):
        log = tip + " " + self.name + " çalışmaya başladı.\n"
        self.logq.put(log)

        while not serverReaderQueue.empty():
            c, addr = serverReaderQueue.get()
            logQueue.put('Got connection from ' + str(addr))
            print(addr[0])
            print("Soket Server\n")

            while True:

                try:
                    print("Recv Server\n")
                    rps = c.recv(1024).decode()
                    data_rcv = inc_parser_server(rps, self.my_uuid, tip, self.logq, self.peer_dict,
                                                clientSenderQueue, clientReaderQueue, c, addr, private_key, self.pub_key,
                                                 pm_dict, mikro_blog, block_list, follow_list, follower_list, feeds)
                    data = parser(data_rcv, tip)
                    data_rcv += "\n"
                    print(rps)
                    if(data['status'] == "OK"):
                        c.send(data_rcv.encode())
                    else:
                        c.send(data_rcv.encode())
                        c.close()
                        break
                except Exception as e:
                    log = self.name + " got Exception -- " + str(e)
                    self.logq.put(log)
                    print(log)
                    break #hatalı durumlarda protokol.py içerisinde close
        log = tip + " " + self.name + " kapandi\n"
        self.logq.put(log)

class clientToServer(threading.Thread):
    def __init__(self, name, logq):
        threading.Thread.__init__(self)
        self.name = name
        self.logq = logq

    def run(self):
        log = tip + " " + self.name + " thread çalışmaya başladı.\n"
        self.logq.put(log)
        print(log)

        while True:

            while not clientToServerQueue.empty():
                reader_data = clientToServerQueue.get()  ##devamı gelecek.
                print("reader data\n" + str(reader_data))
                c = reader_data['server_soket']
                data_dict = reader_data['data_dict']
                if ((reader_data['cmd'] == "AUID") and (reader_data['uuid'] == data_dict[
                    'cuuid'])):  # client reader queue dict yazılmış gibi değerlendirildi.
                    c_dict = {
                        "cip": data_dict['cip'],
                        "cport": data_dict['cport'],
                        "ctype": data_dict["ctype"],
                        "cnick": data_dict["cnick"],
                        "last_login":time.time()

                    # time değeri float cinsinde atılıyor. Bu değeri datetime cinsine dönüştürmek için datetime.datetime.fromtimestamp(x) fonksiyonu verilmeli ve x yerine float değer yazılmalı
                        # pubkey eklenecek
                    }
                    server_dict[data_dict['cuuid']] = c_dict
                    appendToDictionaryFile(server_dict, self.logq, "yayinci", "_peer_dictionary.txt")
                    data = data_dict['resp2'] + " " + data_dict['cuuid']
                    c.send(data.encode())
                else:
                    log = "AUID WAIT eşleşmesi yapılamadı\n"
                    self.logq.put(log)
                    print(log)
                    c.close()
                    break


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
    #out_parser_client("BANN", "57407536053104", tip, logQueue, server_dict, clientSenderQueue,
                      #pubkey_dict, block_list, follow_list)
    # server name icin
    serverCounter = 0
    while True:
        serverReaderQueue.put(s1.accept())
        server_thread = serverThread("Server Thread - " + str(serverCounter), logQueue, server_dict, my_uuid, public_key)
        server_thread.start()
        serverCounter += 1



if __name__ == '__main__':
    main()

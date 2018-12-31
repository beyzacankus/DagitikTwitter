import threading
import queue
import socket
import time
import uuid

from loggerThread import loggerThread
from util_functions import *
from protokol import *

#Kuyruklar
logQueue = queue.Queue()
clientSenderQueue = queue.Queue()
clientReaderQueue = queue.Queue()
clientToServerQueue = queue.Queue()

#ser
serverSenderQueue = queue.Queue()
serverReaderQueue = queue.Queue()

tip = "araci"

server_dict = readFromDictionaryFile(logQueue, "araci", "_peer_dictionary.txt")
#  Bir peer icin hem client hem de server var.

#  Peer'in client tarafi tanimlaniyor.
class clientThread(threading.Thread): #Bu client aracı için çalıştığında kendi listsinde olan herkesten gidip liste ister
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
        log = "Aracı client çalışmaya başladı.\n"
        self.logq.put(log)

        while True:
            while not clientSenderQueue.empty():
                data_dict = clientSenderQueue.get()
                client_sender_thread = clientSender(self.logq, data_dict)
                client_sender_thread.start()

def list_control(peer_dict, logq, my_ip, my_port, my_uuid,): #bu kod içerisinde time sleep olduğu için bunu çağıracak thread in başka işi olduğunda bekleme yapıyor
    # peer_dict'te kayitli her kullanici ile iletisim baslatma
    for key in peer_dict:
        # Kullaniciya ait bilgiler ayristiriliyor
        ip, port, type, nick, last_login = split_HELO_parametres(peer_dict[ key ])
        # Kullaniciyla baglanti baslatiliyor
        try:
            log = "Aracıdan IP: " + str(ip) + " Port: " + str(port) + " ile bağlantı kuruldu.\n"
            logq.put(log)

            msg = "HELO " + str(my_uuid) + " " + str(my_ip) + " " + str(my_port) + " " + "A" + " " + "Araci_Nick"  # Burada araci kendi ipsini ve server taradinin portunu yolluyor. Nick de aracida onemli olmadigi icin bos.
            sender_dict = {
                'ip': ip,
                'port': port,
                'cmd': msg,
                'cuuid': key
            }
            clientSenderQueue.put(sender_dict)
        except:
            continue
        time.sleep(60)

# Client için sender thread
class clientSender(threading.Thread):
    def __init__(self, logq, data_dict):
        threading.Thread.__init__(self)
        self.logq = logq
        self.data_dict = data_dict

    def run(self):
        log = "Aracı Client Sender Thread çalışmaya başladı.\n"
        self.logq.put(log)
        try: #senderqueue dan gelen soket kontrolü
            data = self.data_dict
            print("ClientSenderCalisti - " + str(data))
            log = "Aracı Client SenderQue gelen data : " + str(data) + "\n"
            self.logq.put(log)

            skt = socket.socket()
            ip = data['ip']
            port = int(data['port'])
            skt.connect((ip, port))
            skt.send((data['cmd'] + "\n").encode())
            command = {
                'skt':skt,
                'server_soket':data['soket'],
                'data_dict': data['data_dict']
            }
            clientReaderQueue.put(command)
            client_reader = clientReader(self.logq)
            client_reader.start()
        except:
            print("client sender hata")



class clientReader(threading.Thread):
    def __init__(self, logq):
        threading.Thread.__init__(self)
        self.logq = logq

    def run(self):
        log = "Aracı Client Reader Thread çalışmaya başladı.\n"
        self.logq.put(log)
        print(log)

        while not clientReaderQueue.empty():
            data_queue = clientReaderQueue.get()
            skt = data_queue['skt']
            msg = skt.recv(1024).decode()
            print(msg)
            data = parser(msg, "A")
            data['server_soket'] = data_queue['server_soket']
            data['data_dict'] = data_queue['data_dict']
            print(data)

            if(data['cmd'] == "AUID"):
                clientToServerQueue.put(data)
                client_toserver = clientToServer(self.logq)
                client_toserver.start()
            else:
                print("farklı protokol")
                #inc_parser_client(data, tip, server_dict, )


            #inc_parser_client(msg, "A", clientReaderQueue)

# Server için thread
class serverThread(threading.Thread):
    def __init__(self, logq, peer_dict, my_uuid, pub_key):
        threading.Thread.__init__(self)
        self.pub_key = pub_key
        self.logq = logq
        self.my_uuid = my_uuid
        self.peer_dict = peer_dict # uuid ve baglanti adreslerinin oldugu dictionary

    def run(self):
        log = "Aracı Server Thread çalışmaya başladı.\n"
        self.logq.put(log)

        while not serverReaderQueue.empty():
            soket =  serverReaderQueue.get()
            c = soket['c']
            addr = soket['addr']
            print("Soket Server\n")

            # Kullanıcı kayıt olup olmadığı flag ile tutuluyor
            flag = 1
            c_uuid = ""
            while True:
                print("Recv Server\n")
                try:
                    rps = c.recv(1024).decode()
                    data_dict = parser(rps, "araci")
                    data_rcv = inc_parser_server(rps, self.my_uuid, "araci", self.logq, self.peer_dict,
                                             flag, clientSenderQueue, clientReaderQueue, self.pub_key ,c)
                    data = parser(data_rcv, "araci")
                    print(data)
                    if(data_rcv):

                        c.send(data_rcv.encode())
                except OSError:
                    log = "Soket hatası\n"
                    self.logq.put(log)
                    print(log)
                    break

                """
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
                        appendToDictionaryFile(data, self.logq, "araci", "araci_peer_dictionary.txt")
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
                """
class clientToServer(threading.Thread):
    def __init__(self, logq):
        threading.Thread.__init__(self)
        self.logq = logq

    def run(self):
        log = "Aracı Client To Server Thread çalışmaya başladı.\n"
        self.logq.put(log)
        print(log)

        while True:

            while not clientToServerQueue.empty():
                reader_data = clientToServerQueue.get()  ##devamı gelecek.
                print("reader data\n" + str(reader_data))
                c = reader_data[ 'server_soket' ]
                data_dict = reader_data[ 'data_dict' ]
                if ((reader_data[ 'cmd' ] == "AUID") and (reader_data[ 'uuid' ] == data_dict[
                    'cuuid' ])):  # client reader queue dict yazılmış gibi değerlendirildi.
                    c_dict = {
                        "cip": data_dict['cip'],
                        "cport": data_dict['cport' ],
                        "ctype": data_dict[ "ctype" ],
                        "cnick": data_dict[ "cnick" ],
                        #timestamp eklenecek!!!
                        #pubkey
                    }
                    server_dict[data_dict['cuuid']] = c_dict
                    appendToDictionaryFile(server_dict, self.logq, "araci", "_peer_dictionary.txt")
                    data = data_dict[ 'resp2' ] + " " + data_dict[ 'cuuid' ]
                    c.send(data.encode())
                    flag = 1
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
    port = int(sys.argv[2])
    s1.bind((host, port))
    s1.listen(5)
    
    # Kendi ip ve port bilgilerini client alıyor, bunları karşı tarafa atıcak
    ip = str(sys.argv[1])
    #print("Main IP", str(ip))
    port = int(sys.argv[2])

    # Kullanıcı kayıtlarının tutulacağı dictionary
    # write_dictionary ile text dosyası çağırılıp önceki kayıtlar dictionary içerisine yazılıyor



    # MAC adresiyle UUID
    my_uuid = str(uuid.getnode())
    print(my_uuid)

    # Public ve private keyler
    # Burada her şekilde yeni key oluşturuluyor ancak eğer daha önceden oluşmuş key var ise
    # Write_Read_RSAKeys fonskiyonu tarafından okunup rsa_key dict ine yazılıyor.
    keys = create_rsa_key(my_uuid)
    private_key = my_uuid + "_private_key"
    public_key = my_uuid + "_public_key"
    private_key = keys[private_key].exportKey().decode()
    public_key = keys[public_key].exportKey().decode()

    rsa_keys = Write_Read_RSAKeys(public_key, private_key, logQueue)
    private_key = rsa_keys['privKey']
    public_key = rsa_keys['pubKey']

    #list_control(server_dict, logQueue, ip, port, my_uuid)
    # #tüm listenin kontrol edilmesini sağlayan fonksiyon
    # bu kod içerisinde time sleep olduğu için bunu çağıracak thread in başka işi olduğunda bekleme yapıyor

    #--------------------------------------RSA KEYS

    client_thread = clientThread(server_dict, clientSenderQueue, clientReaderQueue, logQueue, ip, port, my_uuid)
    client_thread.start()

    while True:
        c, addr = s1.accept()
        gelen_soket = {
            'c': c,
            'addr': addr
        }
        #print(addr[1])
        serverReaderQueue.put(gelen_soket)
        logQueue.put('Got connection from ' + str(addr))
        server_thread = serverThread(logQueue, server_dict, my_uuid, public_key)
        server_thread.start()







if __name__ == '__main__':
    main()

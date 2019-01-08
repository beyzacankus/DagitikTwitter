#!/usr/bin/env python
import sys
import threading
import queue
import socket
import time
import uuid
from loggerThread import loggerThread
from util_functions import *
from datetime import datetime

merhaba = "HELO"
hosgeldin = "WLCM"
bekle = "WAIT"
suid = "SUID"
auid = "AUID"
list = "LIST"
listo = "LSTO"
pubkeygeldi = "PUBR"
pubkeygitsin = "PUBO"
pubkeycontrol = "PUBC"
pubkeyonay = "PUBV"
pubkeydenied = "PUBD"
microblogistek = "MBLR"
microblogokey = "MBLO"
aboneol = "SUBS"
aboneoldun = "SUBO"
aboneliktencik = "UNSB"
aboneliktenciktin = "UNSO"
tweet = "TWTS"
tweetokey = "TWTO"
ban = "BANN"
uban = "UBAN"
ubanok = "UBAO"
omesaj = "PRIV"
mesajok = "PRIO"
parametre = "ERRP"
genelhata = "ERRG"
authhata = "AUTH"
engelhatası = "BLCK"


#types, parser fonksiyonunu çağıran aracı mı ? yayıncı mı ? bunu bilmemiz gerekiyor.
araci = "A"
yayinci = "Y"


def parser(data, type): #AUTH ve BLCK hataları ana kod içerisinde yazılacak
    delimiter = " "
    splitLine = data.split(delimiter)
    command = splitLine[0].strip()
    try:

        if(command == merhaba):
            rdict = {
                "status": "OK",
                "cmd": merhaba,
                "resp1": bekle,
                "resp2": hosgeldin,
                "cuuid": splitLine[1].strip(),
                "cip": splitLine[2].strip(),
                "cport": splitLine[3].strip(),
                "ctype": splitLine[4].strip(),
                "cnick": splitLine[5].strip(),
            }
        elif(command == hosgeldin):
            rdict = {
                'status': "OK",
                'cmd': hosgeldin,
                'resp': list
            }
        elif(command == bekle):
            rdict = {
                'status':"OK",
                'cmd':command,
            }
        elif(command == suid): #suid argüman almaz ancak auid dönüş yaparken uuid parametresi ile döner.
            rdict = {
                "status": "OK",
                "cmd": suid,
                "resp": auid
            }
        elif(command == auid): #suid argüman almaz ancak auid dönüş yaparken uuid parametresi ile döner.
            rdict = {
                "status": "OK",
                "cmd": auid,
                "uuid": splitLine[1].strip()
            }

        elif(command == list): #liste ve count dönüyoruz.
            rdict = {
                "status": "OK",
                "cmd": list,
                "resp": listo,
            }
        elif(command == listo):
            rdict = {
                "status": "OK",
                "cmd":listo,
                "list":data[5:]
            }

        elif(command == pubkeygeldi): #cpubkey ile gelen pubkey i alıyoruz. gönderim yaparken kendi pubkey imizi göndereceğiz.
            if(type == yayinci):
                rdict = {
                    "status" : "OK",
                    "cmd": pubkeygeldi,
                    "resp": pubkeygitsin,
                    "cpubkey": data[5:]
                }
            else:
                rdict = {
                    "status" : "NOK",
                    "cmd": pubkeygeldi
                }
        elif(command == pubkeygitsin): #cpubkey ile gelen pubkey i alıyoruz. gönderim yaparken kendi pubkey imizi göndereceğiz.
            if(type == yayinci):
                rdict = {
                    "status" : "OK",
                    "cmd": pubkeygitsin,
                    "spubkey": data[5:]
                }
            else:
                rdict = {
                    "status" : "NOK",
                    "cmd": pubkeygitsin
                }

        elif(command == pubkeycontrol): #signed ve text in doğruluğunu kontrol edip resp1 veya resp2 döneceğiz
            if(type == yayinci):
                rdict = {
                    "status" : "OK",
                    "cmd": pubkeycontrol,
                    "resp1": pubkeyonay,
                    "resp2": pubkeydenied,
                    "ctext": splitLine[1].strip(),
                    "csigned": splitLine[2].strip()
                }
            else:
                rdict = {
                    "status" : "NOK",
                    "cmd": pubkeycontrol
                }

        elif(command == microblogistek): #mikroblog onay mesajı ve count dönüyoruz.
            if(type == yayinci):
                rdict = {
                    "status" : "OK",
                    "cmd": microblogistek,
                    "resp": microblogokey,
                    "count": splitLine[1].strip()
                }
            else:
                rdict = {
                    "status": "NOK",
                    "cmd": microblogistek
                }
        elif(command == aboneol): #abone olma işlemleri
            if(type == yayinci):
                rdict = {
                    "status" : "OK",
                    "cmd": aboneol,
                    "resp": aboneoldun
                }
            else:
                rdict = {
                    "status": "NOK",
                    "cmd": aboneol
                }
        elif(command == aboneliktencik): #abonelikten cikma islemleri
            if(type == yayinci):
                rdict = {
                    "status" : "OK",
                    "cmd": aboneliktencik,
                    "resp": aboneliktenciktin
                }
            else:
                rdict = {
                    "status": "NOK",
                    "cmd": aboneliktencik
                }
        elif(command == tweet): #tweet gönderme
            if(type == yayinci):
                rdict = {
                    "status": "OK",
                    "cmd": tweet,
                    "resp": tweetokey,
                    "text": splitLine[1].strip()
                }
            else:
                rdict = {
                    "status": "NOK",
                    "cmd": tweet
                }
        elif(command == ban): #user ban
            if(type == yayinci):
                rdict = {
                    "status": "OK",
                    "cmd": ban,
                    "resp": " "
                }
            else:
                rdict = {
                    "status": "NOK",
                    "cmd": ban
                }
        elif(command == uban): #user unban
            if(type == yayinci):
                rdict = {
                    "status": "OK",
                    "cmd": uban,
                    "resp": ubanok
                }
            else:
                rdict = {
                    "status": "NOK",
                    "cmd": uban
                }
        elif(command == omesaj): #özel mesaj
            if(type == yayinci):
                rdict = {
                    "status": "OK",
                    "cmd": omesaj,
                    "resp": mesajok,
                    "mesaj": splitLine[1].strip()

                }
            else:
                rdict = {
                    "status": "NOK",
                    "cmd": omesaj
                }
        else: #genel hatayı burada tanımlıyoruz
            rdict = {
                "status": "NOK",
                "cmd": command,
                "resp": genelhata
            }
    except IndexError: #parametre hatası burada tanımlanıyor.
        rdict = {
            "status": "NOK",
            "cmd": command,
            "resp":parametre
        }

    return rdict

def inc_parser_server(data, suuid, type, logq, user_dict, flag, clientsenderqueue, clientreaderqueue, public_key, soket):

    data_dict = parser(data,type)
    data = ""
    if(data_dict['status'] == "OK"):
        if(data_dict['cmd'] == merhaba):
            if(data_dict['cuuid'] in user_dict):
                data = data_dict['resp2'] + " " + data_dict['cuuid']
                user_dict[data_dict['cuuid']]['cip'] = data_dict['cip']
                user_dict[data_dict['cuuid']]['cport'] = data_dict['cport']
                user_dict[data_dict['cuuid']]['last_login'] = time.time()
                appendToDictionaryFile(user_dict, logq, "araci", "_peer_dictionary.txt")
                #eğer uuid var ve ip-port farklı ise güncelle sonra welcome dön
                #gelen_port
                #gelen uuid
            else: #WAIT burada göndereliyor ancak ekleme yapmak için client threadinin SUID kontrolünün sonucunu beklemek gerekiyor.
                data = data_dict['resp1']
                command = {
                    'ip':data_dict['cip'],
                    'port':data_dict['cport'],
                    'cmd':"SUID",
                    'soket':soket,
                    'data_dict':data_dict
                }
                print(command)
                clientsenderqueue.put(command)
        elif(data_dict['cmd'] == hosgeldin):
            data = data_dict['resp']

        elif(data_dict['cmd'] == list):

            if flag == 1:
                return_dict = timestamptodate(user_dict)
                data = data_dict['resp'] + " " + str(return_dict)
            else:
                data = "AUTH"

        elif (data_dict['cmd'] == suid):

            data = data_dict['resp'] + " " + suuid

        elif(data_dict['cmd'] == pubkeygeldi):
            if flag == 1:
                r_pub_key = data_dict['cpubkey']

                data = data_dict['resp'] + " " + public_key

            else:
                data = "AUTH"
    else:
        soket.send(str(data_dict['resp']).encode())
        logq.put(data_dict)
        soket.close()
    return data

def out_parser_client(data, type, my_pub_key, clientSenderQueue, clientReaderQueue):

    return 1

def inc_parser_client(data, type, server_dict, pubkey_dict, clientReaderQueue, clientSenderQueue, logq):

    if (data['status'] == "OK"):
        if (data['cmd'] == listo):
            list = data["list"]     # Parametre olarak gelen dict alınıyor
            mergeTwoDict(server_dict, list)     # server_dict'e gelen dict ekleniyor
            log = "Gelen peer listesi asıl listeye eklendi"
            logq.put(log)
            appendToDictionaryFile(server_dict, logq, type, "_peer_dict")
            print("Peerdan alınan liste sözlüğe eklendi\n")

        elif(data['cmd'] == pubkeygeldi):
            #gelen pub_key i alacak server_dict te ekleyecek fonksiyon
            cuuid = data['data_dict']['cuuid']
            pubkey_dict[cuuid] = data['spubkey']
            appendToDictionaryFile(pubkey_dict, logq, type, "_pubkey_dict.txt")

        elif (data['cmd'] == microblogokey):
            pass
        elif (data['cmd'] == aboneoldun):
            pass
        elif (data['cmd'] == aboneliktenciktin):
            pass
        elif (data['cmd'] == tweetokey):
            pass
        elif (data['cmd'] == ubanok):
            pass
        elif (data['cmd'] == mesajok):
            pass
        elif (data['cmd'] == authhata):
            pass
        elif (data['cmd'] == engelhatası):
            pass

    return 1







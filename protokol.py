#!/usr/bin/env python
import sys
from loggerThread import loggerThread
from util_functions import *

merhaba = "HELO"
hosgeldin = "WLCM"
bekle = "WAIT"
suid = "SUID"
auid = "AUID"
list = "LIST"
listo = "LISTO"
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
                "cnick": splitLine[5].strip()
            }
        elif(command == suid): #suid argüman almaz ancak auid dönüş yaparken uuid parametresi ile döner.
            rdict = {
                "status": "OK",
                "cmd": suid,
                "resp": auid,
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
                "count": splitLine[1].strip()
            }

        elif(command == pubkeygeldi): #cpubkey ile gelen pubkey i alıyoruz. gönderim yaparken kendi pubkey imizi göndereceğiz.
            if(type == yayinci):
                rdict = {
                    "status" : "OK",
                    "cmd": pubkeygeldi,
                    "resp": pubkeygitsin,
                    "cpubkey": splitLine[1].strip()
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
                    "spubkey": splitLine[1].strip()
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

def inc_parser_server(data, suuid, type, logq, user_dict, flag, clientsenderqueue, clientreaderqueue, public_key, r_pub_key, micro_blog):

    data_dict = parser(data,type)

    if(data_dict['status'] == "OK"):
        if(data_dict['cmd'] == merhaba):
            if(data_dict['cuuid'] in user_dict):
                data = data_dict['resp2'] + " " + data_dict['cuuid']
            else: #WAIT burada göndereliyor ancak ekleme yapmak için client threadinin SUID kontrolünün sonucunu beklemek gerekiyor.
                sender_dict = {
                    "cmd":"SUID",
                    "ip":data_dict['cip'],
                    "port":data_dict['cport']
                }
                clientsenderqueue.put(sender_dict)
                while not clientreaderqueue.empty():
                    reader_data = clientreaderqueue.get() ##devamı gelecek.
                    if(reader_data['uuid'] == data_dict['cuuid']):#client reader queue dict yazılmış gibi değerlendirildi.
                        c_dict = {
                            "cip": data_dict['cip'],
                            "cport": data_dict['cport'],
                            "ctype": data_dict["ctype"],
                            "cnick": data_dict["cnick"]
                        }
                        user_dict[data_dict['cuuid']] = c_dict
                        line = data_dict['cuuid'] + " -" + c_dict
                        appendToPeerDictionary(line, logq, "yayinci")
                        data = data_dict['resp1'] + " " + data_dict['cuuid']
                        flag = 1
                    else:
                        break
            data += "\nThank you for connecting!"

        elif(data_dict['cmd'] == list):

            if flag == 1:
                if(data_dict['count'] > 0): #sıfırdan büyük olması durumunda count kadar kayıt liste olarak döner
                    data = data_dict['resp'] + " " + str(take(data_dict['count'], user_dict.items()))
                else:
                    data = data_dict['resp'] + " " + str(user_dict)
            else:
                data = "AUTH"

        elif (data_dict['cmd'] == suid):

            data = data_dict['resp'] + " " + suuid

        elif(data_dict['cmd'] == pubkeygeldi): #gelen public key r_pub_key değişkenine atanıyor.
            if flag == 1:
                r_pub_key = data_dict['cpubkey']
                data = data_dict['resp'] + " " + public_key.exportKey("PEM").decode()
            else:
                data = "AUTH"
        elif(data_dict['cmd'] == pubkeycontrol): #buraya public key hatalı olması durumunda çalışacak fonksiyonu eklemeliyiz
            if flag == 1:
                if(check_signature(data_dict['ctext'], data_dict['csigned'], r_pub_key)):
                    data = data_dict['resp1']
                else:
                    data = data_dict['resp2']
            else:
                data = "AUTH"
        elif(data_dict['cmd'] == microblogistek):
            if flag == 1:
                if(data_dict['count'] > 0): #sıfırdan büyük olması durumunda count kadar kayıt liste olarak döner
                    data = data_dict['resp'] + " " + str(take(data_dict['count'], micro_blog.items()))
                else:
                    data = data_dict['resp'] + " " + str(micro_blog)
            else:
                data = "AUTH"
        elif(data_dict['cmd'] == aboneol):
            if flag == 1:
                #abone olmayı sağlayan fonksiyon buraya gelecek.
                #neye göre abone alacak bunu protokolde belirlemeyliyiz
                data = data_dict['resp']

            else:
                data = "AUTH"
        elif(data_dict['cmd'] == aboneliktencik):
            if flag == 1:
                #abonelikten çıkmayı sağlayan fonksiyon buraya gelecek.
                #neye göre abonelikten çıkacak bunu protkolde belirlemeliyiz.
                data = data_dict['resp']

            else:
                data = "AUTH"
        elif(data_dict['cmd'] == tweet):#herkese atılan tweetin server a gelmesi
            if flag == 1:
                #data_dict['text'] - tweet datası
                #gelen tweet ekrana mı basılacak nereye basılacak bunu yapan fonksiyon gerekiyor
                data = data_dict['resp']

            else:
                data = "AUTH"


    else:
        logq.put(data_dict)

    return data

def out_parser_client(data, type, clientSenderQueue, clientReaderQueue):
    data_dict = clientsenderqueue

    return 1
def inc_parser_client(data, type, clientSenderQueue, clientReaderQueue):

    data_dict = parser(data, type)
    if (data_dict['status'] == "OK"):
        if (data_dict['cmd'] == auid):
            clientreaderqueue.put(data_dict) # gelen uuid bizim dict içerisinde var mı ? varsa o ip ile gelen ip aynı mı ? bunun kontrolü.
        elif(data_dict['cmd'] == pubkeygitsin):
            clientreaderqueue.put(data_dict)

    return 1







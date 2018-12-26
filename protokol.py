#!/usr/bin/env python
import sys

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
                "resp": auid
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

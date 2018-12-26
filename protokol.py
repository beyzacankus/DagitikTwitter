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

#types, parser fonksiyonunu çağıran aracı mı ? yayıncı mı ? bunu bilmemiz gerekiyor.
araci = "araci"
yayinci = "yayinci"


def parser(data, type): #AUTH ve BLCK hataları ana kod içerisinde yazılacak
    delimiter = " "
    splitLine = data.split(delimiter)
    command = splitLine[0].strip()

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
        return rdict
    elif(command == suid): #suid argüman almaz ancak auid dönüş yaparken uuid parametresi ile döner.
        rdict = {
            "status": "OK",
            "cmd": suid,
            "resp": auid
        }

        return rdict
    elif(command == list):
        rdict = {
            "status": "OK",
            "cmd": list,
            "resp": listo,
            "count": splitLine[1].strip()
        }

        return rdict
    elif(command == pubkeygeldi):
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

        return rdict









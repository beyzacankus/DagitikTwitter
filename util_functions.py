from Crypto.PublicKey import RSA
from Crypto import Random
from Crypto.Hash import SHA256
from Crypto.Signature import PKCS1_v1_5
from base64 import b64encode, b64decode
import Crypto.Signature
import threading
import queue
import socket
import time
import uuid
from pathlib import Path
from itertools import islice
from datetime import datetime
import copy

def take(n, iterable):
    "Return first n items of the iterable as a list"
    return list(islice(iterable, n))

def create_rsa_key(uuid):
    random_generator = Random.new().read
    new_key = RSA.generate(2048, randfunc=random_generator)
    # print(random_generator)
    public_key = new_key.publickey()
    # print(public_key.exportKey())
    private_key = new_key
    # print(new_key.exportKey())

    return {str(uuid) + "_public_key": public_key, str(uuid)+ "_private_key": private_key}

def Write_Read_RSAKeys(logq, my_uuid): #RSA keylerini oluşturup dosyaya yazan eğer dosyada varsa okuyan fonksiyon
    pubKey_file = Path("./my_pubKey.txt")
    privKey_file = Path("./my_privKey.txt")

    if pubKey_file.is_file() and privKey_file.is_file():
        file = open(str(pubKey_file), "r+")
        fid_pub = file.read().encode()
        keys_dict = {
            "pubKey": RSA.importKey(fid_pub)
        }

        file = open(str(privKey_file), "r+")
        fid_priv = file.read().encode()
        keys_dict[ 'privKey' ] = RSA.importKey(fid_priv)

    else:

        keys = create_rsa_key(my_uuid)
        private_key = my_uuid + "_private_key"
        public_key = my_uuid + "_public_key"
        private_key = keys[private_key].exportKey()
        public_key = keys[public_key].exportKey()
        fid_pub = open(str(pubKey_file), "w")
        fid_pub.write(public_key.decode())
        keys_dict = {
            "pubKey": public_key
        }
        logq.put("PublicKey oluşturuldu, dosyaya yazıldı.")

        fid_priv = open(str(privKey_file), "w")
        fid_priv.write(private_key.decode())
        keys_dict[ 'privKey' ] = private_key

        logq.put("PrivateKey oluşturuldu, dosyaya yazıldı.")

    return keys_dict



def update_public_key_dictionary(uuid, public_key) :

    pass


def encrypte_message(message,receiver_public_key) :
    encrypted = receiver_public_key.encrypt(message.encode(), 64)
    return encrypted


def decrypte_message(encrypted_message,receiver_private_key) :
    decrypted = receiver_private_key.decrypt(encrypted_message)
    return decrypted.decode()


def sign_message(message, private_key):
    hash = SHA256.new()
    hash.update(message.encode())
    signer = PKCS1_v1_5.new(private_key)
    signature = signer.sign(hash)
    return b64encode(signature).decode()


def check_signature(message, signature, sender_public_key) :
    hash = SHA256.new()
    hash.update(message.encode())
    signer = PKCS1_v1_5.new(sender_public_key)
    return signer.verify(hash, b64decode(signature))



# Peer bilgileri ilgili dosyalardan okunuyor ve bir dictionary'e kaydediliyor.
# Araci ve yayinci için kullanilan dosya adlari karisikliklari onlemek icin farkli belirlenmistir.
""""
def writeToPeerDictionary(peer_dict, logq, type):
    if(type == "araci"):
        fid = open("araci_peer_dictionary.txt", "r+")
        log = "Aracı dosyadan kayıtları çekti.\n"
    else:
        fid = open("yayinci_peer_dictionary.txt", "r+")
        log = "Yayıncı dosyadan kayıtları çekti.\n"

    #uuid key'i ile geri kalan baglanti bilgilerini tutan peer_dict olusturur.
    for line in fid:
        listedline = line.strip().split('-')
        if len(listedline) > 1:
            peer_dict[listedline[0].strip()] = listedline[1].strip()

    logq.put(log)
    fid.close()
"""""

#tum dictionarylerden okumak icin read
def readFromDictionaryFile(logq, type, filename):
    try:
        filename = str(type) + filename
        fid = open(filename, "r+")
        log = type + "dosyadan kayıtları çekti.\n"  #hangi kayitlari cekti duzenle

        #uuid key'i ile geri kalan baglanti bilgilerini tutan peer_dict olusturur.

        dict = eval(fid.read())
        logq.put(log)
        fid.close()
    except:
        return {}
    return dict


# Tum dictionarylere yazmak icin genel bir append fonksiyonu
def appendToDictionaryFile(data_dict, logq, type, filename): #tüm dict tekrar dosyaya yazılır.
    filename = str(type) + filename
    fid = open(filename, "w")
    fid.write("%s\n" % data_dict)
    fid.flush()
    log = type + "tarafından yeni kayıt dosyaya yazıldı.\n"
    logq.put(log)
    fid.close()
    
# Yeni eklenen peer bilgileri ilgili dosyalara kaydediliyor.
# Araci ve yayinci için kullanilan dosya adlari karisikliklari onlemek icin farkli belirlenmistir.
#def appendToPeerDictionary(data, logq, type):
#    if (type == "araci"):
#        fid = open("araci_peer_dictionary.txt", "a+")
#        log = "Aracı tarafından yeni kayıt dosyaya yazıldı: UUID -> "+ data[:14] + "\n"
#    else:
#        fid = open("yayinci_peer_dictionary.txt", "a+")
#        log = "Yayıncı tarafından yeni kayıt dosyaya yazıldı: UUID -> "+ data[:14] + "\n"
#
#    fid.write("%s" % data)
#   fid.flush()
#   logq.put(log)
#  fid.close()

# HELO mesajıyla alinan input ip, port, type ve nick parametrelerine ayristiriliyor
def split_HELO_parametres(inp):

    ip = inp['cip']
    port = int(inp['cport'])
    type = inp['ctype']
    nick = inp['cnick']
    last_login = inp['last_login']

    return ip, port, type, nick, last_login


# sozlukleri birlestiren fonksiyon
def mergeTwoDict(ourDict, otherDict):
    # ilk for aynı keylerin timestamplerini karsilastirmak icin
    for ourKey in ourDict.keys():
        for otherKey in otherDict.keys():
            if ourKey == otherKey:
                if ourDict[ourKey]["last_login"] < otherDict[otherKey]["last_login"]: # timestamp'i time.time() olarak denedim float donduruyor
                    ourDict[ourKey] = otherDict[otherKey]
    # ikinci for bizde olmayan itemleri almak icin
    for otherKey in otherDict.keys():
        if not otherKey in ourDict.keys():
            ourDict[otherKey] = otherDict[otherKey]


def timestamptodate(user_dict):
    return_dict = copy.deepcopy(user_dict)
    #Python yapısı gereği variableA = variableB yaptığımız zaman uyguladığımız değişiklikleri diğer değişkenede uygulayan bir dil (bellek pointer yapısı gibi )
    #Bu nedenle copy modülü kullanılarak o değişkenin içeriği kopyalayıp değişiklerden etkilenmemesini sağlıyoruz.
    for key in user_dict:
        return_dict[key]['last_login'] = datetime.utcfromtimestamp(return_dict[key]['last_login']).strftime("%m/%d/%Y %H:%M:%S")

    return return_dict

def ispeer_valid(ip, user_dict):

    flag = 0
    for keys in user_dict:
        if user_dict[keys ][ 'cip' ] == str(ip):
            flag +=1

    if flag > 0:
        return True
    else:
        return False

def iptouid(ip, user_dict):

    for keys in user_dict:
        if user_dict[keys ][ 'cip' ] == str(ip):
            user_id = keys

    return user_id

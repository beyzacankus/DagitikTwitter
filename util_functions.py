from Crypto.PublicKey import RSA
from Crypto import Random
from Crypto.Hash import SHA256
import threading
import queue
import socket
import time
import uuid
from pathlib import Path
from itertools import islice

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

def Write_Read_RSAKeys(publicKey, privateKey,logq): #RSA keylerini dosyaya yazan eğer dosyada varsa okuyan fonksiyon
    pubKey_file = Path("./my_pubKey.txt")
    privKey_file = Path("./my_privKey.txt")

    if pubKey_file.is_file():
        fid_pub = open(pubKey_file, "r+")
        keys_dict = {
            "pubKey": fid_pub.read()
        }
    else:
        fid_pub = open(pubKey_file, "w")
        fid_pub.write(publicKey)
        keys_dict = {
            "pubKey": publicKey
        }
        logq.put("PublicKey oluşturuldu, dosyaya yazıldı.")
    if privKey_file.is_file():
        fid_priv = open(privKey_file, "r+")
        keys_dict['privKey'] = fid_priv.read()

    else:
        fid_priv = open(privKey_file, "w")
        fid_priv.write(privateKey)
        keys_dict['privKey'] = privateKey

        logq.put("PrivateKey oluşturuldu, dosyaya yazıldı.")

    return keys_dict



def update_public_key_dictionary(uuid, public_key) :

    pass


def encrypte_message(message,receiver_public_key) :
    encrypted = receiver_public_key.encrypt(message.encode(), 64)
    return encrypted


def decrypte_message(encrypted_message,receiver_private_key) :
    decrypted = receiver_private_key.decrypt(encrypted_message)
    return decrypted.encode()


def sign_message(message, private_key):
    hash = SHA256.new(message.encode()).digest()
    signature = private_key.sign(hash, '')
    return signature


def check_signature(message, signature, sender_public_key) :
    hash = SHA256.new(message.encode()).digest()
    return sender_public_key.verify(hash, signature)



# Peer bilgileri ilgili dosyalardan okunuyor ve bir dictionary'e kaydediliyor.
# Araci ve yayinci için kullanilan dosya adlari karisikliklari onlemek icin farkli belirlenmistir.
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
    #log = type + "tarafından yeni kayıt dosyaya yazıldı: UUID -> "+ data[:14] + "\n" # uuid 'yi alacak şekilde duzenlenmeli
    #logq.put(log)
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
    port = inp['cport']
    type = inp['ctype']
    nick = inp['cnick']

    return ip, port, type, nick
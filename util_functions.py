from Crypto.PublicKey import RSA
from Crypto import Random
from Crypto.Hash import SHA256
import threading
import queue
import socket
import time
import uuid

def create_rsa_key(uuid) :
    random_generator = Random.new().read
    new_key = RSA.generate(2048, randfunc=random_generator)
    # print(random_generator)
    public_key = new_key.publickey()
    # print(public_key.exportKey())
    private_key = new_key
    # print(new_key.exportKey())

    return {uuid + "_public_key": public_key, uuid+ "_private_key": private_key}


def update_public_key_dictionary(uuid, public_key) :
    pass


def encrypte_message(message,receiver_public_key) :
    encrypted = receiver_public_key.encrypt(message.encode(), 64)
    return encrypted


def decrypte_message(encrypted_message,receiver_private_key) :
    decrypted = receiver_private_key.decrypt(encrypted_message)
    return decrypted.encode()


def sign_message(message, private_key) :
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

    for line in fid:
        listedline = line.strip().split('-')
        if len(listedline) > 1:
            peer_dict[listedline[0].strip()] = listedline[1].strip()

    logq.put(log)
    fid.close()


# Yeni eklenen peer bilgileri ilgili dosyalara kaydediliyor.
# Araci ve yayinci için kullanilan dosya adlari karisikliklari onlemek icin farkli belirlenmistir.
def appendToPeerDictionary(data, logq, type):
    if (type == "araci"):
        fid = open("araci_peer_dictionary.txt", "a+")
        log = "Aracı tarafından yeni kayıt dosyaya yazıldı: UUID -> "+ data[:14] + "\n"
    else:
        fid = open("yayinci_peer_dictionary.txt", "a+")
        log = "Yayıncı tarafından yeni kayıt dosyaya yazıldı: UUID -> "+ data[:14] + "\n"

    fid.write("%s" % data)
    logq.put(log)
    fid.close()

# HELO mesajıyla alinan input ip, port, type ve nick parametrelerine ayristiriliyor
def split_HELO_parametres(inp):
    inp = str(inp)
    nick = ""
    ip = ""
    port = ""
    delimiter = " "
    list = inp.split(delimiter)
    ip = list[0]
    port = list[1]
    type = list[2]
    nick = list[3]

    return ip, port, type, nick
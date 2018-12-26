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



# peer_dictionary dosyasındaki kayitlar peer_dict'e yazılıyor. UUID key degeri, geri kalan bilgiler(ip,port,tip,nick) valuelar
def writeToPeerDictionary(peer_dict, logq):
    fid = open("dictionary.txt", "r+")
    for line in fid:
        listedline = line.strip().split('-')
        if len(listedline) > 1:
            peer_dict[listedline[0].strip()] = listedline[1].strip()

    log = "Aracı tarafından sözlük dosyasındaki kayıt sunucu sözlüğüne çekildi.\n"
    logq.put(log)

    fid.close()


# Yeni kaydi peer_dictionary dosyasina ekleme
def appendToPeerDictionary(data, logq):
    f = open("dictionary.txt", "a+")
    f.write("%s" % data)

    log = "Aracı tarafından yeni kayıt sözlük dosyasına yazıldı.\n"
    logq.put(log)

    f.close()
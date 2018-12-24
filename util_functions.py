from Crypto.PublicKey import RSA

from Crypto import Random

from Crypto.Hash import SHA256

def create_rsa_key(uuid) :

    random_generator = Random.new().read

    new_key = RSA.generate(2048, randfunc=random_generator)

    print(random_generator)

    public_key = new_key.publickey()

    print(public_key.exportKey())

    private_key = new_key

    print(new_key.exportKey())


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

import hashlib
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
import os


researchlab_pwd = os.getenv('researchlab_pwd')


def sha256_encode(data):
    hash_object = hashlib.sha256()
    hash_object.update(data.encode('utf-8'))
    hex_dig = hash_object.hexdigest()
    return hex_dig


def hash_key(key_str):
    hash_object = hashlib.sha256()
    hash_object.update(key_str.encode())
    return hash_object.digest()[:32]


def encrypt(plain_text, key_str):
    key = hash_key(key_str)
    backend = default_backend()
    iv = os.urandom(16)
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=backend)
    encryptor = cipher.encryptor()
    padder = padding.PKCS7(algorithms.AES.block_size).padder()
    padded_data = padder.update(plain_text.encode()) + padder.finalize()
    encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
    return (iv + encrypted_data).hex()


def decrypt(cipher_text_hex, key_str=researchlab_pwd):
    key = hash_key(key_str)
    backend = default_backend()
    cipher_text = bytes.fromhex(cipher_text_hex)
    iv = cipher_text[:16]
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=backend)
    decryptor = cipher.decryptor()
    decrypted_padded_data = decryptor.update(cipher_text[16:]) + decryptor.finalize()
    unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
    original_data = unpadder.update(decrypted_padded_data) + unpadder.finalize()
    return original_data.decode()


if __name__ == '__main__':
    # cipher_text = encrypt('hcc-rag', 'S2LI(#@slF')
    # print(cipher_text)
    # plain_text = decrypt(cipher_text, 'collection')
    # print(plain_text)

    hash_value = sha256_encode("45355$%Dff")
    print(hash_value)

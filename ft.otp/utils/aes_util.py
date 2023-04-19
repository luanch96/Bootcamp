from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Util.Padding import pad, unpad

import base64
import os

MODE = AES.MODE_CBC
SALT = "RANDOM_SALT".encode("utf-8")  # Valor aleatorio para el SALT


def generate_master_key_for_AES_cipher():
    AES_key_length = 16
    master_key = os.urandom(AES_key_length)
    encoded_master_key = base64.b64encode(master_key)
    return encoded_master_key


def encrypt_message(private_msg: str, encoded_master_key: bytes) -> bytes:
    master_key = base64.b64decode(encoded_master_key).decode("utf-8")
    key = PBKDF2(
        master_key, SALT, dkLen=16
    )  # Derivar la clave de texto a una clave de 16 bytes
    iv = b"\x00" * AES.block_size
    cipher = AES.new(key, MODE, iv)
    padded_message = pad(private_msg.encode("utf-8"), AES.block_size)
    encrypted_msg = cipher.encrypt(padded_message)
    encoded_encrypted_msg = base64.b64encode(encrypted_msg)
    return encoded_encrypted_msg


def decrypt_message(encoded_encrypted_msg: bytes, encoded_master_key: bytes) -> str:
    master_key = base64.b64decode(encoded_master_key).decode("utf-8")
    encrypted_msg = base64.b64decode(encoded_encrypted_msg)
    key = PBKDF2(
        master_key, SALT, dkLen=16
    )  # Derivar la clave de texto a una clave de 16 bytes
    iv = b"\x00" * AES.block_size
    cipher = AES.new(key, MODE, iv)
    decrypted_msg = cipher.decrypt(encrypted_msg)
    plaintext = unpad(decrypted_msg, AES.block_size).decode("utf-8")
    return plaintext

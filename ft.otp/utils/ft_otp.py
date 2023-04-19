from utils.aes_util import (
    encrypt_message,
    decrypt_message,
    generate_master_key_for_AES_cipher,
)
import argparse
import time
import hmac
import base64

from typing import Union

FT_OTP_KEY = "keys/ft_otp.key"
FT_MASTER_PASSWORD = "keys/master_password.key"
MIN_LENGTH = 64


def get_totp_key(file_path: str, master_password: Union[bytes, None] = None) -> str:
    cyphered_secret = read_file(file_path)
    temp_master_key = load_master_password()
    if master_password is not None:
        temp_master_key = master_password
    secret = decrypt_message(cyphered_secret, temp_master_key)
    secret = hex_to_text(base64.b32decode(secret).decode("utf-8")).encode("utf-8")
    calculated_timestep = timestep(30)
    totp_token = str(gen_totp_token(secret, calculated_timestep))
    print("Got key at {}: {}".format(calculated_timestep, totp_token))
    return totp_token


def gen_totp_token(secret, timestamp) -> str:
    msg = timestamp.to_bytes(8, "big")
    digest = hmac.new(secret, msg, "sha1").digest()
    offset = digest[19] & 0xF
    code = int.from_bytes(digest[offset : offset + 4], "big") & 0x7FFFFFFF
    return str(code % 1000000).zfill(6)


def timestep(timestep: int) -> int:
    return int(time.time()) // timestep


def read_file(file_path: str) -> bytes:
    with open(file_path, "r") as reader:
        lines = ""
        for line in reader:
            lines += line

        hex_lines = lines.strip().encode("utf-8")
        return hex_lines


def text_to_hex(text: str) -> str:
    return text.encode("utf-8").hex()


def hex_to_text(hex: str) -> str:
    return bytearray.fromhex(hex).decode()


def save_seed(plain_text):
    b32_text = base64.b32encode(plain_text).decode("utf-8")
    cyphered_text = encrypt_message(b32_text, load_master_password())
    with open(FT_OTP_KEY, "wb") as writer:
        writer.write(cyphered_text)
        print("Key was successfuly saved in {}".format(FT_OTP_KEY))


def check_key(key):
    if len(key) < MIN_LENGTH:
        raise Exception(
            "error: key must be {} hexadecimal characters. {}".format(
                MIN_LENGTH, len(key)
            )
        )


def load_master_password() -> bytes:
    # MASTER KEY BASE64:
    # TVkgU0VDUkVUIFBBU1NXT1JEIDEyMzQ1Njc4OTAyMzQyMzQyMzQyMzQyMzQyMzQyMzIzNDIzMTQxMjM0
    return base64.b64encode(read_master_password().encode("utf-8"))


def read_master_password() -> str:
    with open(FT_MASTER_PASSWORD, "r") as reader:
        return reader.readlines()[0]


def update_master_password(new_master_password: str):
    old_password = load_master_password()
    cyphered_secret = read_file(FT_OTP_KEY)
    secret = decrypt_message(cyphered_secret, old_password)

    b64_new_master_password_encoded = base64.b64encode(
        new_master_password.encode("utf-8")
    )
    cyphered_text = encrypt_message(secret, b64_new_master_password_encoded)

    new_secret = decrypt_message(cyphered_text, b64_new_master_password_encoded)
    if secret == new_secret:
        # password cambiada
        with open(FT_MASTER_PASSWORD, "w") as writer:
            writer.write(new_master_password)
        save_seed(base64.b32decode(new_secret))

    return secret == new_secret


def get_random_master_key():
    non_valid_chars = ["+", "/"]
    new_key = generate_master_key_for_AES_cipher().decode("utf-8")
    for char in non_valid_chars:
        new_key = new_key.replace(char, "=")

    return new_key


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="ft_otp", description="otp key generator")

    try:
        parser.add_argument("-g", "--hex", help="64 bits chars hexadecimal key")
        parser.add_argument("-t", "--text", help="Plain text")
        parser.add_argument("-k", "--key", help="Generates a totp key")

        args = parser.parse_args()
        if args.hex is not None:
            hex_text = read_file(args.hex)
            check_key(hex_text)
            save_seed(hex_text)

        elif args.text is not None:
            plain_text = read_file(args.text).decode("utf-8")
            hex_text = text_to_hex(plain_text)
            save_seed(hex_text.encode("utf-8"))

        elif args.key is not None:
            get_totp_key(args.key)

        else:
            get_totp_key(FT_OTP_KEY)
            parser.print_help()

    except Exception as e:
        print(e)

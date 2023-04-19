from utils.aes_util import encrypt_message, decrypt_message
import base64
import pytest

encoded_secret_key = base64.b64encode(
    "MY SECRET PASSWORD 12345678902342342342342342342323423141234".encode("utf-8")
)


@pytest.mark.parametrize(
    "plain_text, expected",
    [
        (
            "hello my name is iker",
            b"yZUZpPwjBuwxCPm44DhImHTuZr0O4ekT8sWq0ZkIJCjT9g/QrR/yKrUwRrDaQNRs",
        ),
        (
            "hello my name is 0x10",
            b"yZUZpPwjBuwxCPm44DhImMMNWjGoLis28dMxCk5x0FgzbF0gYqDA1dz3tfWFIcAK",
        ),
        (
            "hello my name is Harry Potter",
            b"yZUZpPwjBuwxCPm44DhImExHAqJb6o9NIvOVGZVHV3H3P39ZrLhIwk/XHNF+fi3gOI4Wavg0OJ+rIS0CliLtIQ==",
        ),
    ],
)
def test_cypher(plain_text, expected):
    b32_text = base64.b32encode(plain_text.encode("utf-8")).decode("utf-8")
    cyphered_text = encrypt_message(b32_text, encoded_secret_key)
    assert cyphered_text == expected


@pytest.mark.parametrize(
    "cyphered_text, expected",
    [
        (
            b"yZUZpPwjBuwxCPm44DhImHTuZr0O4ekT8sWq0ZkIJCjT9g/QrR/yKrUwRrDaQNRs",
            "hello my name is iker",
        ),
        (
            b"yZUZpPwjBuwxCPm44DhImMMNWjGoLis28dMxCk5x0FgzbF0gYqDA1dz3tfWFIcAK",
            "hello my name is 0x10",
        ),
        (
            b"yZUZpPwjBuwxCPm44DhImExHAqJb6o9NIvOVGZVHV3H3P39ZrLhIwk/XHNF+fi3gOI4Wavg0OJ+rIS0CliLtIQ==",
            "hello my name is Harry Potter",
        ),
    ],
)
def test_decypher(cyphered_text, expected):
    secret = decrypt_message(cyphered_text, encoded_secret_key)
    secret = base64.b32decode(secret).decode("utf-8")
    assert secret == expected

import pytest
from utils.ft_otp import gen_totp_token, save_seed, text_to_hex, check_key


@pytest.mark.parametrize(
    "timestep, expected",
    [(56060595, "851674"), (56060603, "113017"), (56060607, "003360")],
)
def test_gen_totp_token(timestep, expected):
    calculated_timestep = timestep
    secret = "NEVER GONNA GIVE YOU UP"
    x = str(gen_totp_token(secret.encode("utf-8"), calculated_timestep))
    assert x == expected


@pytest.mark.parametrize(
    "content, expected",
    [
        (
            b"4e4556455220474f4e4e41204749564520594f55205550",
            "OGvY+IeOlt948O4zVvwFv+XY9NEdBz9D2FywYvxb61IJCM9lGV8bYUIqnLELVWD+nId00mBkZ/knO4V242EFgnqnHegZqu4fyQk+1JqiPmBOKryTE1b85UxbByWnzeGv",
        )
    ],
)
def test_save_seed(content, expected):
    ft_otp_key = "keys/ft_otp.key"
    save_seed(content)

    with open(ft_otp_key, "r") as reader:
        lines = reader.readlines()[0]
        assert type(lines) == str
        assert len(lines) > 0

@pytest.mark.parametrize(
    "text, expected",
    [
        ("This is a sample", "5468697320697320612073616d706c65"),
        ("Never Gonna Give You Up", "4e6576657220476f6e6e61204769766520596f75205570"),
        ("NEVER GONNA GIVE YOU UP", "4e4556455220474f4e4e41204749564520594f55205550"),
    ],
)
def test_text_to_hex(text, expected):
    hex = text_to_hex(text)
    assert hex == expected


@pytest.mark.parametrize("key", [("No"), ("Short")])
def test_check_key_should_raise(key):
    with pytest.raises(Exception):
        check_key(key)


@pytest.mark.parametrize(
    "key",
    [("Lorem Ipsum es simplemente el te"), ("LOREM IPSUM ES SIMPLEMENTE EL TE")],
)
def test_check_key_should_not_raise(key):
    hex = text_to_hex(key)
    check_key(hex)

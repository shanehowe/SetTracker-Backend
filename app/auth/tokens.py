import datetime
import os

import jwt
import requests
from jwt.algorithms import RSAAlgorithm

from app.exceptions import UnsupportedProviderException
from app.utils import add_days_to_date

SECRET = os.environ["JWT_SECRET"]


def encode_jwt(payload: dict, algorithm: str = "HS256") -> str:
    today = datetime.datetime.now()
    twenty_four_hours = add_days_to_date(today, 1)
    updated_payload = {**payload, "exp": twenty_four_hours}
    return jwt.encode(updated_payload, SECRET, algorithm=algorithm)


def decode_jwt(token: str, algorithm: str = "HS256") -> dict:
    return jwt.decode(token, SECRET, algorithms=[algorithm])


def decode_and_verify_token(token: str, provider: str) -> dict:
    """
    Decode and verify an identity token based on the provider.

    Note this function calls the appropriate
    decode function based on the provider. Exceptions by this function and functions called within
    are raised if the provider is not supported or the token is invalid and should be caught by the caller.

    :param token: The identity token
    :param provider: The provider of the token
    :return: The decoded token
    :raises UnsupportedProviderException: If the provider is not supported
    """
    match provider:
        case "apple":
            return decode_verify_apple_identity_token(token)
        case _:
            raise UnsupportedProviderException(f"Unsupported provider {provider}")


def fetch_apple_public_keys():
    APPLE_KEYS_URL = "https://appleid.apple.com/auth/keys"
    response = requests.get(APPLE_KEYS_URL)
    return response.json()["keys"]


def decode_verify_apple_identity_token(token: str) -> dict:
    """
    Decode and verify an Apple identity token

    :param token: The Apple identity token
    :return: The decoded token
    :raises ValueError: If the public key is not found
    :raises jwt.exceptions.InvalidTokenError: If the token is invalid
    """
    apple_keys = fetch_apple_public_keys()

    try:
        headers = jwt.get_unverified_header(token)
    except jwt.exceptions.DecodeError:
        raise jwt.exceptions.InvalidTokenError()

    matching_key = next(
        (key for key in apple_keys if key["kid"] == headers["kid"]), None
    )
    if not matching_key:
        raise ValueError("Matching public key not found.")

    public_key = RSAAlgorithm.from_jwk(matching_key)

    return jwt.decode(
        token,
        key=public_key,  # type: ignore
        algorithms=["RS256"],
        audience="host.exp.Exponent",
        issuer="https://appleid.apple.com",
    )

import jwt
from jwt.algorithms import RSAAlgorithm
import datetime
import requests
from app.utils import add_days_to_date
from app.exceptions import UnsupportedProviderException


def encode_jwt(payload: dict, secret: str, algorithm: str = "HS256") -> str:
    today = datetime.datetime.now()
    twenty_four_hours = add_days_to_date(today, 1)
    updated_payload = {**payload, "exp": twenty_four_hours}
    return jwt.encode(updated_payload, secret, algorithm=algorithm)


def decode_jwt(token: str, secret: str, algorithm: str = "HS256") -> dict:
    return jwt.decode(token, secret, algorithms=[algorithm])


def decode_and_verify_token(token: str, provider: str) -> dict | None:
    match provider:
        case "apple":
            return decode_verify_apple_identity_token(token)
        case _:
            raise UnsupportedProviderException(f"Unsupported provider {provider}")


def fetch_apple_public_keys():
    APPLE_KEYS_URL = "https://appleid.apple.com/auth/keys"
    response = requests.get(APPLE_KEYS_URL)
    return response.json()["keys"]


def decode_verify_apple_identity_token(token: str) -> dict | None:
    apple_keys = fetch_apple_public_keys()

    try:
        headers = jwt.get_unverified_header(token)
    except jwt.exceptions.DecodeError:
        return None

    matching_key = next((key for key in apple_keys if key["kid"] == headers["kid"]), None)
    if not matching_key:
        raise ValueError("Matching public key not found.")
    
    public_key = RSAAlgorithm.from_jwk(matching_key)
    
    # Now verify and decode the token
    try:
        decoded = jwt.decode(
            token,
            key=public_key,  # type: ignore
            algorithms=["RS256"],
            audience="host.exp.Exponent",
            issuer="https://appleid.apple.com"
        )
    except jwt.exceptions.InvalidAudienceError | jwt.exceptions.DecodeError:
        return None
    return decoded

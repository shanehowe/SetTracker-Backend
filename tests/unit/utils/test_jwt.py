from app.auth.tokens import encode_jwt, decode_jwt


def test_encode_jwt():
    payload = {"user_id": "123"}
    secret = "secret"
    token = encode_jwt(payload, secret)
    assert isinstance(token, str)


def test_decode_jwt():
    payload = {"user_id": "123"}
    secret = "secret"
    token = encode_jwt(payload, secret)
    decoded = decode_jwt(token, secret)
    assert decoded["user_id"] == payload["user_id"]
    assert "exp" in decoded


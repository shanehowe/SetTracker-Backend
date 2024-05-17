import pytest
from pydantic import ValidationError

from app.models.user_models import BaseUser, UserEmailAuthInSignUpAndIn


@pytest.mark.parametrize(
    "email",
    [
        "someone@something.com",
        "   someone@something.com   ",
        "SOMEONE@SOMETHING.COM",
        "   SOMEONE@SOMETHING.COM   ",
    ],
)
def test_base_user_transforms_email_to_lowercase_and_strips_whitespace(email):
    user = BaseUser(email=email)
    assert user.email == email.strip().lower()


@pytest.mark.parametrize("password", ["12345", "", "123"])
def test_user_email_auth_raises_ecxeption_when_password_length_less_than_six(password):
    with pytest.raises(ValueError):
        UserEmailAuthInSignUpAndIn(email="something@something.com", password=password)


@pytest.mark.parametrize("password", ["123456", "1234567", "12345678"])
def test_user_email_auth_does_not_raise_exception_when_password_length_is_six_or_more(
    password,
):
    try:
        UserEmailAuthInSignUpAndIn(email="something@something.com", password=password)
    except ValidationError:
        pytest.fail(
            f"ValidationError was raised unexpectedly for password: {password} - Length: {len(password)}"
        )

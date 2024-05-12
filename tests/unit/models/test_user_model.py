import pytest

from app.models.user_models import BaseUser


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

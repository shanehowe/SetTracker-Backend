from app.utils.utils import to_camel
from app.utils.date_utils import add_days_to_date
import pytest
import datetime


@pytest.mark.parametrize(
    "test_input, expected",
    [
        ("hello_world", "helloWorld"),
        ("hello", "hello"),
        ("hello_world_", "helloWorld"),
        ("hello_world__", "helloWorld"),
        ("hello_world__this", "helloWorldThis"),
        ("", "")
    ],
)
def test_to_camel(test_input, expected):
    assert to_camel(test_input) == expected


@pytest.mark.parametrize(
    "test_input, days, expected",
    [
        (datetime.datetime(2021, 1, 1), 7, datetime.datetime(2021, 1, 8)),
        (datetime.datetime(2021, 1, 1), 0, datetime.datetime(2021, 1, 1)),
        (datetime.datetime(2021, 1, 1), 1, datetime.datetime(2021, 1, 2)),
        (datetime.datetime(2021, 1, 1), 365, datetime.datetime(2022, 1, 1)),
    ],
)
def test_add_days_to_date(test_input, days, expected):
    assert add_days_to_date(test_input, days) == expected
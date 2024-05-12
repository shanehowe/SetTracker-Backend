import datetime

import pytest

from app.utils.date_utils import add_days_to_date
from app.utils.string_utils import strip_and_lower


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


@pytest.mark.parametrize(
    "test_input, expected",
    [
        ("  L ", "l"),
        ("I DONT KNOW", "i dont know"),
        ("  I DONT KNOW  ", "i dont know"),
        ("i dont know", "i dont know"),
    ],
)
def test_strip_and_lower(test_input, expected):
    assert strip_and_lower(test_input) == expected

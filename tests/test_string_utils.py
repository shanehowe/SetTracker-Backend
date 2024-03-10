from utils.string_utils import to_camel
import pytest


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

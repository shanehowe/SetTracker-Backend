from unittest.mock import MagicMock

import pytest

from app.models.set_models import SetInDB
from app.service.set_service import SetService


@pytest.fixture
def mock_set_data_access():
    return MagicMock()


@pytest.fixture
def set_service(mock_set_data_access):
    return SetService(mock_set_data_access)


def test_get_users_sets_by_exercise_id(set_service, mock_set_data_access):
    mock_set_data_access.get_users_sets_by_exercise_id = MagicMock(return_value=[])
    set_service.get_users_sets_by_exercise_id("1", "2")
    mock_set_data_access.get_users_sets_by_exercise_id.assert_called_once_with(
        exercise_id="1", user_id="2"
    )

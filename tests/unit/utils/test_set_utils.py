import pytest

from app.models.set_models import SetGroup, SetInDB
from app.utils.set_utils import group_sets_by_date

# This looks crazy long, but its just how black formats it
test_data = [
    (
        [
            SetInDB(
                id="1",
                reps=2,
                exercise_id="1",
                user_id="1",
                weight=100,
                date_created="2022-01-01",
            ),
            SetInDB(
                id="2",
                reps=2,
                exercise_id="1",
                user_id="1",
                weight=100,
                date_created="2022-01-01",
            ),
            SetInDB(
                id="3",
                reps=2,
                exercise_id="1",
                user_id="1",
                weight=100,
                date_created="2022-01-02",
            ),
            SetInDB(
                id="4",
                reps=2,
                exercise_id="1",
                user_id="1",
                weight=100,
                date_created="2022-01-02",
            ),
            SetInDB(
                id="5",
                reps=2,
                exercise_id="1",
                user_id="1",
                weight=100,
                date_created="2022-01-03",
            ),
        ],
        [
            SetGroup(
                sets=[
                    SetInDB(
                        id="1",
                        reps=2,
                        exercise_id="1",
                        user_id="1",
                        weight=100,
                        date_created="2022-01-01",
                    ),
                    SetInDB(
                        id="2",
                        reps=2,
                        exercise_id="1",
                        user_id="1",
                        weight=100,
                        date_created="2022-01-01",
                    ),
                ],
                date_created="2022-01-01",
            ),
            SetGroup(
                sets=[
                    SetInDB(
                        id="3",
                        reps=2,
                        exercise_id="1",
                        user_id="1",
                        weight=100,
                        date_created="2022-01-02",
                    ),
                    SetInDB(
                        id="4",
                        reps=2,
                        exercise_id="1",
                        user_id="1",
                        weight=100,
                        date_created="2022-01-02",
                    ),
                ],
                date_created="2022-01-02",
            ),
            SetGroup(
                sets=[
                    SetInDB(
                        id="5",
                        reps=2,
                        exercise_id="1",
                        user_id="1",
                        weight=100,
                        date_created="2022-01-03",
                    )
                ],
                date_created="2022-01-03",
            ),
        ],
    ),
    ([], []),
    
]


@pytest.mark.parametrize("sets, expected", test_data)
def test_group_sets_by_date(sets, expected):
    assert group_sets_by_date(sets) == expected

import pytest
from pydantic import ValidationError

from app.models.set_models import BaseSetModel, Tempo


def test_tempo_raises_exception_when_eccentric_less_than_zero():
    with pytest.raises(ValidationError):
        Tempo(eccentric=-1, concentric=1, pause=1)


def test_tempo_raises_exception_when_concentric_less_than_zero():
    with pytest.raises(ValidationError):
        Tempo(eccentric=1, concentric=-1, pause=1)


def test_tempo_raises_exception_when_pause_less_than_zero():
    with pytest.raises(ValidationError):
        Tempo(eccentric=1, concentric=1, pause=-1)


@pytest.mark.parametrize("weight", [-0.1, -1, 0])
def test_base_set_model_raises_exception_when_weight_is_less_or_equal_to_zero(weight):
    with pytest.raises(ValidationError):
        BaseSetModel(exercise_id="1", weight=weight, reps=1)


@pytest.mark.parametrize("reps", [0, -1])
def test_base_set_model_raises_exception_when_reps_is_less_or_equal_to_zero(reps):
    with pytest.raises(ValidationError):
        BaseSetModel(exercise_id="1", weight=1, reps=reps)
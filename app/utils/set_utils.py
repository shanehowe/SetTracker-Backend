import functools
from copy import deepcopy
from datetime import datetime

from app.models.set_models import SetGroup, SetInDB


def group_sets_by_date(sets: list[SetInDB]) -> list[SetGroup]:
    """
    Group sets by date_created attribute
    :param sets: list of SetInDB
    :return: list of SetGroup
    """

    def __grouping_func(acc, set_):
        dict_key = set_.date_created.split("T")[0]
        if dict_key not in acc:
            acc[dict_key] = []
        acc[dict_key].append(set_)
        return acc

    grouped_dict: dict = functools.reduce(__grouping_func, sets, {})
    return [
        SetGroup(sets=value, date_created=key) for key, value in grouped_dict.items()
    ]


def sorted_set_history(set_history: list[SetGroup]) -> list[SetGroup]:
    """
    Set history in json/dict format is a list of dicts. Each
    dict has a date_created and sets key which is a list.
    Firstly this function sorts the top level history by date in reverse
    chronological order. Then for each dictionary sorts the sets in the same way.

    :param set_history: The data to be sorted
    :returns SetGroup: In sorted order.
    """
    data_for_sort = deepcopy(set_history)
    for set_group in data_for_sort:
        set_group.sets.sort(
            key=lambda x: datetime.fromisoformat(x.date_created), reverse=True
        )
    data_for_sort.sort(
        key=lambda x: datetime.fromisoformat(x.date_created), reverse=True
    )
    return data_for_sort

import functools

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

    grouped_dict = functools.reduce(__grouping_func, sets, {})
    return [
        SetGroup(sets=value, date_created=key) for key, value in grouped_dict.items()
    ]

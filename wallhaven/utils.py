from typing import Dict, List


def string_to_bool(s: str) -> bool:
    return bool(int(s))


def bool_to_string(*booleans: bool) -> str:
    result = ""
    for b in booleans:
        result += str(int(b))
    return result


def get_first_three(numeric_string: str) -> str:
    """Gets the first three characters from a numeric string.

    If the string's length is smaller than three, zeros are added until it reaches the desired
    length.
    """
    result = ""
    if len(numeric_string) < 3:
        missing = 3 - len(numeric_string)
        result = numeric_string + "0" * missing

    else:
        for index in range(0, len(numeric_string)):
            if index == 3:
                break

            result += numeric_string[index]

    return result


def numbers_from_list(data: List[str], fields: List[str]) -> str:
    """Gets the categories/purity numbers from a list of categories/purity."""

    # data = ["general", "people"]
    # fields = ["general", "anime", "people"]
    # return: "101"

    numbers: List[str] = []
    for index, category in enumerate(fields):
        if category in data:
            numbers.insert(index, "1")
        else:
            numbers.insert(index, "0")

    return "".join(numbers)


def numbers_from_dict(data: Dict[str, bool], fields: List[str]) -> str:
    """Gets the categories/purity numbers from a dictionary of categories/purity.

    If an item from `data` has a value other than a boolean, its value will default to False.
    """

    # data = {"general": True, "people": True}
    # fields = ["general", "anime", "people"]
    # return: "101"

    numbers: List[str] = []
    for index, category in enumerate(fields):
        value = data.get(category, False)
        # Category was present in the dict, but its value was not a boolean, so we default to False.
        if not isinstance(value, bool):
            value = False

        if value:
            numbers.insert(index, "1")
        else:
            numbers.insert(index, "0")

    return "".join(numbers)

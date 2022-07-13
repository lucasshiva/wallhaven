from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, List, Type, TypeVar, Union

from pydantic import BaseModel

from wallhaven import utils

T_PARAM = TypeVar("T_PARAM", bound="BaseParameter")
T_ENUM = TypeVar("T_ENUM", bound="BaseEnum")
T_CATEGORY = TypeVar("T_CATEGORY", bound="BaseCategories")

CategoryTypes = Union[str, int, List[str], Dict[str, bool]]


class BaseParameter(ABC, BaseModel):
    """The parent class for all parameters."""

    class Config:
        validate_assignment = True

    @abstractmethod
    def as_query_param(self) -> str:
        raise NotImplementedError


class BaseEnum(Enum):
    """The parent class for all enums."""

    @classmethod
    def create(cls: Type[T_ENUM], data: str) -> T_ENUM:
        """Create an instance of ``cls`` from data.

        Args:
            data: A string referencing the enum's name or value.
        """
        data = data.lower().replace(" ", "")

        for name, enum_obj in cls._member_map_.items():
            if data in (name.lower(), enum_obj.value):
                data = enum_obj.value

        return cls(data)

    def as_query_param(self) -> str:
        return self.value


class BaseCategories(BaseParameter):
    def _get_categories_dict(self, data: CategoryTypes) -> Dict[str, bool]:
        """Parses `data` and creates a dictionary of the categories.

        Missing categories are False by default. If `data` is a numerical string, however, it is
        only possible to add missing values to the right of the string. For example, the  string `1`
        will set the first category to True and the rest to False. The string `01` will set the
        first category to False, the second category to True, and the third category will default to
        False.

        This means that, if you want the first category to be False and the others to True, you
        can't pass the string `11`, as this method would set the first and second categories to
        True, thus defaulting the last category to False.

        Args:
            data:
                The data to parse.

        Returns:
            A dictionary of categories. Example:

            {
                "general": True,
                "anime": False,
                "people": True,
            }

        Examples:
            >>> _get_categories_dict("anime,people")
            {"general": False, "anime": True, "people" True}

            The result above is also achieved using other data structures, such as:
            - Lists: `["anime", "people"]`
            - Dicts: `{"anime": True, "people": True}`
            - Numerical strings: `"011"`
        """
        field_names = list(self.__fields__.keys())
        if isinstance(data, str) and data.isnumeric():
            numbers = utils.get_first_three(data)
        elif isinstance(data, str):  # Not a numeric string.
            category_list = [c.strip() for c in data.split(",")]
            numbers = utils.numbers_from_list(category_list, field_names)
        elif isinstance(data, list):
            numbers = utils.numbers_from_list(data, field_names)
        elif isinstance(data, dict):
            numbers = utils.numbers_from_dict(data, field_names)
        else:
            numbers = "111"

        # Make the dict from the numbers.
        categories: Dict[str, bool] = {}
        for attr, number in zip(field_names, numbers):
            categories[attr] = utils.string_to_bool(number)

        return categories

    @classmethod
    def create(cls: Type[T_CATEGORY], data: CategoryTypes) -> T_CATEGORY:
        """Creates an instance of `cls` from data."""
        instance = cls()
        categories = instance._get_categories_dict(data)
        for category, value in categories.items():
            setattr(instance, category, value)

        return instance

    def as_query_param(self) -> str:
        attrs: List[bool] = [bool(getattr(self, field)) for field in self.__fields__.keys()]
        return utils.bool_to_string(*attrs)

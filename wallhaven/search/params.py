from typing import Any, Dict

from pydantic import BaseModel, Field

from wallhaven.search import Categories, ColorManager, Purity, Query
from wallhaven.search.enums import Sorting, SortingOrder, ToplistRange


class SearchParameters(BaseModel):
    query: Query = Field(default_factory=Query, alias="q")
    categories: Categories = Categories()
    purity: Purity = Purity()
    sorting: Sorting = Sorting.DateAdded
    order: SortingOrder = SortingOrder.Descending
    toplist_range: ToplistRange = Field(default=ToplistRange.LastMonth, alias="topRange")
    colors: ColorManager = ColorManager()

    def as_dict(self, skip_defaults: bool = False, skip_empty: bool = True) -> dict:
        """Returns the instance as a dictionary.

        Args:
            skip_defaults:
                Skip parameters whose current values are the same as their default values. This is
                useful if the dictionary is supposed to only contain parameters that have been
                modified by the user.
            skip_empty:
                Skip parameters without a value. This is useful if you want to remove items such as
                `{'colors': ''}` from the dictionary.

        Returns:
            A dictionary containing all the parameters formatted as a query parameters. For example:

            {
                'categories': '111',
                'purity': '100',
                'sorting': 'date_added',
                ...
            }
        """
        params: Dict[str, Any] = {}

        for field, value in self.__fields__.items():
            attr = getattr(self, field)

            if skip_empty and (attr is None or not attr.as_query_param()):
                continue

            if skip_defaults and attr == value.default:
                continue

            name = value.alias if value.has_alias else field
            if not skip_empty and attr is None:
                params[name] = None
            else:
                params[name] = attr.as_query_param()

        return params

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SearchParameters":
        """Creates an instance of ``SearchParameters`` from data."""
        attrs = {}
        for field, value in cls.__fields__.items():
            # We use the alias when possible
            name = value.alias if value.has_alias else field

            if name not in [k.lower() for k in data]:
                continue
            attr = value.type_

            # We assume that every parameter has a `.create()` classmethod.
            attrs[name] = attr.create(data[name])

        return cls(**attrs)

from typing import Any, Dict

from pydantic import Field

from wallhaven.models import BaseModel
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

    # TODO: Maybe just use this instead of `as_dict()`.
    def dict(self, *args, **kwargs) -> Dict[str, Any]:  # type: ignore
        # This is to format the params when calling `.dict()` from `Meta`.
        return self.as_dict(skip_defaults=True)

    def as_dict(self, skip_defaults: bool = False, skip_empty: bool = True) -> Dict[str, Any]:
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

    def _get_attrs_from_dict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(data, dict):
            raise ValueError(f"Cannot create `SearchParameters` from a {type(data)}")

        attrs: Dict[str, Any] = {}
        for field, value in self.__fields__.items():
            # We use the alias whenever possible
            name = value.alias if value.has_alias else field

            if name not in [k.lower() for k in data]:
                continue

            # We assume that every parameter has a `.create()` classmethod.
            attrs[name] = value.type_.create(data[name])

        return attrs

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SearchParameters":
        """Creates an instance of ``SearchParameters`` from data."""
        instance = cls()
        instance.load_dict(data)
        return instance

    def load_dict(self, data: Dict[str, Any]) -> None:
        """Load parameters from `data`."""
        for attr, value in self._get_attrs_from_dict(data).items():
            setattr(self, attr, value)

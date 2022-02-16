from dataclasses import dataclass

from typing_extensions import Literal

from wallhaven.models.base import BaseModel


@dataclass
class Collection(BaseModel):
    """Represents a collection.

    This model only contains information about the collection itself. It does not show a
    listing of the wallpapers inside it, for that you need `CollectionListing` instead.

    Attributes:
        id (int): The ID of the collection.
        label (str): A user defined name/label for the collection.
        views (int): The amount of views the collection has.
        public (int): Whether the collection is public (1) or private (0).
        count (int): The amount of wallpapers inside the collection.
    """

    id: int
    label: str
    views: int

    # The API returns this field as 1 (True) or 0 (False).
    public: Literal[0, 1]
    count: int

    def is_public(self) -> bool:
        """Returns if the collection is marked as private (False) or public (True).

        This is essentially the same as calling the `public` attribute in a condition.
        For example: `if collection.is_public()` instead of `if collection.public`.
        """
        # True if 1, False if 0.
        return bool(self.public)

import re
from typing import Any, Dict, Optional, Sequence, Set, List, Union

from pydantic import Field
from typing_extensions import Literal

from wallhaven.search.base import BaseParameter


class Query(BaseParameter):
    included_keywords: Set[str] = Field(default_factory=set)
    excluded_keywords: Set[str] = Field(default_factory=set)
    user: Optional[str] = None
    exact_tag: Optional[int] = None
    image_type: Optional[Literal["png", "jpg", "jpeg"]] = None
    similar: Optional[str] = None

    @property
    def text(self) -> str:
        return self._construct_query()

    def _construct_query(self) -> str:
        query = []

        for keyword in self.included_keywords:
            query.append(f"+{keyword}")

        for keyword in self.excluded_keywords:
            query.append(f"-{keyword}")

        if self.user is not None:
            query.append(f"@{self.user}")

        if self.exact_tag is not None:
            query.append(f"id:{self.exact_tag}")

        if self.image_type is not None:
            query.append(f"type:{self.image_type}")

        if self.similar is not None:
            query.append(f"like:{self.similar}")

        return "+".join(query)

    def as_query_param(self) -> str:
        return self.text

    @classmethod
    def create(cls, s: str) -> "Query":
        """Creates an instance of `Query` from a string."""
        instance = cls()
        attrs = instance._parse_string(s)

        # We could return 'instance.load_string(s)' to avoid creating the class twice, but we'd lose
        # the validation from pydantic. There should be a way around this, I just don't know it
        # yet.
        return cls(**attrs)

    def _parse_string(self, s: str) -> Dict[str, Any]:
        words = [word.lower() for word in str(s).split(" ")]
        attrs: Dict[str, Any] = {"included_keywords": [], "excluded_keywords": []}

        # TODO: Make the regex remove extra identifiers.
        # It would be great if the regex could understand that '-+animals' means we want to exclude
        # the world 'animals'.
        for word in words:
            if re.search(r"^[\w|\+]\w+$", word):
                attrs["included_keywords"].append(word.replace("+", ""))
            elif re.search(r"^\-\w+$", word):
                attrs["excluded_keywords"].append(word.replace("-", ""))
            elif re.search(r"^@", word):
                attrs["user"] = word.replace("@", "")
            elif re.search(r"^id:\d+$", word):
                attrs["exact_tag"] = int(word.replace("id:", ""))
            elif re.search(r"^type:\w+$", word):
                attrs["image_type"] = word.replace("type:", "")
            elif re.search(r"^like:\w+$", word):
                attrs["similar"] = word.replace("like:", "")

        return attrs

    def _format_input(
        self,
        input: Union[str, int],
        param: Literal["include", "exclude", "user", "exact_tag", "image_type", "similar"],
    ) -> str:
        """Add the identifier for the param, enabling the regex in `_parse_string` to function."""
        id_map = {
            "include": "+",
            "exclude": "-",
            "user": "@",
            "exact_tag": "id:",
            "image_type": "type:",
            "similar": "like:",
        }

        identifier = id_map.get(param, None)
        if identifier is None:
            raise ValueError(f"The parameter must be one of: {list(id_map.keys())}")

        input = str(input)
        if input[0] == identifier:
            return input

        return f"{identifier}{input}"

    def load_string(self, string: str) -> None:
        """Loads the search query from a string.

        Args:
            string:
                The string to load. Parameters must be separated by a space.

        Examples:
            >>> query = Query()
            >>> query.load_string('forest +animals -cars type:png')
            >>> print(query)
            <Query(included_keywords={'forest', 'animals'}, ...)>
        """
        attrs = self._parse_string(string)

        for attr, value in attrs.items():
            if "keywords" in attr:
                value = set(value)
            setattr(self, attr, value)

    def include_one(self, keyword: str) -> None:
        """Includes a keyword/tag to the search query.

        Args:
            keyword:
                The keyword or tag to include.

        Examples:
            >>> query = Query()
            >>> query.include_one("animals")
        """
        # It is possible to include/exclude several keywords if `keyword` is separated by spaces.
        # We, however, do not want this functionality in this method. Therefore, we add only the
        # first item of the list.
        keyword = self._format_input(keyword, "include")
        word: List[str] = self._parse_string(keyword)["included_keywords"]
        if not word:
            raise ValueError(f"Unable to include keyword: {keyword}")

        self.included_keywords.add(word[0])

    def include_many(self, keywords: Sequence[str]) -> None:
        """Includes several keywords/tags to the search query.

        If `keywords` is a string, it will be considered as a single keyword.

        Args:
            keywords:
                A sequence of keywords/tags to include.

        Examples:
            >>> query = Query()
            >>> query.include_many(['animals', 'forest'])
        """
        if isinstance(keywords, str):
            self.include_one(keywords)
            return

        for k in keywords:
            self.include_one(k)

    def exclude_one(self, keyword: str) -> None:
        """Excludes a keyword/tag from the search query.

        Args:
            keyword:
                The keyword/tag to exclude.

        Examples:
            >>> query = Query()
            >>> query.exclude_one('animals')
        """
        # We need the minus for the regex to work.
        keyword = self._format_input(keyword, "exclude")
        word: List[str] = self._parse_string(keyword)["excluded_keywords"]
        if not word:
            raise ValueError(f"Unable to exclude keyword: {keyword}")

        self.excluded_keywords.add(word[0])

    def exclude_many(self, keywords: Sequence[str]) -> None:
        """Excludes several keywords/tags from the search query.

        If `keywords` is a string, it will be considered as a single keyword.

        Args:
            keywords:
                A sequence of keywords/tags to exclude.

        Examples:
            >>> query = Query()
            >>> query.exclude_many(['animals', 'forest'])
        """
        if isinstance(keywords, str):
            self.exclude_one(keywords)
            return

        for k in keywords:
            self.exclude_one(k)

    def filter_by_user(self, username: str) -> None:
        """Makes the search return only wallpapers uploaded by this user."""
        username = self._format_input(username, "user")
        self.user = self._parse_string(username)["user"]

    def filter_by_tag(self, tag_id: Union[int, str]) -> None:
        """Makes the search return only wallpapers with this tag."""
        tag_id = self._format_input(tag_id, "exact_tag")
        self.exact_tag = self._parse_string(tag_id)["exact_tag"]

    def filter_by_type(self, image_type: Literal["png", "jpg", "jpeg"]) -> None:
        image_type = self._format_input(image_type, "image_type")  # type: ignore
        self.image_type = self._parse_string(image_type)["image_type"]

    def find_similar(self, wallpaper_id: str) -> None:
        """Makes the search return only wallpapers similar to the given wallpaper."""
        wallpaper_id = self._format_input(wallpaper_id, "similar")
        self.similar = self._parse_string(wallpaper_id)["similar"]

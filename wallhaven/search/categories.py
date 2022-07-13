from wallhaven.search.base import BaseCategories


class Categories(BaseCategories):
    general: bool = True
    anime: bool = True
    people: bool = True

    def set(self, *, general: bool, anime: bool, people: bool) -> None:
        self.general = general
        self.anime = anime
        self.people = people

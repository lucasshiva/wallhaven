from wallhaven.search.base import BaseCategories


class Purity(BaseCategories):
    sfw: bool = True
    sketchy: bool = False
    nsfw: bool = False

    def set(self, *, sfw: bool, sketchy: bool, nsfw: bool) -> None:
        self.sfw = sfw
        self.sketchy = sketchy
        self.nsfw = nsfw

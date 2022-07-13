from wallhaven.search.base import BaseEnum


class Sorting(BaseEnum):
    DateAdded = "date_added"
    Relevance = "relevance"
    Random = "random"
    Views = "views"
    Favorites = "favorites"
    Toplist = "toplist"


class ToplistRange(BaseEnum):
    LastDay = "1d"
    LastThreeDays = "3d"
    LastWeek = "1w"
    LastMonth = "1M"
    LastThreeMonths = "3M"
    LastSixMonths = "6M"
    LastYear = "1y"


class SortingOrder(BaseEnum):
    Descending = "desc"
    Ascending = "asc"


class Color(BaseEnum):
    BloodRed = "#660000"
    CrimsonRed = "#990000"
    BostonUniversityRed = "#cc0000"
    PersianRed = "#cc3333"
    DarkPink = "#ea4c88"
    Violet = "#993399"
    RebeccaPurple = "#663399"
    BluePigment = "#333399"
    TrueBlue = "#0066cc"
    RichEletricBlue = "#0099cc"
    SeaSerpent = "#66cccc"
    Green = "#77cc33"
    Avocado = "#669900"
    MetallicGreen = "#336600"
    BronzeYellow = "#666600"
    DarkYellow = "#999900"
    Pear = "#cccc33"
    Yellow = "#ffff00"
    Sunglow = "#ffcc33"
    VividGamboge = "#ff9900"
    Orange = "#ff6600"
    MediumVermillion = "#cc6633"
    Coconut = "#996633"
    PhilippineBronze = "#663300"
    Black = "#000000"
    SpanishGray = "#999999"
    ChineseSilver = "#cccccc"
    White = "#ffffff"
    Arsenic = "#424153"

    def as_query_param(self) -> str:
        return self.value[1:]

    @classmethod
    def create(cls, s: str) -> "Color":
        s = s.lower().replace(" ", "")

        instance: Color
        try:
            instance = super().create(s)
        except ValueError:
            # Getting here means the string is equal to neither the name nor the value.
            # So we add a '#' in case the string is something like 'ffffff', without the '#'.
            instance = super().create("#" + s)

        return instance

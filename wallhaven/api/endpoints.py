"""List of endpoints that Wallhaven knows about.

For more information, see: https://wallhaven.cc/help/api
"""

# fmt: off
API_ENDPOINTS = {
    "wallpaper":            "https://wallhaven.cc/api/v1/w/{id}",
    "tag":                  "https://wallhaven.cc/api/v1/tag/{id}",
    "settings":             "https://wallhaven.cc/api/v1/settings",
    "collection":           "https://wallhaven.cc/api/v1/collections/{username}",
    "collection_apikey":    "https://wallhaven.cc/api/v1/collections",
    "collection_listing":   "https://wallhaven.cc/api/v1/collections/{username}/{id}",
    "search":               "https://wallhaven.cc/api/v1/search"
}

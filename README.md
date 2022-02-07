# wallhaven
A Python library and CLI for interacting with the Wallhaven API.

`wallhaven` provides a simple interface to access the data provided by the API in a quick and easy way. The main goal is to automate the searching and downloading of wallpapers by using the CLI and to enable users to import the code and use it in their own scripts.

## Features
`wallhaven` currently allows you to interact with:
- **Wallpapers**
- **Tags**
- **User Settings**
- **User Collections**
- **Collection Listing**
- **Search**

**Note**: There is no pagination/filtering available for **Collection Listing** and **Searching**.
## Installation
**Note**: Before installing, make sure you have Python 3.7 or newer installed.<br><br>

`wallhaven` is available as package in PyPI. You can install it using pip.
```sh
# Make sure you're using the latest version of pip.
pip install --upgrade pip

# Then, install the package.
pip install wallhaven
```
### Installing from source
Additionally, for development purposes, you may want to install this project from source. First, you'll need to install and configure [Poetry](https://python-poetry.org/docs/) on your machine. Then, in your terminal, run the following commands:
```sh
# Clone the repository
git clone https://github.com/lucasshiva/wallhaven

# Go into the folder
cd wallhaven

# Create a virtual environment using Poetry.
poetry env use python

# Activate it
poetry shell

# Install the dependencies (and wallhaven)
poetry install
```

## Usage
The project is still small and fairly simple to use.

First, instantiate the `wallhaven.API` class.
```python
import wallhaven

api = wallhaven.API()
```
Some operations need an **API key** to function. In such cases, you pass your API key directly to the constructor or set the environment variable `WALLHAVEN_API_KEY`. The API key in the constructor takes priotity over the environment variable.

```python
import wallhaven

# If an API key is *NOT* passed to the constructor, `wallhaven.API` will try to load it from the
# environment variable.
api = wallhaven.API(api_key="my-apy-key")
```

After that, you may now start interacting with the API.
```python
# ----------------- Wallpaper -----------------
# Get wallpaper information.
wallpaper = api.get_wallpaper(<wallpaper_id>)

# You can also download it.
wallpaper.save(<directory>)

# -------------------- Tag --------------------
# Get tag information.
tag = api.get_tag(<tag_id>)

# --------------- User Settings ---------------
# Fetch user browsing settings. These are the settings used when calling `search`.
# An API key is required.
settings = api.get_user_settings()

# --------------- User Collections ---------------
# Fetch public collections.
collections = api.get_collections_from_username(<username>)

# Or all collections (including private ones) from an authenticated user.
# An API key is required.
collections = wallhaven.get_collections_from_apikey()

# --------------- Collection Listing ---------------
# To view the listing of a PUBLIC collection:
listing = api.get_collection_listing(<username>, <collection_id>)

# To view the listing of a PRIVATE collection:
# The only difference is that you also need an API key.
listing = api.get_private_collection_listing(<username>, <collection_id>)

# Download wallpapers.
# Listing is limited to the first 24 wallpapers.
for wallpaper in listing.data:
    wallpaper.save(<directory>)

# -------------------- Searching --------------------
# This method will use your API key if one is available.
# With the way the Wallhaven API works, searches are performed utilizing the user's 
# browsing settings when provide with an API key. This means that by changing the amount
# of results per page in your settings, you also change the results per page in here.
# Limited to 24/32/64 results per page. 
results = api.search()

# Whether you have provided an API key or not, you may still set the search parameters
# by calling `wallhaven.params`.
# It should be noted that these have priority over your settings. 
api.params["categories"] = "110"
api.params["sorting"] = "toplist"
api.params["topRange"] = "1M"
results = api.search()

# Wallpapers in search results are stored similarly to collection listings.
# Which means that you can download them with:
for wallpaper in results.data:
    wallpaper.save(<directory>)
```

When it comes to searching, it should be noted that if you provide both an API key and search parameters, `Wallhaven` will merge them together while giving priority to the search parameters. For example, if you set the `purity` to `sfw` in your browsing settings, every search you perform will return sfw wallpapers unless you change the purity in the search parameters. 

It is recommended to use both methods together, as you can change the `Thumbs Per Page` option in your browsing settings to increase
the amount of wallpapers returned per page/request to a maximum of 64. You may also want to set a permanent parameter, like always searching for the same categories/purity. In this case, you can set the option in your browsing settings and only modify what you need in the search parameters.

```python
import wallhaven

# Load API key from the environment variable.
api = wallhaven.API()

# Set the parameters to return the top wallpapers.
api.params["sorting"] = "toplist"

# Perform the search. 
# Since I set the categories, purity and toplist range in my browsing settings, this 
# will return the top SFW wallpapers from the last month that belong to the General or 
# Anime category. 
results = api.search()

# If I wanted to override some of the parameters, such as only retrieving the top 
# wallpapers from the `General` category and from the last week, it would be as
# simple as doing:
api.params["category"] = "100"
api.params["topRange"] = "1w"  # Only works if `sorting` is equal to "toplist" 
api.params["sorting"] = "toplist"

# Search again, this time using the updated parameters.
results = api.search()
```

For more information about the search parameters and how to define them, you can check the [parameter list](https://wallhaven.cc/help/api#search).

## Rate Limiting and Errors
From the official docs:
> API calls are currently limited to **45** per minute. If you do hit this limit, you will receive a **429 - Too many requests** error.
> Attempting to access a NSFW wallpaper without an API Key or with an invalid one will result in a **401 - Unauthorized** error.
> Any other attempts to use an invalid API key will result in a **401 - Unauthorized** error.

### Am I allowed to run scrapper/mass download scripts?
> We ask that you don't. You may have noticed we don't run any ads on this website. Because of that, we don't pay for the big boxes that can absorb huge requests. We're not some big company here, just a few guys trying to provide a nice wallpaper website. 

Please be mindful of how you use this project. If you need more information, feel free to visit their [FAQ](https://wallhaven.cc/faq) or the official [API documentation](https://wallhaven.cc/help/api). 


## Disclaimer
This is an unofficial project which was built for educational purposes, therefore, it has no affiliation with [Wallhaven](https://wallhaven.cc/). 

## License
See [License](LICENSE) for more information.

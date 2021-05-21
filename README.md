# wallhaven
A Python library and CLI for interacting with the Wallhaven API.

`wallhaven` provides a simple interface to access the data provided by the API in a quick and easy way. The main goal is to automate the searching and downloading of wallpapers by using the CLI and to enable users to import the code and use it in their own scripts.

## Development
This project is currently being rewritten from scratch. The old version is located at [wallhaven-old](https://github.com/lucasshiva/wallhaven-old). The old version is still available on [PyPI](https://pypi.org/project/wallhaven/), although that won't be the case when the development of the initial release (version 0.1.0) finishes. 

Keep in mind that every section below [Development](#Development) can (and probably will) change during the development stages.
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
git clone 

# Go into the folder
cd wallhaven

# Inside the directory, install the dependencies (and wallhaven) using Poetry.
poetry install
```

This should install `wallhaven` in your global Python installation. If you are planning on contributing to this project, it is good practice to create a virtual envinroment before installing it. For that, you simply need to run:
```sh
# Create the virtual environment
# You may also specify a python version if you are using something like Pyenv.
# >> poetry env use python3.7
poetry env use python

# Activate it.
poetry shell

# Install dependencies and the project locally.
poetry install
```
Now you only have access to `wallhaven` while inside the virtual environment. You can deactivate it by typing `exit`.

## Usage
**TBD**. This section is still a work-in-progress. It is supposed to show how to get started using both the library and the CLI. This will be updated when version 0.1.0 is released.

## Rate Limiting and Errors
From the official docs:
> API calls are currently limited to **45** per minute. If you do hit this limit, you will receive a **429 - Too many requests** error.
> Attempting to access a NSFW wallpaper without an API Key or with an invalid one will result in a **401 - Unauthorized** error.
> Any other attempts to use an invalid API key will result in a **401 - Unauthorized** error.

### Am I allowed to run scrapper/mass download scripts?
> We ask that you don't. You may have noticed we don't run any ads on this website. Because of that, we don't pay for the big boxes that can absorb huge requests. We're not some big company here, just a few guys trying to provide a nice wallpaper website. 

Please be mindful of how you use this project. If you need more information, feel free to visit their [FAQ](https://wallhaven.cc/faq) or the official [API documentation](https://wallhaven.cc/help/api). 


## Disclaimer
This is an unofficial project which was built for educational purposes, therefore it has no affiliation with [Wallhaven](https://wallhaven.cc/). 

## License
See [License](LICENSE) for more information.

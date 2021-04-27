"""Utility functions for handling text"""

# Standard library imports
import pathlib
import re
from dataclasses import dataclass
from importlib import resources
from typing import Union

# Third party imports
import requests

# Geo:N:G imports
from geong_common.log import logger

# RegExp used to recognize URLs
RE_URL_PROTOCOL = re.compile(r"https?://.+")


@dataclass
class URL:
    """Mirror some of the basic pathlib functionality for URLs"""

    url: str

    def __post_init__(self):
        """Initialize basic properties derived from the url"""
        if not RE_URL_PROTOCOL.match(self.url):
            raise ValueError(f"URL {self.url!r} should start with http/https")
        if self.url.count("/") == 2:
            self.url += "/"

        self.name = self.url.rpartition("/")[-1]
        self.stem, dot, suffix = self.name.rpartition(".")
        self.suffix = f"{dot}{suffix}"

        # Cache for downloaded content
        self._bytes = None

    @property
    def parent(self):
        cls = type(self)
        parent_str, slash, _ = self.url.strip("/").rpartition("/")
        if RE_URL_PROTOCOL.match(parent_str):
            return cls(f"{parent_str}{slash}")
        else:
            return self

    def __truediv__(self, other):
        """Use / to append a string at the end of the URL"""
        cls = type(self)
        slash = "" if self.url.endswith("/") or not other else "/"
        return cls(f"{self.url}{slash}{other}")

    def __str__(self):
        """Represent the URL using a pure string representation"""
        return self.url

    def joinpath(self, *args):
        """Append one or several strings at the end of the URL, separated by /"""
        parts = [p.strip("/") for p in args]
        return self / "/".join(parts)

    def resolve(self):
        """Resolving the URL is a no-op

        The corresponding pathlib method resolves a path to an absolute path.
        The analogy would be to convert a relative URL to a full URL. However,
        we don't support relative URLs yet.
        """
        return self

    def read_text(self, encoding="utf-8"):
        """Read the contents from the URL as text"""
        raw = self.read_bytes()
        return raw.decode(encoding=encoding)

    def read_bytes(self):
        """Read the contents from the URL as bytes"""
        if self._bytes is None:
            response = requests.get(self.url)
            if response:
                self._bytes = response.content
            else:
                logger.error(
                    f"GET request to {self.url} returned "
                    f"{response.status_code} {response.reason}"
                )
                self._bytes = f"Missing file: {self.name}".encode()

        return self._bytes


def get_url_or_asset(
    path: str, *path_parts, local_assets: str = "geong_common.assets"
) -> Union[URL, pathlib.Path]:
    """Seamlessly work with local assets and resources available online

    This is used to be able to inject assets without touching the source code.
    """
    if RE_URL_PROTOCOL.match(path):
        return URL(url=path).joinpath(*path_parts)
    else:
        # Try to read from the assets directory if no http/https protocol is given
        with resources.path(local_assets, "") as assets:
            return assets.joinpath(path, *path_parts)

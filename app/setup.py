"""Use setup.cfg for installation
This file is needed for legacy reasons to be able to do editable installs.
See
- https://setuptools.readthedocs.io/en/latest/setuptools.html#setup-cfg-only-projects
- https://snarky.ca/what-the-heck-is-pyproject-toml/

Install with

    $ python -m pip install -e .
"""

# Third party imports
import setuptools

setuptools.setup()

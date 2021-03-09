"""Handle configuration settings in Geo:N:G"""

# Standard library imports
import pathlib
from typing import List

# Third party imports
from pyconfs import Configuration


def read(cfg_name: str, *directories: pathlib.Path) -> Configuration:
    """Read one configuration from file

    Args:
        cfg_name:     Name of configuration, `.toml`-suffix is added
        directories:  Prioritized list of directories

    Returns:
        A configuration object
    """
    cfg = Configuration(cfg_name)
    for file_path in _config_paths(cfg_name, [pathlib.Path(d) for d in directories]):
        cfg.update_from_file(file_path)

    if not cfg:
        raise FileNotFoundError(
            f"Configuration {cfg_name!r} not found in {', '.join(directories)}"
        )

    return cfg


def _config_paths(cfg_name: str, directories: List[pathlib.Path]) -> pathlib.Path:
    """Yield all files that contain the given configuration"""
    file_names = (f"{cfg_name}.toml", f"{cfg_name}_local.toml")

    for file_name in file_names:
        for file_dir in directories:
            file_path = file_dir / file_name
            if file_path.exists():
                yield file_path
                break

# Standard library imports
import pathlib
from enum import Enum

# Third party imports
import pandas as pd
from azure.core.credentials import AccessToken
from azure.storage.blob import BlobServiceClient

# Geo:N:G imports
from api.config.validators import BlobSettings


class DatasetName(str, Enum):
    shallow = "shallow"
    deep = "deep"


class TableName(str, Enum):
    systems = "systems"
    complexes = "complexes"
    elements = "elements"


TABLE_FILE_MAPPING = {
    TableName.systems: "systems.json",
    TableName.complexes: "complexes.json",
    TableName.elements: "elements.json",
}


class CustomTokenCredential(object):
    def __init__(self, token: str):
        self.__token = token

    def get_token(self, *scopes, **kwargs):
        return AccessToken(self.__token, 1)


def get_blob(storage_url: str, container: str, filepath: str, token: str) -> bytes:
    """Download blob from Azure"""
    credential = CustomTokenCredential(token)
    blob_service_client = BlobServiceClient(storage_url, credential)
    blob_client = blob_service_client.get_blob_client(container, filepath)

    return blob_client.download_blob().readall()


def get_dataframe_from_blob(
    dataset: DatasetName,
    table: TableName,
    token: str,
    blob_settings: BlobSettings,
) -> pd.DataFrame:
    """Read from the data lake"""
    filepath = str(
        pathlib.PurePosixPath(blob_settings.folder_name)
        / dataset.value
        / TABLE_FILE_MAPPING[table]
    )
    blob = get_blob(blob_settings.storage_url, blob_settings.container, filepath, token)
    return pd.read_json(blob.decode("UTF-8"), orient="split")

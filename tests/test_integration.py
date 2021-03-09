# Standard library imports
import itertools
import json
import os
from time import sleep
from urllib.parse import parse_qs
from urllib.parse import urlparse

# Third party imports
import pandas as pd
import pytest
import requests
from azure.core.credentials import AccessToken
from azure.storage.blob import BlobServiceClient

API_ADDR = os.getenv("API_ADDR", "http://localhost:5000")
AUTHORITY = os.getenv("AUTHORITY", "http://localhost:8089/common")
AUDIENCE = os.getenv("AUDIENCE")
STORAGE_URL = os.getenv("STORAGE_URL")
FOLDER_NAME = os.getenv("FOLDER_NAME")


class CustomTokenCredential(object):
    def get_token(self, *scopes, **kwargs):
        r = requests.post(f"{AUTHORITY}/oauth2/v2.0/token")
        access_token = r.json()["access_token"]
        return AccessToken(access_token, 1)


def auth_header():
    r = requests.get(
        f"{AUTHORITY}/oauth2/v2.0/authorize?client_id={AUDIENCE}",
        headers={"content-type": "application/json"},
        allow_redirects=False,
    )
    token = parse_qs(urlparse(r.headers["location"]).fragment)["access_token"]

    return {"Authorization": f"Bearer {token[0]}"}


AUTH_HEADER = auth_header()


@pytest.fixture(scope="session")
def wait_a_sec():
    """
    Sometimes the api is not ready when the tests start
    Waits for up to 5 seconds
    """
    for _ in range(5):
        try:
            r = requests.get(f"{API_ADDR}/health", headers=AUTH_HEADER)
            if r.ok:
                return
        except requests.exceptions.ConnectionError:
            pass
        sleep(1)
    raise RuntimeError(f"Could not connect to {API_ADDR}/health")


def upload(blob_service_client, data, file_name):
    system_blob_client = blob_service_client.get_blob_client("dls", blob=file_name)
    system_blob_client.upload_blob(json.dumps(data))


@pytest.fixture
def create_dls(wait_a_sec):
    credential = CustomTokenCredential()
    blob_service_client = BlobServiceClient(STORAGE_URL, credential)
    try:
        blob_service_client.delete_container("dls")
    except Exception:
        pass
    blob_service_client.create_container("dls")

    dummy_data = pd.DataFrame.from_dict(
        {"key0": ["val00", "val01"], "key1": ["val10", "val11"]}
    ).to_dict(orient="split")

    for (data_set, file) in itertools.product(
        ["deep", "shallow"], ["systems", "complexes", "elements"]
    ):
        upload(
            blob_service_client,
            dummy_data,
            f"{FOLDER_NAME}/{data_set}/{file}.json",
        )

    yield dummy_data

    blob_service_client.delete_container("dls")


@pytest.mark.parametrize(
    ("dataset", "table"),
    itertools.product(["deep", "shallow"], ["systems", "complexes", "elements"]),
)
def test_all_data_endpoints_required(dataset, table, create_dls):
    r = requests.get(f"{API_ADDR}/data/{dataset}/{table}", headers=AUTH_HEADER)
    assert r

    assert r.json() == create_dls


def test_undefined_endpoints(wait_a_sec):
    r = requests.get(f"{API_ADDR}/data/undefined/undefined", headers=AUTH_HEADER)
    assert r.status_code == 422


def test_get_blob_not_found(wait_a_sec):
    r = requests.get(f"{API_ADDR}/data/deep/systems", headers=AUTH_HEADER)
    assert r.status_code == 500


def test_get_health(wait_a_sec):
    r = requests.get(f"{API_ADDR}/health")
    assert r


def test_filtered_data(create_dls):
    r = requests.get(
        f"{API_ADDR}/data/deep/systems?filters=key0%3Dval01", headers=AUTH_HEADER
    )
    assert r

    assert r.json()["data"] == [["val01", "val11"]]


def test_filtered_data_with_no_result(create_dls):
    r = requests.get(
        f"{API_ADDR}/data/deep/systems?filters=key0%3Dmissing_value",
        headers=AUTH_HEADER,
    )
    assert r

    assert r.json()["data"] == []

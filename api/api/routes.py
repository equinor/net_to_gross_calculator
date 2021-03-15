# Standard library imports
import sys
from functools import lru_cache
from typing import Dict
from typing import List
from typing import Optional

# Third party imports
import requests
from azure.core.exceptions import ResourceNotFoundError
from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Query
from fastapi import Security

# Geo:N:G imports
from api import config
from api.config.validators import BlobSettings
from api.config.validators import get_blob_settings
from api.config.validators import get_log_settings
from api.config.validators import get_oauth_settings
from api.data import DatasetName
from api.data import TableName
from api.data import get_dataframe_from_blob
from api.utils import oidc
from api.utils.auth import Oauth
from geong_common.data import models
from geong_common.log import logger

router = APIRouter()


@lru_cache
def get_oidc():
    try:
        return oidc.get_config(
            f"{get_oauth_settings().authority}/.well-known/openid-configuration"
        )
    except oidc.OidcError as e:
        sys.exit(f"{e}")


def as_dict(keyvalues: List[str] = Query(default=[])) -> Dict[str, str]:
    """Parse a list of strings on the form ['key1=value1', ...] into a dictionary"""
    return dict(kv.split("=", maxsplit=1) for kv in keyvalues if "=" in kv)


oauth = Oauth(get_oidc(), get_oauth_settings())


async def _user_department(token, url):
    r = requests.get(
        url,
        headers={"Authorization": f"Bearer {token}"},
    )
    if r.ok:
        return r.json().get("value")
    else:
        logger.error(f"user_department {url=}: {r.status_code}")


async def log_dep(token, session_id):
    if not get_log_settings().log_user_info:
        return
    user_token = await oauth.obo(token, scope="User.Read")
    dep = await _user_department(user_token, config.api.ms_graph.url)
    if dep is not None:
        logger.insights(f"Department: {dep}, SessionID: {session_id}")

    return None


@router.get("/data/{dataset}/{table}")
async def get_table(
    dataset: DatasetName,
    table: TableName,
    session_id: Optional[str] = "",
    filters: List[str] = Query(default=[]),
    token: Optional[str] = Security(oauth),
    blob_settings: BlobSettings = Depends(get_blob_settings),
):
    await log_dep(token, session_id)
    """Get Geo:N:G data from a given dataset and table"""
    try:
        geong_data = get_dataframe_from_blob(
            dataset,
            table,
            await oauth.obo(token),
            blob_settings,
        )
    except ResourceNotFoundError:
        raise HTTPException(status_code=500)
    return models.filter_data(geong_data, as_dict(filters)).to_dict(orient="split")


@router.get("/model/{dataset}")
async def run_model(
    dataset: DatasetName,
    session_id: Optional[str] = "",
    blob_settings: BlobSettings = Depends(get_blob_settings),
    token: Optional[str] = Security(oauth),
):
    """Run the model on the given dataset"""
    await log_dep(token, session_id)
    try:
        geong_data = get_dataframe_from_blob(
            dataset,
            TableName.elements,
            await oauth.obo(token),
            blob_settings,
        )
    except ResourceNotFoundError:
        raise HTTPException(status_code=500)
    return models.calculate(geong_data, dataset).to_dict(orient="split")

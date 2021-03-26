"""Read data from the API"""

# Third party imports
import pandas as pd
import panel as pn
import pyplugs
import requests

# Geo:N:G imports
from geong_common import config
from geong_common.data import composition
from geong_common.exceptions import APIResponseError
from geong_common.exceptions import MissingAccessTokenError
from geong_common.log import logger

# Read plugin configuration
*_, PACKAGE, PLUGIN = __name__.split(".")
CFG = config.geong[PACKAGE][PLUGIN]


@pyplugs.register
def read_all(dataset, table):
    """Read all data from the API, convert to pandas dataframe"""
    return _read_from_api(CFG.url.replace("data", dataset=dataset, table=table))


@pyplugs.register
def read_filtered(dataset, table, **filters):
    """Read filtered data from the API, convert to pandas dataframe"""
    return _read_from_api(
        request_url=CFG.url.replace("data", dataset=dataset, table=table),
        params={"filters": [f"{k}={v}" for k, v in filters.items()]},
    )


@pyplugs.register
def read_elements(dataset, base_table, **filters):
    """Get elements satisfying filters on base table

    TODO: Move more of this functionality to the API to avoid calling the API twice
    """
    # Filter to get wells
    wells = read_filtered(dataset=dataset, table=base_table, **filters)
    elements = read_all(dataset=dataset, table="elements")
    return composition.combine_scale_and_elements(base_table, wells, elements)


@pyplugs.register
def read_model(dataset):
    """Read the dataset models from the API, convert to pandas dataframe"""
    return _read_from_api(CFG.url.replace("model", dataset=dataset))


def _read_from_api(request_url, params: dict = None):
    """Handle one request to the API"""
    header = "X-Forwarded-Access-Token"
    access_token = pn.state.headers.get(header)

    if access_token is None:
        raise MissingAccessTokenError(
            user_message="Data service unavailable. Please try again later.",
            log_message=f"Missing {header} header",
        )

    try:
        session_id = pn.state.curdoc.session_context.id
        if params is not None:
            params["session_id"] = session_id
        else:
            params = {"session_id": session_id}
    except AttributeError as e:
        logger.error(f"SessionID not available: {e}")

    # Send a request to the API
    logger.debug(f"Sending GET {request_url} to API")
    response = requests.get(
        request_url,
        params=params,
        headers={"Authorization": f"bearer {access_token}"},
    )

    # Handle errors
    if not response:
        raise APIResponseError(
            user_message="Data service unavailable. Please try again later.",
            status_code=response.status_code,
            reason=response.reason,
        )

    # Convert to pandas dataframe
    return pd.DataFrame(**response.json())

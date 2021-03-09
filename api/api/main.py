# Third party imports
from fastapi import FastAPI

# Geo:N:G imports
from api import __version__
from api import routes
from api.config.validators import get_blob_settings
from api.config.validators import get_log_settings
from api.config.validators import get_oauth_settings
from geong_common.log import logger

# Call these here to trigger potential error at startup
get_blob_settings()
get_oauth_settings()
get_log_settings()


app = FastAPI()


@app.middleware("http")
async def log_x_real_ip(request, call_next):
    x_real_ip = request.headers.get("x-real-ip")
    response = await call_next(request)
    logger.info(f"{request.method} {request.url} {response.status_code} {x_real_ip=}")
    return response


app.include_router(routes.router)


@app.get("/health")
async def health():
    return ""


@app.get("/version")
async def version():
    return __version__

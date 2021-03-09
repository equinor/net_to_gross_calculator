# Third party imports
import jwt
import requests
from fastapi import HTTPException
from fastapi import Request
from fastapi import status
from fastapi.security import HTTPBearer

# Geo:N:G imports
from geong_common.log import logger


class Oauth(HTTPBearer):
    def __init__(self, oid_config, oauth_settings):
        super().__init__()
        self.oid_config = oid_config
        self.oauth_settings = oauth_settings

    async def __call__(self, request: Request):
        ac = await super().__call__(request)
        token = ac.credentials
        self.verify(token)
        return token

    def verify(self, token, decode=jwt.decode):
        try:
            jwt_header = jwt.get_unverified_header(token)
        except jwt.exceptions.DecodeError as e:
            logger.warning(f"{e}")
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
        kid = jwt_header.get("kid")
        if kid is None:
            logger.warning(f"{kid=}")
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
        key = self.oid_config.public_keys.get(kid)
        if key is None:
            logger.warning(f"{key=}")
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
        try:
            decode(
                jwt=token,
                key=key,
                issuer=self.oid_config.issuer,
                audience=self.oauth_settings.audience,
                algorithms=["RS256"],
            )
        except jwt.exceptions.PyJWTError as e:
            logger.warning(f"JWT decoding error: {e}")
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    async def obo(self, token, scope="https://storage.azure.com/user_impersonation"):

        data = (
            "grant_type=urn:ietf:params:oauth:grant-type:jwt-bearer"
            + f"&client_id={self.oauth_settings.client_id}"
            + f"&client_secret={self.oauth_settings.client_secret}"
            + f"&assertion={token}"
            + f"&scope={scope}"
            + "&requested_token_use=on_behalf_of"
        )
        headers = {"content-type": "application/x-www-form-urlencoded"}
        r = requests.post(
            self.oid_config.token_endpoint,
            str.encode(data),
            headers=headers,
        )
        if r.status_code != 200:
            logger.error(r.text)
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

        json = r.json()
        if json is None:
            logger.error("not a json response")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

        access_token = json.get("access_token")
        if access_token is None:
            logger.error("missing access_token")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

        return access_token

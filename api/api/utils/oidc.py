# Standard library imports
import json
from collections import namedtuple

# Third party imports
import jwt
import requests
from pydantic import BaseModel
from pydantic import parse_obj_as
from pydantic.error_wrappers import ValidationError


class OidcError(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return str(self.msg)


class Oid(BaseModel):
    jwks_uri: str
    token_endpoint: str
    issuer: str


def get_config(url: str) -> dict:
    try:
        r = requests.get(url)
    except requests.exceptions.ConnectionError:
        raise OidcError(f"Could not connect to oidc server: {url=}")
    if not r:
        raise OidcError(
            f"Could not get config from oidc server: {url=} {r.status_code=}"
        )
    try:
        m = parse_obj_as(Oid, r.json())
    except ValidationError as e:
        raise OidcError(str(e))

    jwks = requests.get(m.jwks_uri)
    if not jwks:
        raise RuntimeError("Could not get jwks")

    public_keys = {}
    keys = [key for key in jwks.json()["keys"] if key["kty"] == "RSA"]
    for jwk in keys:
        kid = jwk["kid"]
        public_keys[kid] = jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(jwk))

    Oidc = namedtuple("Oidc", ["public_keys", "token_endpoint", "issuer"])
    return Oidc(
        public_keys=public_keys, token_endpoint=m.token_endpoint, issuer=m.issuer
    )

# Standard library imports
from collections import namedtuple
from unittest.mock import Mock

# Third party imports
import pytest
from fastapi.exceptions import HTTPException

# Geo:N:G imports
from api.utils import auth


def test_missing_bearer():
    oauth = auth.Oauth(oid_config=None, oauth_settings=None)
    with pytest.raises(HTTPException) as e:
        oauth.verify("not.a.bearer")
    assert e.value.status_code == 403


def test_not_a_decodable_jwt():
    oauth = auth.Oauth(oid_config="", oauth_settings="")
    with pytest.raises(HTTPException) as e:
        oauth.verify("bearer this.is.an.invalid.token")
    assert e.value.status_code == 403


def test_token_without_kid():
    token_without_kid = """eyJhbGciOiJIUzI1NiJ9\
    .e30.ZRrHA1JJJW8opsbCGfG_HACGpVUMN_a9IV7pAx_Zmeo"""
    oauth = auth.Oauth(oid_config="", oauth_settings="")

    with pytest.raises(HTTPException) as e:
        oauth.verify(token_without_kid)
    assert e.value.status_code == 403


def test_public_keys_without_kid():
    Oidc = namedtuple("_", ["public_keys", "token_endpoint"])
    oid_config = Oidc(public_keys={"without 'id' as kid": ""}, token_endpoint="")
    token_without_kid = """eyJhbGciOiJIUzI1NiIsImtpZCI6ImlkIn0\
    .e30.rHWCMy2sWIp8pohPfD5Tx5QhjlJqPYlR6WAhVB8pmOI"""
    oauth = auth.Oauth(oid_config=oid_config, oauth_settings="")

    with pytest.raises(HTTPException) as e:
        oauth.verify(f"bearer {token_without_kid}")

    assert e.value.status_code == 403


def test_ok():
    mock = Mock()
    kid = "id"
    key = "some_key"
    audience = "some_audience"
    Oidc = namedtuple("_", ["public_keys", "token_endpoint", "issuer"])
    oid_config = Oidc(public_keys={kid: key}, token_endpoint="", issuer="")

    some_token = """eyJhbGciOiJIUzI1NiIsImtpZCI6ImlkIn0\
    .e30.rHWCMy2sWIp8pohPfD5Tx5QhjlJqPYlR6WAhVB8pmOI"""

    oauth_settings = namedtuple("_", ["audience"])(audience=audience)
    oauth = auth.Oauth(oid_config=oid_config, oauth_settings=oauth_settings)
    oauth.verify(some_token, decode=mock.method)

    mock.method.assert_called_with(
        jwt=some_token, key=key, audience=audience, algorithms=["RS256"], issuer=""
    )

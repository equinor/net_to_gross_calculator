# Third party imports
import pytest

# Geo:N:G imports
from api.utils import oidc


def test_disc_body_invalid(requests_mock):
    disc_url = "http://disc"
    requests_mock.get(disc_url, json={})
    with pytest.raises(oidc.OidcError):
        oidc.get_config(disc_url)


def test_jwks(requests_mock):
    disc_url = "http://disc"
    jwks_url = "http://jwks"

    disc_body = {"jwks_uri": jwks_url, "issuer": "", "token_endpoint": "endpoint"}
    key = {
        "e": "AQAB",
        "n": "2y6laZzXOPwGpMOhh0RcZq-Cng12HRv4EHT_Y6w5WOuNWZxzGFjF77qfTKtp_izFIGlr0IwJnbJsDqmTfAXdDMsfRXpWE6DZ6D0s49coNgu-nEFT7UdkuyfUnfPfU8lZLLzxB4fPp0CpUZIacZWb9Ci83dkqS6yEkppftf8bZOW1Cmz6SQuBbZgDyrm7hKBK8NxmSxJvnqUN6CDdOpxJdLSvIon8EUMcA0VEhNx0acgzZmjedZJEGWO6zs8jrRROkX0_fhpjW1BP4nq5OI6JpXMRgV6LuqCdmg9s3Qvw2k27baa97pxAJprMKwBnHSLcbrjkldREZgQ9NweYbLX-JQ",  # noqa
        "kty": "RSA",
        "kid": "5Of9P5F9gCCwCmF2BOHHxDDQ-Dk",
        "x5c": [
            "MIIDBTCCAe2gAwIBAgIQQiR8gZNKuYpH6cP+KIE5ijANBgkqhkiG9w0BAQsFADAtMSswKQYDVQQDEyJhY2NvdW50cy5hY2Nlc3Njb250cm9sLndpbmRvd3MubmV0MB4XDTIwMDgyODAwMDAwMFoXDTI1MDgyODAwMDAwMFowLTErMCkGA1UEAxMiYWNjb3VudHMuYWNjZXNzY29udHJvbC53aW5kb3dzLm5ldDCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBAMkymupuRhTpZc+6CBxQpL0SaAb+8CzLiiDyx2xRoecjojvKN2pKKjIX9cejMSDRoWaOnZCK4VZVX1iYRCWT1WkHb8r1ZpSGa7oXG89zxjKjwG46tiamwdZjJ7Mhh8fqLz9ApucY/LICPMJuu6d56LKs6hb4OpjylTvsNUAa+bHg1NgMFNg0fPCxdr9N2Y4J+Jhrz3VDl4oU0KDZX/pyRXblzA8kYGWm50dh5WB4WoB8MtW3lltVrRGj8/IgTf9GxpBsO9OWgwVByZHU7ctZs7AmUbq/59Ipql7vSM6EsoquXdMiq0QOcZAPitwzHkTKrmeULz0/RHnuBGXxS/e8wX0CAwEAAaMhMB8wHQYDVR0OBBYEFGcWXwaqmO25Blh2kHHAFrM/AS2CMA0GCSqGSIb3DQEBCwUAA4IBAQDFnKQ98CBnvVd4OhZP0KpaKbyDv93PGukE1ifWilFlWhvDde2mMv/ysBCWAR8AGSb1pAW/ZaJlMvqSN/+dXihcHzLEfKbCPw4/Mf2ikq4gqigt5t6hcTOSxL8wpe8OKkbNCMcU0cGpX5NJoqhJBt9SjoD3VPq7qRmDHX4h4nniKUMI7awI94iGtX/vlHnAMU4+8y6sfRQDGiCIWPSyypIWfEA6/O+SsEQ7vZ/b4mXlghUmxL+o2emsCI1e9PORvm5yc9Y/htN3Ju0x6ElHnih7MJT6/YUMISuyob9/mbw8Vf49M7H2t3AE5QIYcjqTwWJcwMlq5i9XfW2QLGH7K5i8"  # noqa
        ],
        "x5t": "5Of9P5F9gCCwCmF2BOHHxDDQ-Dk",
    }
    jwks_body = {
        "keys": [
            {
                **key,
            },
            {"kty": "oct", "use": "sig", "kid": "hmac", "k": "SECRET_2gtzk"},
        ]
    }
    requests_mock.get(disc_url, json=disc_body)
    requests_mock.get(jwks_url, json=jwks_body)

    config = oidc.get_config(disc_url)
    for k in ["public_keys", "token_endpoint"]:
        assert k in config._asdict().keys()

from typing import Annotated

import requests
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt
from jose.exceptions import ExpiredSignatureError, JWTClaimsError, JWTError
from sqlalchemy.orm import Session

from app import models
from app.deps.misc import get_db
from app.config import settings


def _get_auth_token(
    authorization: Annotated[HTTPAuthorizationCredentials, Depends(HTTPBearer())],
) -> str:
    """Get the auth token from the Authorization header."""
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    return authorization.credentials


def _validate_token(token: Annotated[str, Depends(_get_auth_token)]) -> dict:
    jsonurl = requests.get(f"https://{settings.AUTH0_DOMAIN}/.well-known/jwks.json")
    jwks = jsonurl.json()

    try:
        unverified_header = jwt.get_unverified_header(token)
    except JWTError:
        raise HTTPException(status_code=401, detail="Error decoding token headers.")

    rsa_key = {}
    for key in jwks["keys"]:
        if key["kid"] == unverified_header["kid"]:
            rsa_key = {
                "kty": key["kty"],
                "kid": key["kid"],
                "use": key["use"],
                "n": key["n"],
                "e": key["e"],
            }

    if rsa_key:
        try:
            claims = jwt.decode(
                token,
                rsa_key,
                algorithms=settings.ALGORITHMS,
                audience=settings.API_AUDIENCE,
                issuer=f"https://{settings.AUTH0_DOMAIN}/",
            )
        except ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token is expired")
        except JWTClaimsError:
            raise HTTPException(
                status_code=401, detail="Invalid claims. Check the audience and issuer"
            )
        except Exception:
            raise HTTPException(
                status_code=401, detail="Unable to parse authentication token."
            )

        return claims

    raise HTTPException(status_code=401, detail="Unable to find appropriate key.")


def authenticate(
    claims: Annotated[str, Depends(_validate_token)],
    db: Annotated[Session, Depends(get_db)],
) -> models.User:
    sub = claims.get("sub")
    user = models.User.get_or_404(db, auth0_sub=sub)
    return user

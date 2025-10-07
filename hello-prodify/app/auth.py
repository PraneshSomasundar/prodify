from fastapi import Header, HTTPException, status
from typing import Optional

from google.oauth2 import id_token
from google.auth.transport import requests

# Your Identity Platform / Firebase audience is your PROJECT ID
PROJECT_ID = "prodify-474400"

def verify_bearer_token(authorization: Optional[str] = Header(None)) -> dict:
    """
    Expect header: Authorization: Bearer <ID_TOKEN>
    Returns decoded claims if valid, otherwise raises 401.
    """
    if not authorization:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing Authorization header")

    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Use Bearer <token>")

    token = parts[1]

    try:
        # Verifies signature and checks aud/iss for Identity Platform (securetoken)
        claims = id_token.verify_firebase_token(token, requests.Request(), audience=PROJECT_ID)
        if not claims:
            raise ValueError("Invalid token")
        return claims
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Invalid token: {e}")


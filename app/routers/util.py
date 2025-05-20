from typing import Annotated
from fastapi import Cookie, HTTPException
from fastapi.responses import JSONResponse
from jose import jwt
from app.database.connection import get_user_by_email
from app.config import Config


config = Config()


def get_verified_user_email(
    authorization: Annotated[str | None, Cookie(alias="Authorization")] = None,
):
    if not authorization:
        raise HTTPException(
            status_code=412, detail="You need to be logged in to access this resource"
        )

    token = authorization.split(" ")[1]
    try:
        email = jwt.decode(token, config.session_secret_key, algorithms=["HS256"]).get(
            "sub"
        )
    except jwt.JWTError:
        # TODO: handle different types of errors - invalid or expired. Right now we simply logout
        raise HTTPException(
            status_code=401,
            detail="Invalid token",
            headers={
                "Set-Cookie": "Authorization=; Path=/; Expires=Thu, 01 Jan 1970 00:00:00 GMT"
            },
        )

    return email

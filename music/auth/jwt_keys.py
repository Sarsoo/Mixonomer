from datetime import timedelta, datetime, timezone
import jwt
from music.magic_strings import JWT_SECRET_URI
from music.model.user import User

from google.cloud import secretmanager

secret_client = secretmanager.SecretManagerServiceClient()


def get_jwt_secret_key() -> str:
    return secret_client.access_secret_version(request={"name": JWT_SECRET_URI}).payload.data.decode("UTF-8")


def generate_key(user: User, timeout: datetime | timedelta = timedelta(minutes=60)) -> str:

    if isinstance(timeout, timedelta):
        exp = timeout + datetime.now(tz=timezone.utc)
    else:
        exp = timeout

    payload = {
        "exp": exp,
        "iss": "mixonomer-api",
        "sub": user.username
    }

    return jwt.encode(payload, get_jwt_secret_key(), algorithm="HS512")


def validate_key(key: str) -> dict:

    try:
        decoded = jwt.decode(key, get_jwt_secret_key(), algorithms=["HS512"], options={
            "require": ["exp", "sub"]
        })

        return decoded

    except jwt.exceptions.PyJWTError as e:
        pass

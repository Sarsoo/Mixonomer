from ctypes import Union
from datetime import timedelta, datetime, timezone
import jwt
from music.model.user import User
from music.model.config import Config

def get_jwt_secret_key() -> str:

    config = Config.collection.get("config/music-tools")
    
    if config.jwt_secret_key is None or len(config.jwt_secret_key) == 0:
        raise KeyError("no jwt secret key found")

    return config.jwt_secret_key

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

    except Exception as e:
        pass

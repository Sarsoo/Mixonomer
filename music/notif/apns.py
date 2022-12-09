import json

from music.magic_strings import APNS_SIGN_URI
from music.model.config import Config

from datetime import datetime, timedelta

from google.cloud import secretmanager

import httpx
import jwt
import os

secret_client = secretmanager.SecretManagerServiceClient()

DEV_SERVER = "https://api.sandbox.push.apple.com"
PROD_SERVER = "https://api.push.apple.com"


def get_url(device_token: str) -> str:

    # if os.environ.get('DEPLOY_DESTINATION', None) == 'PROD':
    #     url = PROD_SERVER
    # else:
    #     url = DEV_SERVER

    return DEV_SERVER + '/3/device/' + device_token


def get_secret() -> str:
    return secret_client.access_secret_version(request={"name": APNS_SIGN_URI}).payload.data.decode("UTF-8")


def get_token():
    config = Config.collection.get("config/music-tools")

    # top_hour = int(datetime.utcnow().replace(minute=0, second=0, microsecond=0).timestamp()) # for
    top_hour = int(datetime.utcnow().timestamp())

    payload = {
        "iss": config.apns_team_id,
        "iat": top_hour
    }

    secret = get_secret()

    return jwt.encode(payload, secret, algorithm="ES256", headers={"kid": config.apns_key_id, "typ": None})


def send_notification(
        device_token: str,
        alert: dict | str = None,
        badge: int = None,
        expiry: int = None,
        priority: int = None
):

    payload = {
        "aps": {

        }
    }

    if alert:
        payload['aps']['alert'] = alert

    if badge is not None:
        payload['aps']['badge'] = badge

    headers = {
        'authorization': 'bearer ' + get_token(),
        'apns-push-type': 'alert',
        'apns-topic': 'xyz.sarsoo.Mixonomer',
        'content-type': 'application/x-www-form-urlencoded',
        'apns-priority': '10'
    }

    if expiry is not None:
        if expiry == 0:
            headers['apns-expiration'] = '0'
        else:
            headers['apns-expiration'] = str(int((datetime.utcnow() + timedelta(seconds=expiry)).timestamp()))
    else:
        headers['apns-expiration'] = str(int((datetime.utcnow() + timedelta(hours=6)).timestamp()))

    if priority is not None:
        headers['apns-priority'] = str(priority)

    client = httpx.Client(http2=True)
    url = get_url(device_token)

    resp = client.post(url=url,
                       content=json.dumps(payload),
                       headers=headers)

    return resp

import os
project_id = os.environ.get('GOOGLE_CLOUD_PROJECT')

SPOT_CLIENT_URI = f"projects/{project_id}/secrets/spotify-client/versions/latest"
SPOT_SECRET_URI = f"projects/{project_id}/secrets/spotify-secret/versions/latest"
LASTFM_CLIENT_URI = f"projects/{project_id}/secrets/lastfm-client/versions/latest"
JWT_SECRET_URI = f"projects/{project_id}/secrets/jwt-secret/versions/latest"
COOKIE_SECRET_URI = f"projects/{project_id}/secrets/cookie-secret/versions/latest"
APNS_SIGN_URI = f"projects/{project_id}/secrets/apns-auth-sign-key/versions/1"

STATIC_BUCKET = f'{project_id}-static'
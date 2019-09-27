from spotframework.net.user import NetworkUser


class DatabaseUser(NetworkUser):

    def __init__(self, client_id, client_secret, refresh_token, user_id, access_token=None):
        super().__init__(client_id=client_id, client_secret=client_secret,
                         refresh_token=refresh_token, access_token=access_token)
        self.user_id = user_id

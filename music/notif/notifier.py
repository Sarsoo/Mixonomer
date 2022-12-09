from .apns import send_notification
from music.model.user import User
from music.model.playlist import Playlist
from music.model.tag import Tag
import logging


logger = logging.getLogger(__name__)


def notify_user_playlist_update(user: User, playlist: Playlist):

    if user.notify_playlist_updates:
        notify_user(user=user, alert={
            "title": "Playlist Updated",
            "body": f"{playlist.name} was just updated"
        }, priority=1)


def notify_user_tag_update(user: User, tag: Tag):

    if user.notify_tag_updates:
        notify_user(user=user, alert={
            "title": "Tag Updated",
            "body": f"{tag.name} was just updated"
        }, priority=1)


def notify_admin_new_user(user: User, new_username: str):

    if user.notify_admins:
        notify_user(user=user, alert={
            "title": "New User",
            "body": f"{new_username} just created an account"
        })


def notify_user(user: User,
                alert: dict | str = None,
                badge: int = None,
                expiry: int = None,
                priority: int = None):

    if user.apns_tokens:
        logger.debug(f"notifying {user.username}")

        stale_tokens = []
        for device in user.apns_tokens:
            resp = send_notification(device_token=device,
                                     alert=alert,
                                     badge=badge,
                                     expiry=expiry,
                                     priority=priority)

            if 400 <= resp.status_code < 600:
                logger.warning(f'http error when notifying {user.username}: {resp.content}')

                if resp.status_code == 410:
                    logger.warning(f'http error 410 when notifying {user.username}: removing stale token')
                    stale_tokens += [device]

        if len(stale_tokens) > 0:
            user.apns_tokens = [i for i in user.apns_tokens if i not in stale_tokens]
            user.update()

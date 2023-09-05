import logging
import os
from google.cloud import pubsub_v1

publisher = pubsub_v1.PublisherClient()
logger = logging.getLogger(__name__)


def update_tag(username: str, tag_id: str) -> None:
    """Queue serverless tag update for user

    Args:
        username (str): Subject username
        tag_id (str): Subject tag ID
    """

    logger.info(f'queuing {tag_id} update for {username}')

    if username is None or tag_id is None:
        logger.error(f'less than two args provided, {username} / {tag_id}')
        return

    if not isinstance(username, str) or not isinstance(tag_id, str):
        logger.error(f'less than two strings provided, {type(username)} / {type(tag_id)}')
        return

    publisher.publish(f'projects/{os.environ["GOOGLE_CLOUD_PROJECT"]}/topics/update_tag', b'', tag_id=tag_id, username=username)


def run_user_playlist_function(username: str, playlist_name: str) -> None:
    """Queue serverless playlist update for user

    Args:
        username (str): Subject username
        playlist_name (str): Subject tag ID
    """

    logger.info(f'queuing {playlist_name} update for {username}')

    if username is None or playlist_name is None:
        logger.error(f'less than two args provided, {username} / {playlist_name}')
        return

    if not isinstance(username, str) or not isinstance(playlist_name, str):
        logger.error(f'less than two strings provided, {type(username)} / {type(playlist_name)}')
        return

    publisher.publish(f'projects/{os.environ["GOOGLE_CLOUD_PROJECT"]}/topics/run_user_playlist', b'', name=playlist_name, username=username)

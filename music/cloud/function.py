import logging
from google.cloud import pubsub_v1

publisher = pubsub_v1.PublisherClient()
logger = logging.getLogger(__name__)


def update_tag(username, tag_id):
    """Queue serverless tag update for user"""
    logger.info(f'queuing {tag_id} update for {username}')

    if username is None or tag_id is None:
        logger.error(f'less than two args provided, {username} / {tag_id}')
        return

    if not isinstance(username, str) or not isinstance(tag_id, str):
        logger.error(f'less than two strings provided, {type(username)} / {type(tag_id)}')
        return

    publisher.publish('projects/sarsooxyz/topics/update_tag', b'', tag_id=tag_id, username=username)


def run_user_playlist_function(username, playlist_name):
    """Queue serverless playlist update for user"""
    logger.info(f'queuing {playlist_name} update for {username}')

    if username is None or playlist_name is None:
        logger.error(f'less than two args provided, {username} / {playlist_name}')
        return

    if not isinstance(username, str) or not isinstance(playlist_name, str):
        logger.error(f'less than two strings provided, {type(username)} / {type(playlist_name)}')
        return

    publisher.publish('projects/sarsooxyz/topics/run_user_playlist', b'', name=playlist_name, username=username)

import logging
from google.cloud import pubsub_v1

publisher = pubsub_v1.PublisherClient()
logger = logging.getLogger(__name__)


def update_tag(username, tag_id):
    """Queue serverless tag update for user"""
    logger.info(f'queuing {tag_id} update for {username}')

    if username is None:
        logger.error(f'no username provided')
        return

    if tag_id is None:
        logger.error(f'no tag_id provided for {username}')
        return

    publisher.publish('projects/sarsooxyz/topics/update_tag', b'', tag_id=tag_id, username=username)

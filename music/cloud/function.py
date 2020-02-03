import logging
from google.cloud import pubsub_v1

publisher = pubsub_v1.PublisherClient()
logger = logging.getLogger(__name__)


def update_tag(username, tag_id):
    logger.info(f'queuing {tag_id} update for {username}')
    publisher.publish('projects/sarsooxyz/topics/update_tag', b'', tag_id=tag_id, username=username)

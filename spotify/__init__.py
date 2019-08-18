from .spotify import app

import logging
import os

logger = logging.getLogger(__name__)
logger.setLevel('DEBUG')

if os.environ.get('DEPLOY_DESTINATION', None) == 'PROD':
    from google.cloud import logging as glogging

    log_format = '%(funcName)s - %(message)s'
    formatter = logging.Formatter(log_format)

    client = glogging.Client()
    handler = client.get_default_handler()

    handler.setFormatter(formatter)

    logger.addHandler(handler)

else:
    log_format = '%(levelname)s %(name)s:%(funcName)s - %(message)s'
    formatter = logging.Formatter(log_format)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    logger.addHandler(stream_handler)

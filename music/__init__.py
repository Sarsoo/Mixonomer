"""Root module containing Mixonomer backend

Top level module with functions for creating app with loaded blueprints and initialising the logging stack

"""

import logging
import os

logger = logging.getLogger(__name__)
logger.setLevel('DEBUG')

spotframework_logger = logging.getLogger('spotframework')
fmframework_logger = logging.getLogger('fmframework')
spotfm_logger = logging.getLogger('spotfm')


def init_log(cloud=False, console=False):
    if cloud:
        import google.cloud.logging
        from google.cloud.logging.handlers import CloudLoggingHandler

        log_format = '%(funcName)s - %(message)s'
        formatter = logging.Formatter(log_format)

        client = google.cloud.logging.Client()
        handler = CloudLoggingHandler(client, name="music-tools")

        handler.setFormatter(formatter)

        logger.addHandler(handler)
        spotframework_logger.addHandler(handler)
        fmframework_logger.addHandler(handler)
        spotfm_logger.addHandler(handler)

    if console:
        log_format = '%(levelname)s %(name)s:%(funcName)s - %(message)s'
        formatter = logging.Formatter(log_format)

        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)

        logger.addHandler(stream_handler)
        spotframework_logger.addHandler(stream_handler)
        fmframework_logger.addHandler(stream_handler)
        spotfm_logger.addHandler(stream_handler)


if os.environ.get('DEPLOY_DESTINATION', None) == 'PROD':
    init_log(cloud=True)

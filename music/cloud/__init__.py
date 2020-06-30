import logging

from music.model.config import Config
from music.tasks.run_user_playlist import run_user_playlist as run_now
from .function import run_user_playlist_function
from .tasks import run_user_playlist_task

logger = logging.getLogger(__name__)


def queue_run_user_playlist(username: str, playlist_name: str):
    config = Config.collection.get("config/music-tools")

    if config is None:
        logger.error(f'no config object returned, passing to cloud function {username} / {playlist_name}')
        run_user_playlist_function(username=username, playlist_name=playlist_name)

    if config.playlist_cloud_operating_mode == 'task':
        logger.debug(f'passing {username} / {playlist_name} to cloud tasks')
        run_user_playlist_task(username=username, playlist_name=playlist_name)

    elif config.playlist_cloud_operating_mode == 'function':
        logger.debug(f'passing {username} / {playlist_name} to cloud function')
        run_user_playlist_function(username=username, playlist_name=playlist_name)

    else:
        logger.critical(f'invalid operating mode {username} / {playlist_name}, '
                        f'{config.playlist_cloud_operating_mode}, passing to cloud function')
        run_user_playlist_function(username=username, playlist_name=playlist_name)


def offload_or_run_user_playlist(username: str, playlist_name: str):
    config = Config.collection.get("config/music-tools")

    if config is None:
        logger.error(f'no config object returned, passing to cloud function {username} / {playlist_name}')
        run_user_playlist_function(username=username, playlist_name=playlist_name)

    if config.playlist_cloud_operating_mode == 'task':
        run_now(username=username, playlist_name=playlist_name)

    elif config.playlist_cloud_operating_mode == 'function':
        logger.debug(f'offloading {username} / {playlist_name} to cloud function')
        run_user_playlist_function(username=username, playlist_name=playlist_name)

    else:
        logger.critical(f'invalid operating mode {username} / {playlist_name}, '
                        f'{config.playlist_cloud_operating_mode}, passing to cloud function')
        run_user_playlist_function(username=username, playlist_name=playlist_name)

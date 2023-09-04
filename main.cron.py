from cloudevents.http import CloudEvent
import functions_framework

from music.cloud.tasks import update_all_user_playlists, refresh_all_user_playlist_stats, update_all_user_tags


@functions_framework.cloud_event
def run_all_playlists(event: CloudEvent):
    update_all_user_playlists()


@functions_framework.cloud_event
def run_all_playlist_stats(event: CloudEvent):
    refresh_all_user_playlist_stats()


@functions_framework.cloud_event
def run_all_tags(event: CloudEvent):
    update_all_user_tags()

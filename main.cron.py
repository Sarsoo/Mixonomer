from music.cloud.tasks import update_all_user_playlists, refresh_all_user_playlist_stats, update_all_user_tags


def run_all_playlists(event, context):
    update_all_user_playlists()


def run_all_playlist_stats(event, context):
    refresh_all_user_playlist_stats()


def run_all_tags(event, context):
    update_all_user_tags()

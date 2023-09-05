from cloudevents.http import CloudEvent
import functions_framework

# Register a CloudEvent function with the Functions Framework
@functions_framework.cloud_event
def run_user_playlist(event: CloudEvent):
    import logging

    logger = logging.getLogger('music')

    attr = event.get_data()['message']['attributes']
    if 'username' in attr and 'name' in attr:

        from music.tasks.run_user_playlist import run_user_playlist as do_run_user_playlist
        do_run_user_playlist(user=attr['username'], playlist=attr["name"])

    else:
        logger.error('no parameters in event attributes')

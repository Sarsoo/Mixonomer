def run_user_playlist(event, context):
    import logging

    logger = logging.getLogger('music')

    if event.get('attributes'):
        if 'username' in event['attributes'] and 'name' in event['attributes']:

            from music.tasks.run_user_playlist import run_user_playlist as do_run_user_playlist
            do_run_user_playlist(user=event['attributes']['username'], playlist=event['attributes']["name"])

        else:
            logger.error('no parameters in event attributes')
    else:
        logger.error('no attributes in event')

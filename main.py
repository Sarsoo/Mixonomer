from music import app
from music.tasks.update_tag import update_tag as do_update_tag

app = app


def update_tag(event, context):
    import logging

    logger = logging.getLogger('music')

    if event.get('attributes'):
        if 'username' in event['attributes'] and 'tag_id' in event['attributes']:
            do_update_tag(username=event['attributes']['username'], tag_id=event['attributes']["tag_id"])
        else:
            logger.error('no parameters in event attributes')
    else:
        logger.error('no attributes in event')


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)

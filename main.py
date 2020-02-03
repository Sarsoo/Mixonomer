from music import app
from music.tasks.update_tag import update_tag as do_update_tag

app = app


def update_tag(event, context):
    import base64
    import logging
    import json

    logger = logging.getLogger('music')

    if 'data' in event:
        body = json.loads(base64.b64decode(event['data']).decode('utf-8'))

        if 'username' not in body or 'tag_id' not in body:
            logger.error('malformed body')
            return

        do_update_tag(username=body["username"], tag_id=body["tag_id"])
    else:
        logger.error('no data in event')


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)

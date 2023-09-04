from cloudevents.http import CloudEvent
import functions_framework

# Register a CloudEvent function with the Functions Framework
@functions_framework.cloud_event
def update_tag(event: CloudEvent):
    import logging

    logger = logging.getLogger('music')

    attr = event.get_data()['message']['attributes']

    if 'username' in attr and 'tag_id' in attr:

        from music.tasks.update_tag import update_tag as do_update_tag
        do_update_tag(user=attr['username'], tag=attr["tag_id"])

    else:
        logger.error('no parameters in event attributes')

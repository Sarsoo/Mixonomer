from flask import Blueprint, jsonify

import logging
from datetime import datetime

from google.cloud import tasks_v2

from music.api.decorators import login_or_jwt, admin_required, no_locked_users

blueprint = Blueprint('admin-api', __name__)

tasker = tasks_v2.CloudTasksClient()
task_path = tasker.queue_path('sarsooxyz', 'europe-west2', 'spotify-executions')

logger = logging.getLogger(__name__)


@blueprint.route('/tasks', methods=['GET'])
@login_or_jwt
@admin_required
@no_locked_users
def get_tasks(auth=None, user=None):

    tasks = list(tasker.list_tasks(parent=task_path))

    urls = {}
    for task in tasks:
        if urls.get(task.app_engine_http_request.relative_uri):
            urls[task.app_engine_http_request.relative_uri] += 1
        else:
            urls[task.app_engine_http_request.relative_uri] = 1

    response = {
        'tasks': [{
            'url': i,
            'count': j,
            'scheduled_times': [datetime.fromtimestamp(k.schedule_time.seconds) for k in tasks
                                if k.app_engine_http_request.relative_uri == i]
        } for i, j in urls.items()],
        'total_tasks': len(tasks),
    }
    return jsonify(response), 200

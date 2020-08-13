from flask import Blueprint, jsonify, request

import logging
import os
import json

from music.api.decorators import login_or_basic_auth, gae_cron, cloud_task
from music.cloud.function import update_tag as serverless_update_tag
from music.cloud.tasks import update_all_user_tags
from music.tasks.update_tag import update_tag

from music.model.tag import Tag

blueprint = Blueprint('task', __name__)
logger = logging.getLogger(__name__)


@blueprint.route('/tag', methods=['GET'])
@login_or_basic_auth
def tags(user=None):
    logger.info(f'retrieving tags for {user.username}')
    return jsonify({
        'tags': [i.to_dict() for i in Tag.collection.parent(user.key).fetch()]
    }), 200


@blueprint.route('/tag/<tag_id>', methods=['GET', 'PUT', 'POST', "DELETE"])
@login_or_basic_auth
def tag_route(tag_id, user=None):
    if request.method == 'GET':
        return get_tag(tag_id, user)
    elif request.method == 'PUT':
        return put_tag(tag_id, user)
    elif request.method == 'POST':
        return post_tag(tag_id, user)
    elif request.method == 'DELETE':
        return delete_tag(tag_id, user)


def get_tag(tag_id, user):
    logger.info(f'retrieving {tag_id} for {user.username}')

    db_tag = Tag.collection.parent(user.key).filter('tag_id', '==', tag_id).get()
    if db_tag is not None:
        return jsonify({
            'tag': db_tag.to_dict()
        }), 200
    else:
        return jsonify({"error": 'tag not found'}), 404


def put_tag(tag_id, user):
    logger.info(f'updating {tag_id} for {user.username}')

    db_tag = Tag.collection.parent(user.key).filter('tag_id', '==', tag_id).get()

    if db_tag is None:
        return jsonify({"error": 'tag not found'}), 404

    request_json = request.get_json()

    if request_json.get('name'):
        db_tag.name = request_json['name'].strip()

    if request_json.get('time_objects') is not None:
        db_tag.time_objects = request_json['time_objects']

    if request_json.get('tracks') is not None:
        db_tag.tracks = [
            {
                'name': track['name'].strip(),
                'artist': track['artist'].strip()
            }
            for track in request_json['tracks']
            if track.get('name') and track.get('artist')
        ]

    if request_json.get('albums') is not None:
        db_tag.albums = [
            {
                'name': album['name'].strip(),
                'artist': album['artist'].strip()
            }
            for album in request_json['albums']
            if album.get('name') and album.get('artist')
        ]

    if request_json.get('artists') is not None:
        db_tag.artists = [
            {
                'name': artist['name'].strip()
            }
            for artist in request_json['artists']
            if artist.get('name')
        ]

    db_tag.update()

    return jsonify({"message": 'tag updated', "status": "success"}), 200


def post_tag(tag_id, user):
    logger.info(f'creating {tag_id} for {user.username}')

    tag_id = tag_id.replace(' ', '_').strip()

    existing_ids = [i.tag_id for i in Tag.collection.parent(user.key).fetch()]
    while tag_id in existing_ids:
        tag_id += '_'

    tag = Tag(parent=user.key)
    tag.tag_id = tag_id
    tag.name = tag_id
    tag.username = user.username
    tag.save()

    return jsonify({"message": 'tag added', "status": "success"}), 201


def delete_tag(tag_id, user):
    logger.info(f'deleting {tag_id} for {user.username}')

    db_tag = Tag.collection.parent(user.key).filter('tag_id', '==', tag_id).get()
    Tag.collection.parent(user.key).delete(key=db_tag.key)

    return jsonify({"message": 'tag deleted', "status": "success"}), 201


@blueprint.route('/tag/<tag_id>/update', methods=['GET'])
@login_or_basic_auth
def tag_refresh(tag_id, user=None):
    logger.info(f'updating {tag_id} tag for {user.username}')

    if os.environ.get('DEPLOY_DESTINATION', None) == 'PROD':
        serverless_update_tag(username=user.username, tag_id=tag_id)
    else:
        update_tag(username=user.username, tag_id=tag_id)

    return jsonify({"message": 'tag updated', "status": "success"}), 200


@blueprint.route('/tag/update/task', methods=['POST'])
@cloud_task
def run_tag_task():

    payload = request.get_data(as_text=True)
    if payload:
        payload = json.loads(payload)

        logger.info(f'running {payload["username"]} / {payload["tag_id"]}')

        serverless_update_tag(username=payload['username'], tag_id=payload['tag_id'])

        return jsonify({'message': 'executed playlist', 'status': 'success'}), 200


@blueprint.route('/tag/update/users/cron', methods=['GET'])
@gae_cron
def run_tags_cron():

    update_all_user_tags()
    return jsonify({'status': 'success'}), 200

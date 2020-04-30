from flask import Blueprint, jsonify, request

import logging

from music.api.decorators import login_or_basic_auth
from music.cloud.function import update_tag

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
    logger.info(f'retriving {tag_id} for {user.username}')

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
        db_tag.name = request_json['name']

    update_required = False

    tracks = []
    if request_json.get('tracks') is not None:
        update_required = True
        for track in request_json['tracks']:
            if track.get('name') and track.get('artist'):
                tracks.append({
                    'name': track['name'],
                    'artist': track['artist']
                })
        db_tag.tracks = tracks

    albums = []
    if request_json.get('albums') is not None:
        update_required = True
        for album in request_json['albums']:
            if album.get('name') and album.get('artist'):
                albums.append({
                    'name': album['name'],
                    'artist': album['artist']
                })
        db_tag.albums = albums

    artists = []
    if request_json.get('artists') is not None:
        update_required = True
        for artist in request_json['artists']:
            if artist.get('name'):
                artists.append({
                    'name': artist['name']
                })
        db_tag.artists = artists

    if update_required:
        update_tag(username=user.username, tag_id=tag_id)

    db_tag.update()
    return jsonify({"message": 'tag updated', "status": "success"}), 200


def post_tag(tag_id, user):
    logger.info(f'creating {tag_id} for {user.username}')

    tag_id = tag_id.replace(' ', '_')

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
    update_tag(username=user.username, tag_id=tag_id)
    return jsonify({"message": 'tag updated', "status": "success"}), 200

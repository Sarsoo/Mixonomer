from flask import Blueprint, jsonify, request

import logging

from google.cloud import pubsub_v1

import music.db.database as database
from music.api.decorators import login_or_basic_auth

blueprint = Blueprint('task', __name__)
logger = logging.getLogger(__name__)

publisher = pubsub_v1.PublisherClient()


@blueprint.route('/tag', methods=['GET'])
@login_or_basic_auth
def tags(username=None):
    logger.info(f'retrieving tags for {username}')
    return jsonify({
        'tags': [i.to_dict() for i in database.get_user_tags(username)]
    }), 200


@blueprint.route('/tag/<tag_id>', methods=['GET', 'PUT', 'POST', "DELETE"])
@login_or_basic_auth
def tag(tag_id, username=None):
    if request.method == 'GET':
        return put_tag(tag_id, username)
    elif request.method == 'PUT':
        return put_tag(tag_id, username)
    elif request.method == 'POST':
        return post_tag(tag_id, username)
    elif request.method == 'DELETE':
        return delete_tag(tag_id, username)


def get_tag(tag_id, username):
    logger.info(f'retriving {tag_id} for {username}')

    db_tag = database.get_tag(username=username, tag_id=tag_id)
    if db_tag is not None:
        return jsonify({
            'tag': db_tag.to_dict()
        }), 200
    else:
        return jsonify({"error": 'tag not found'}), 404


def put_tag(tag_id, username):
    logger.info(f'updating {tag_id} for {username}')

    db_tag = database.get_tag(username=username, tag_id=tag_id)

    if db_tag is None:
        return jsonify({"error": 'tag not found'}), 404

    request_json = request.get_json()

    if request_json.get('name'):
        db_tag.name = request_json['name']

    update_required = False

    tracks = []
    if request_json.get('tracks'):
        update_required = True
        for track in request_json['tracks']:
            if track.get('name') and track.get('artist'):
                tracks.append({
                    'name': track['name'],
                    'artist': track['artist']
                })
    db_tag.tracks = tracks

    albums = []
    if request_json.get('albums'):
        update_required = True
        for album in request_json['albums']:
            if album.get('name') and album.get('artist'):
                albums.append({
                    'name': album['name'],
                    'artist': album['artist']
                })
    db_tag.album = albums

    artists = []
    if request_json.get('artists'):
        update_required = True
        for artist in request_json['tracks']:
            if artist.get('name') and artist.get('artist'):
                artists.append({
                    'name': artist['name']
                })
    db_tag.artists = artists

    if update_required:
        update_tag(username=username, tag_id=tag_id)

    return jsonify({"message": 'tag updated', "status": "success"}), 200


def post_tag(tag_id, username):
    logger.info(f'creating {tag_id} for {username}')

    new_tag = database.create_tag(username=username, tag_id=tag_id)
    if new_tag is not None:
        return jsonify({"message": 'tag added', "status": "success"}), 201
    else:
        return jsonify({"error": 'tag not created'}), 400


def delete_tag(tag_id, username):
    logger.info(f'deleting {tag_id} for {username}')

    response = database.delete_tag(username=username, tag_id=tag_id)

    if response is not None:
        return jsonify({"message": 'tag deleted', "status": "success"}), 201
    else:
        return jsonify({"error": 'tag not deleted'}), 400


def update_tag(username, tag_id):
    logger.info(f'queuing {tag_id} update for {username}')

    publisher.publish('projects/sarsooxyz/topics/update_tag', b'', tag_id=tag_id, username=username)

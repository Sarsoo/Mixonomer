from flask import Blueprint, jsonify
from datetime import date
import logging

from music.api.decorators import login_or_jwt, lastfm_username_required, no_locked_users

import music.db.database as database

blueprint = Blueprint('fm-api', __name__)
logger = logging.getLogger(__name__)


@blueprint.route('/today', methods=['GET'])
@login_or_jwt
@no_locked_users
@lastfm_username_required
def daily_scrobbles(auth=None, user=None):

    net = database.get_authed_lastfm_network(user)

    total = net.count_scrobbles_from_date(input_date=date.today())

    return jsonify({
        'username': net.username,
        'scrobbles_today': total
    }), 200

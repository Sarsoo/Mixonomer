from flask import Blueprint, session, flash, request, redirect, url_for
from google.cloud import firestore
from werkzeug.security import check_password_hash

blueprint = Blueprint('authapi', __name__)

db = firestore.Client()


@blueprint.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        session.pop('username', None)

        username = request.form['username'].lower()
        password = request.form['password']

        users = db.collection(u'spotify_users').where(u'username', u'==', username).stream()

        users = [i for i in users]

        if len(users) != 1:
            flash('multiple users found')
            return redirect(url_for('index'))

        doc = users[0].to_dict()
        if doc is None:
            flash('username not found')
            return redirect(url_for('index'))

        if check_password_hash(doc['password'], password):
            session['username'] = username
            return redirect(url_for('app_route'))
        else:
            flash('incorrect password')
            return redirect(url_for('index'))

    else:
        return redirect(url_for('index'))


@blueprint.route('/logout', methods=['GET', 'POST'])
def logout():
    session.pop('username', None)
    flash('logged out')
    return redirect(url_for('index'))

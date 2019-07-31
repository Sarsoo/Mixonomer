from google.cloud import firestore
db = firestore.Client()


def get_user_query_stream(user):

    users = db.collection(u'spotify_users').where(u'username', u'==', user).stream()
    users = [i for i in users]

    return users


def get_user_doc_ref(user):

    users = get_user_query_stream(user)

    if len(users) == 1:

        return db.collection(u'spotify_users').document(u'{}'.format(users[0].id))

    else:
        print(len(users))
        raise ValueError


def get_user_playlists_collection(user_id):

    playlists = db.document(u'spotify_users/{}'.format(user_id)).collection(u'playlists')

    return playlists



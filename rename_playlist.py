import music.db.database as database

playlists = database.get_user_playlists('andy')

name = input('enter playlist name: ')

playlist = next((i for i in playlists if i.name == name), None)

if playlist is not None:
    new_name = input('enter new name: ')
    playlist.update_database({'name': new_name})
else:
    print('playlist not found')

from music.model.user import User
from music.model.playlist import Playlist

user = User.collection.filter('username', '==', 'andy').get()

name = input('enter playlist name: ')
playlist = Playlist.collection.parent(user.key).filter('name', '==', name).get()

if playlist is not None:
    new_name = input('enter new name: ')
    playlist.name = new_name
    playlist.update()
else:
    print('playlist not found')

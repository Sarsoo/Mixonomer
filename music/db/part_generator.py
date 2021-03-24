from music.model.user import User
from music.model.playlist import Playlist
import logging
from typing import List
from google.cloud.firestore import DocumentReference

logger = logging.getLogger(__name__)


class PartGenerator:
    """Resolve a playlists components from other referenced smart playlists
    """

    def __init__(self, user: User = None, username: str = None):
        """Initialise with user to resolve for

        Args:
            user (User, optional): Subject user. Defaults to None.
            username (str, optional): Subject username. Defaults to None.

        Raises:
            LookupError: No user returned when querying for username
            NameError: No user provided
        """
        self.queried_playlists = []
        self.parts = []

        if user:
            self.user = user
        elif username:
            pulled_user = User.collection.filter('username', '==', username.strip().lower()).get()
            if pulled_user:
                self.user = pulled_user
            else:
                raise LookupError(f'{username} not found')
        else:
            raise NameError('no user info provided')

    def reset(self):
        """Reset internal state for resolved playlists
        """

        self.queried_playlists = []
        self.parts = []

    def get_recursive_parts(self, name: str) -> List[str]:
        """Resolve and return a playlist's component Spotify playlist names

        Args:
            name (str): Subject smart playlist name

        Returns:
            List[str]: Resolved list of component playlists
        """

        logger.info(f'getting part from {name} for {self.user.username}')

        self.reset()
        self.process_reference_by_name(name)

        return list({i for i in self.parts})

    def process_reference_by_name(self, name: str) -> None:
        """Resolve a smart playlist by name, recurses into process_reference_by_reference

        Args:
            name (str): Subject playlist name
        """

        playlist = Playlist.collection.parent(self.user.key).filter('name', '==', name).get()

        if playlist is not None:

            if playlist.id not in self.queried_playlists:

                self.parts += playlist.parts
                self.queried_playlists.append(playlist.id)

                for i in playlist.playlist_references:
                    if i.id not in self.queried_playlists:
                        self.process_reference_by_reference(i)

            else:
                logger.warning(f'playlist reference {name} already queried')

        else:
            logger.warning(f'playlist reference {name} not found')

    def process_reference_by_reference(self, ref: DocumentReference):
        """Recursive resolution function for walking a playlist's dependencies by DocumentReference

        Args:
            ref (DocumentReference): Subject Firestore document for resolving
        """

        if ref.id not in self.queried_playlists:
            playlist_reference_object = ref.get().to_dict()
            self.parts += playlist_reference_object['parts']
            self.queried_playlists.append(ref.id)

            for i in playlist_reference_object['playlist_references']:
                self.process_reference_by_reference(i)

        else:
            logger.warning(f'playlist reference {ref.get().to_dict()["name"]} already queried')

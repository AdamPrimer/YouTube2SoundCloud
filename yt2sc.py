import yaml
import soundc
import youtube

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db import Base, Mapping

from bcrypt import hashpw, gensalt

class YT2SC:
    def __init__(self, config_path='yt2sc.conf'):
        # Get the configuration data
        with open(config_path, 'r') as fp:
            self._config = yaml.safe_load(fp)

        # Connect to the DB
        engine = create_engine('sqlite:///db/yt2sc.db')
        Base.metadata.bind = engine
        DBSession = sessionmaker(bind=engine)
        self._session = DBSession()

        # Initialize YouTube
        self.yt = youtube.YouTube()

        # Initialize SoundCloud
        self.user = None
        self._sc = None

    @property
    def sc(self):
        # Initialize SoundCloud
        if not self.user:
            return None

        if not self._sc:
            self._sc = soundc.SoundCloud(
                client_id=self._config['client_id'],
                client_secret=self._config['client_secret'],
                username=self.user['soundcloud_id'],
                password=self.user['soundcloud_password'])

        return self._sc

    def get_mappings(self, username, yt_lists, sc_lists):
        yt_map = {str(x['id']): x['snippet']['title'] for x in yt_lists}
        sc_map = {str(x['id']): x['title'] for x in sc_lists}

        _mappings = self._session.query(Mapping).filter(
            Mapping.user_id == username).all()

        mappings = []
        for mapping in _mappings:
            mappings.append({
                'yt_playlist': mapping.yt_playlist,
                'sc_playlist': mapping.sc_playlist,
                'yt_title': yt_map.get(mapping.yt_playlist, "No Title"),
                'sc_title': sc_map.get(mapping.sc_playlist, "No Title"),
            })

        return mappings

    def add_mapping(self, username, yt_list, sc_list):
        mapping = Mapping(
            user_id=username,
            yt_playlist=yt_list,
            sc_playlist=sc_list
        )
        self._session.add(new_person)
        self._session.commit()

    def authorize(self, username, password_hash):
        if username not in self._config['users']:
            return False

        user = self._config['users'][username]
        stored = user['password']
        if stored == password_hash:
            self.user = {
                'username': username,
                'youtube_id': user['youtube_id'],
                'soundcloud_id': user['soundcloud_id'],
                'soundcloud_password': user['soundcloud_password'],
            }
            return True

        return False

    def get_password_hash(self, username, password):
        if username not in self._config['users']:
            return False

        stored = self._config['users'][username]['password']
        if stored == hashpw(password.encode('utf-8'), stored.encode('utf-8')):
            return stored

        return False

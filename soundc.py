import soundcloud

class SoundCloud:
    def __init__(self, client_id, client_secret, **kwargs):
        self._client = None
        self._method = None
        self._client_id = client_id
        self._client_secret = client_secret
        self._opts = kwargs

    def get_playlists(self, username):
        me = self.client.get("/me")
        objs = self.client.get("/users/{}/playlists".format(me.id))

        playlists = []
        for obj in objs:
            playlists.append({
                'id': obj.id,
                'description': obj.description,
                'title': obj.title,
                'tracks': obj.tracks,
            })

        return playlists

    def get_playlist(self, playlist_id):
        try:
            return self.client.get("/playlists/{}".format(playlist_id))
        except Exception:
            return None

    @property
    def client(self):
        if not self._client:
            self._client = self._get_client()
        return self._client

    def _get_client(self):
        if 'username' in self._opts and 'password' in self._opts:
            return soundcloud.Client(
                client_id=self._client_id,
                client_secret=self._client_secret,
                username=self._opts['username'],
                password=self._opts['password'])

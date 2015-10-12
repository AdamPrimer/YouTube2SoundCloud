import requests

class YouTube:
    def __init__(self):
        self.api_base = "https://www.googleapis.com/youtube/v3"
        self.api_key = "AIzaSyDC2ADHHGOsfSUwab4WEBTvZwFsiCMXMYM"

    def get_playlists(self, channel_id):
        url = "{}/playlists".format(self.api_base)
        req = requests.get(url, params={
            'part': 'snippet',
            'channelId': channel_id,
            'key': self.api_key,
        })
        data = req.json()
        playlists = data['items']

        return playlists

    def get_playlist(self, playlist_id):
        url = "{}/playlists".format(self.api_base)
        req = requests.get(url, params={
            'part': 'snippet',
            'id': playlist_id,
            'key': self.api_key,
        })
        data = req.json()
        playlist = data['items'][0]

        return {
            'id': playlist['id'],
            'title': playlist['snippet']['title'],
            'description': playlist['snippet']['description'],
            'items': self.get_playlist_items(playlist_id)
        }

    def get_playlist_items(self, playlist_id):
        url = "{}/playlistItems".format(self.api_base)

        def get_playlist_page(pageToken=''):
            req = requests.get(url, params={
                'part': 'snippet',
                'playlistId': playlist_id,
                'key': self.api_key,
                'maxResults': 50,
                'pageToken': pageToken
            })
            return req.json()

        items = []

        page = get_playlist_page()
        for item in page['items']:
            if 'thumbnails' in item['snippet']:
                items.append(item)

        while 'nextPageToken' in page:
            page = get_playlist_page(page['nextPageToken'])
            for item in page['items']:
                if 'thumbnails' in item['snippet']:
                    items.append(item)

        return items

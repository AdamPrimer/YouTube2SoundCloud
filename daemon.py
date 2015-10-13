#!/usr/bin/env python
import os
import sys
import yt2sc
import youtube_dl

ytsc = yt2sc.YT2SC()

for username, user in ytsc._config['users'].iteritems():
    authorized = ytsc.authorize(username, user['password'])

    username = ytsc.user['username']

    sys.stdout.write("Fetching YouTube Playlists for {}\n".format(username))
    yt_lists = ytsc.yt.get_playlists(ytsc.user['youtube_id'])

    sys.stdout.write("Fetching SoundCloud Playlists for {}\n".format(username))
    sc_lists = ytsc.sc.get_playlists()

    sys.stdout.write("Mapping YouTube Playlists to SoundCloud Playlists\n")
    maps = ytsc.get_mappings(ytsc.user['username'], yt_lists, sc_lists)

    for m in maps:
        yt_list = ytsc.yt.get_playlist(m['yt_playlist'])
        if not yt_list:
            continue

        sc_list = ytsc.sc.get_playlist(m['sc_playlist'])
        if not sc_list:
            continue

        sc_name_map = {k['title']: k for k in sc_list.tracks}

        _tracks = [k['id'] for k in sc_list.tracks]

        transfers = []

        # Look for each item in the YouTube Playlist, and see if it is in the
        # SoundCloud playlist. If it's not, it's a new upload and needs to be
        # ripped and transfered.
        for track in yt_list['items']:
            title = track['snippet']['title']
            if title not in sc_name_map:
                transfers.append({
                    'title': title,
                    'id': track['snippet']['resourceId']['videoId'],
                    'description': track['snippet']['description'],
                    'added': track['snippet']['publishedAt'],
                    'artist': track['snippet']['channelTitle'],
                    'album': yt_list['title'],
                })

        for i, transfer in enumerate(transfers):
            sys.stdout.write("Downloading {} of {}: {}\n".format(
                i+1, len(transfers), transfer['title']))

            ydl_opts = {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }, {
                    'key': 'FFmpegMetadata',
                }],
                'prefer_ffmpeg': True,
                'postprocessor_args': [
                    '-metadata',
                    'description={}'.format(transfer['description']),
                    '-metadata',
                    'artist={}'.format(transfer['artist']),
                    '-metadata',
                    'album={}'.format(transfer['album'])
                ]
            }

            # Download and post-process using `youtube-dl`
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                result = ydl.extract_info(
                    "https://www.youtube.com/watch?v={}".format(transfer['id']),
                    download=True,
                )

            # Clean the filename of unallowed characters
            clean_title = result['title'].replace('\\', '_').replace('/', '_').replace('&', '_')
            filename = "{}-{}.mp3".format(
                clean_title, result['id'])

            sys.stdout.write("Uploading {} of {}: {}\n".format(
                i+1, len(transfers), transfer['title']))

            # Upload the new track and make it downloadable
            track = ytsc.sc.client.post('/tracks', track={
                'title': result['title'],
                'description': result['description'],
                'downloadable': 'true',
                'release': transfer['added'],
                'asset_data': open(filename, 'rb')
            })

            sys.stdout.write("Assigning Playlist {} of {}: {}\n".format(
                i+1, len(transfers), transfer['title']))

            # Add the new track id to the list of tracks
            _tracks.append(track.id)

            # PUT the new playlist track listing
            ytsc.sc.client.put(sc_list.uri, playlist={
                'tracks': map(lambda id: dict(id=id), _tracks)})

            # Delete the file from the disk to avoid running out of space
            os.remove(filename)

            sys.stdout.write("Transfered {} of {}: {}\n\n".format(
                i+1, len(transfers), transfer['title']))

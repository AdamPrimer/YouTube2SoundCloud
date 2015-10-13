# Pre-requisites

- virtualenv
- Python 2.7.9
- ffmpeg

# Installation

    virtualenv env
    source env/bin/activate
    pip install -r requirements.txt
    chmod 0700 daemon.py
    chmod 0700 password_gen.py

# Configuration File

First, rename `yt2sc.template.conf` to `yt2sc.conf`

    mv yt2sc.template.conf yt2sc.conf

Then edit this YAML formatted file to include the following information.

    "client_id": "" // Your SoundCloud App Client ID
    "client_secret": "" // Your SoundCloud App Client Secret
    "users":
        "SuperAdmin": // Your desired Username to login to the app
            "password": "" // A hash of your disired Password to login to the app (see Password below).
            "youtube_id": "" // The channel ID assigned to you by YouTube
            "soundcloud_id": "" // Your SoundCloud username (should be your email)
            "soundcloud_password": "" // Your SoundCloud password

# Password

- Run `password_gen.py`
- Enter your desired password when asked
- Copy the provided hash into the "password" field of the config file.

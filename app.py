import os
from flask import (
    Flask,
    redirect,
    request,
    render_template,
    send_file,
    Response,
    make_response,
    url_for,
)
from werkzeug import secure_filename
import yt2sc

UPLOAD_FOLDER = './uploads'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def requires_auth(ytsc):
    username = request.cookies.get("username")
    password = request.cookies.get("password")

    if not ytsc.authorize(username, password):
        return redirect('admin/login')

    return None

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/admin/channel/<user>')
def admin_channel(user):
    ytsc = yt2sc.YT2SC()
    return ytsc.yt.get_channel(user_id=user)

@app.route('/admin/logout')
def admin_logout():
    resp = make_response(redirect('admin/login'))
    resp.set_cookie('username', '')
    resp.set_cookie('password', '')
    return resp

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    ytsc = yt2sc.YT2SC()

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        password_hash = ytsc.get_password_hash(username, password)
        if password_hash:
            resp = make_response(redirect('admin/playlist'))
            resp.set_cookie('username', username)
            resp.set_cookie('password', password_hash)
            return resp

    return render_template('admin_login.html')

@app.route('/admin/playlist', methods=['GET', 'POST'])
def admin_playlist():
    ytsc = yt2sc.YT2SC()
    resp = requires_auth(ytsc)
    if resp:
        return resp

    # Insert new Mapping
    if request.method == 'POST':
        yt_list = request.form.get('youtube')
        sc_list = request.form.get('soundcloud')
        ytsc.add_mapping(ytsc.user['username'], yt_list, sc_list)
        return redirect("admin/playlist")

    yt_lists = ytsc.yt.get_playlists(ytsc.user['youtube_id'])
    sc_lists = ytsc.sc.get_playlists()

    maps = ytsc.get_mappings(ytsc.user['username'], yt_lists, sc_lists)

    return render_template('admin_playlist.html',
            maps=maps,
            yt_lists=yt_lists,
            sc_lists=sc_lists)



@app.route('/admin/playlist/<mapping_id>/edit', methods=['GET', 'POST'])
def admin_playlist_edit(mapping_id):
    ytsc = yt2sc.YT2SC()
    resp = requires_auth(ytsc)
    if resp:
        return resp

    mapping = ytsc.get_mapping(mapping_id)

    if not mapping or mapping.user_id != ytsc.user['username']:
        return redirect("admin/playlist")

    if request.method == 'POST':
        # If we are uploading a logo
        f = request.files['logo']
        if f and allowed_file(f.filename):
            _, ext = os.path.splitext(f.filename)
            filename = secure_filename("{}.{}".format(mapping_id, ext))
            path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            f.save(path)

            sc_list = ytsc.sc.get_playlist(mapping.sc_playlist)
            ytsc.set_album_art(mapping_id, path)

            #ytsc.sc.client.put(sc_list.uri, playlist={
            #    'artwork_data': open(path, 'rb')})

            for track in sc_list.tracks:
                if track['artwork_url']:
                    continue

                print track['title']
                res = ytsc.sc.client.put(track['uri'], track={
                    'artwork_data': open(path, 'rb')
                })

            return redirect("admin/playlist/{}/edit".format(mapping_id))

        blist = request.form.getlist('blacklisted[]')
        ytsc.set_blacklist(mapping_id, blist)
        return redirect("admin/playlist")

    blist = ytsc.get_blacklist(mapping_id)
    blacklist = {k.yt_id: k for k in blist}

    playlist = ytsc.yt.get_playlist(mapping.yt_playlist)

    for item in playlist['items']:
        yt_id = item['snippet']['resourceId']['videoId']
        item['is_blacklisted'] = yt_id in blacklist

    return render_template('admin_playlist_blacklist.html',
            playlist=playlist)

@app.route('/admin/playlist/<mapping_id>/delete')
def admin_playlist_delete(mapping_id):
    ytsc = yt2sc.YT2SC()
    resp = requires_auth(ytsc)
    if resp:
        return resp

    # Remove the mapping
    ytsc.rm_mapping(mapping_id)
    return redirect("admin/playlist")

if __name__ == '__main__':
    app.run(debug=True, port=5000)

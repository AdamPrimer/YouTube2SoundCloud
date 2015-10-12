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
import yt2sc

app = Flask(__name__)

def requires_auth(ytsc):
    username = request.cookies.get("username")
    password = request.cookies.get("password")

    if not ytsc.authorize(username, password):
        return redirect('admin/login')

    return None

@app.route('/admin/logout', methods=['GET', 'POST'])
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
    sc_lists = ytsc.sc.get_playlists(ytsc.user['soundcloud_id'])

    maps = ytsc.get_mappings(ytsc.user['username'], yt_lists, sc_lists)

    return render_template('admin_playlist.html',
            maps=maps,
            yt_lists=yt_lists,
            sc_lists=sc_lists)

if __name__ == '__main__':
    app.run(debug=True, port=5555)

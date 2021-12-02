import spotipy
from spotipy.oauth2 import SpotifyOAuth
from flask import Flask, request, url_for, session, redirect, render_template
import json
import time
import os
from spotifysecrets import likedID, likedSecret

app = Flask(__name__)

app.secret_key = "OsdfdEdfdI234D"
app.config['SESSION_COOKIE_NAME'] = 'Cookie'


# TOKENINFO = "token_info"

@app.route('/')
def login():
    sp_oauth = create_spotify_oauth()
    auth_url = sp_oauth.get_authorize_url()
    # print(auth_url)
    return redirect(auth_url)


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    for key in list(session.keys()):
        session.pop(key)
    if os.path.exists("./.cache"):
        os.remove("./.cache")
    return redirect('/')


@app.route('/authorize')
def authorize():
    sp_oauth = create_spotify_oauth()
    session.clear()
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    session["token_info"] = token_info
    return redirect("/functions")


@app.route('/functions')
def spotifyFunctions():
    # Confirm authorization
    session['token_info'], authorized = get_token()
    session.modified = True
    if not authorized:
        return redirect('/')
    sp = spotipy.Spotify(auth=session.get('token_info').get('access_token'))
    # Retrieves user's saved songs
    songList = []
    count = 0
    while True:
        offset = count * 50
        count += 1
        curGroup = sp.current_user_saved_tracks(limit=50, offset=offset)['items']
        for idx, item in enumerate(curGroup):
            track = item['track']
            val = {'name': track['name'], 'artist': track['artists'][0]['name']}
            songList += [val]
        if len(curGroup) < 50:
            break
    # Retrieves user's public owned playlists
    playlistsObject = sp.current_user_playlists()
    playlists = []
    for p in playlistsObject["items"]:
        playlists.append({"name": p["name"], "id": p["id"]})
    # Just added a way to more easily visualize the structure
    with open('playlistTest.json', 'w') as f:
        json.dump(playlistsObject, f)
    return render_template('index.html', songList=songList, playlists=playlists)


@app.route('/addToPlaylist', methods=['POST'])
def addToPlaylist():
    playlistID = request.form.get("addToPlaylist")
    print(playlistID)
    return redirect('/functions')


# Checks to see if token is valid and gets a new token if not
def get_token():
    token_valid = False
    token_info = session.get("token_info", {})

    # Checking if the session already has a token stored
    if not (session.get('token_info', False)):
        token_valid = False
        return token_info, token_valid

    # Checking if token has expired
    now = int(time.time())
    is_token_expired = session.get('token_info').get('expires_at') - now < 60

    # Refreshing token if it has expired
    if is_token_expired:
        sp_oauth = create_spotify_oauth()
        token_info = sp_oauth.refresh_access_token(session.get('token_info').get('refresh_token'))

    token_valid = True
    return token_info, token_valid


def create_spotify_oauth():
    return SpotifyOAuth(
        client_id=likedID,
        client_secret=likedSecret,
        redirect_uri=url_for('authorize', _external=True),
        show_dialog=True,
        scope="user-library-read, playlist-modify-public")

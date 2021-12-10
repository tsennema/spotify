import spotipy
from spotipy.oauth2 import SpotifyOAuth
from flask import Flask, request, url_for, session, redirect, render_template
import json
import time, datetime
import os
import random
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
    songIDs = getLikedSongs(sp)
    songList = []
    for song in songIDs:
        track = sp.track(song)
        songList.append({"name": track["name"], "artist": track["artists"][0]["name"]})

    # Retrieves user's public owned playlists and *publicly* followed playlists
    playlistsObject = sp.current_user_playlists()
    playlists = []
    followedPlaylists = []
    user = sp.current_user()
    for p in playlistsObject["items"]:
        if p['owner']['id'] == user['id']:
            playlists.append({"name": p["name"], "id": p["id"]})
        else:
            followed = sp.playlist(p['id'])
            length = 0
            for track in followed['tracks']['items']:
                length += track['track']['duration_ms'] / 1000 / 60 / 60
            followedPlaylists.append({"name": p["name"], "id": p["id"], "length": round(length, 3)})
    # Just added a way to more easily visualize the structure
    # with open('playlistTest.json', 'w') as f:
    #     json.dump(playlistsObject, f)
    return render_template('index.html', songList=songList, playlists=playlists, followedPlaylists=followedPlaylists)


@app.route('/addToPlaylist', methods=['POST'])
def addToPlaylist():
    sp = spotipy.Spotify(auth=session.get('token_info').get('access_token'))
    playlistID = request.form.get("addToPlaylist")
    songList = getLikedSongs(sp)
    # sp.playlist_add_items(playlistID, songList)
    return redirect('/functions')


@app.route('/removeFromLiked', methods=['POST'])
def removeFromLiked():
    sp = spotipy.Spotify(auth=session.get('token_info').get('access_token'))
    songList = getLikedSongs(sp)
    # sp.current_user_saved_tracks_delete(songList)

    return redirect('/functions')


@app.route('/createPartialPlaylist', methods=['POST'])
def createPartialPlaylist():
    sp = spotipy.Spotify(auth=session.get('token_info').get('access_token'))
    # Get string playlistID
    playlistID = request.form.get("createPartialPlaylist")
    if not playlistID:
        return redirect('/functions')
    # Get list of song IDs
    playlistTracksObject = sp.playlist_items(playlistID, additional_types=("track",))
    playlistTracks = []
    for track in playlistTracksObject["items"]:
        playlistTracks.append(track['track']['id'])
    # Get string newName
    newName = request.form.get("newName")
    if not newName:
        return redirect('/functions')

    # Shuffle will be "on" or None
    shuffle = request.form.get("shuffleOn")
    if shuffle:
        shuffledTracks = []
        while len(shuffledTracks) < len(playlistTracks):
            tmp = random.choice(range(len(playlistTracks)))
            if playlistTracks[tmp] not in shuffledTracks:
                shuffledTracks.append(playlistTracks[tmp])
            if len(shuffledTracks) == len(playlistTracks):
                break
        playlistTracks = shuffledTracks

    # Get max length, convert to float
    maxLength = request.form.get("playlistLength")
    if not isFloat(maxLength) or float(maxLength) < 0.5:
        return redirect('/functions')
    maxLength = float(maxLength)
    # Shorten playlist by adding songs until hitting max length
    shortPlaylist = []
    totalTime = 0
    for trackID in playlistTracks:
        dur = sp.track(trackID)["duration_ms"] / 1000.0 / 60 / 60
        if totalTime + dur < maxLength:
            shortPlaylist.append(trackID)
            totalTime += dur
        else:
            break
    date = datetime.date.today()
    description = f"Shortened version of {sp.playlist(playlistID)['name']}, created on {date}"
    # Create new playlist
    newPlaylist = sp.user_playlist_create(sp.current_user()['id'], name=str(newName), description=description)
    # Add songs
    sp.playlist_add_items(newPlaylist['id'], shortPlaylist)
    return redirect('/functions')


def isFloat(i):
    try:
        float(i)
    except ValueError:
        return False
    return True


def getLikedSongs(sp):
    # Returns list of ids of songs in user's library
    songList = []
    count = 0
    while True:
        offset = count * 50
        count += 1
        curGroup = sp.current_user_saved_tracks(limit=50, offset=offset)['items']
        for idx, item in enumerate(curGroup):
            # val = {item['track']['id']}
            songList.append(item['track']['id'])
        if len(curGroup) < 50:
            break
    return songList


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

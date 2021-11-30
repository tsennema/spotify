import spotipy
from spotipy.oauth2 import SpotifyOAuth
from flask import Flask, request, url_for, session, redirect
import json
import time
# from secrets import likedID, likedSecret

app = Flask(__name__)

app.secret_key = "OsdfdEdfdI234D"
app.config['SESSION_COOKIE_NAME'] = 'Cookie'
TOKENINFO = "token_info"

@app.route('/')
def login():
    print("login")
    sp_oauth = create_spotify_oauth()
    auth_url = sp_oauth.get_authorize_url()
    # print(auth_url)
    return redirect(auth_url)

@app.route('/logout')
def logout():
    print("logout")
    for key in list(session.keys()):
        session.pop(key)
    return redirect('/')


@app.route('/authorize')
def authorize():
    print("authorize")
    sp_oauth = create_spotify_oauth()
    session.clear()
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    session["token_info"] = token_info
    return redirect("/getTracks")


@app.route('/getTracks')
def get_all_tracks():
    print("getTracks")
    session['token_info'], authorized = get_token()
    session.modified = True
    if not authorized:
        return redirect('/')
    sp = spotipy.Spotify(auth=session.get('token_info').get('access_token'))
    results = []
    count = 0
    while True:
        offset = count * 50
        count += 1
        curGroup = sp.current_user_saved_tracks(limit=50, offset=offset)['items']
        for idx, item in enumerate(curGroup):
            track = item['track']
            val = track['name'] + " - " + track['artists'][0]['name']
            results += [val]
        if (len(curGroup) < 50):
            break
    print(results)
    return str(len(results))
    # df = pd.DataFrame(results, columns=["song names"])
    # df.to_csv('songs.csv', index=False)
    return "done"

# Checks to see if token is valid and gets a new token if not
def get_token():
    print("gettoken")
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
    if (is_token_expired):
        sp_oauth = create_spotify_oauth()
        token_info = sp_oauth.refresh_access_token(session.get('token_info').get('refresh_token'))

    token_valid = True
    return token_info, token_valid


likedID = "d16c203095be4fdd8416513097acbcb5"
likedSecret = "ef2088df16d44622a652c2364b26d99f"

def create_spotify_oauth():
    return SpotifyOAuth(
            client_id=likedID,
            client_secret=likedSecret,
            redirect_uri=url_for('authorize', _external=True),
            scope="user-library-read")

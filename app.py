from flask import Flask, request, url_for, session, redirect
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import time
# from secrets import likedID, likedSecret

app = Flask(__name__)

app.secret_key = "OsdfdEdfdI234D"
app.config['SESSION_COOKIE_NAME'] = 'Cookie'
TOKENINFO = "token_info"

@app.route('/')
def login():
    spOauth = createSpotifyOauth()
    authURL = spOauth.get_authorize_url()
    return redirect(authURL)


@app.route('/redirect')
def redirectPage():
    spOauth = createSpotifyOauth()
    session.clear()
    code = request.args.get('code')
    tokenInfo = spOauth.get_access_token(code)
    session[TOKENINFO] = tokenInfo
    return redirect(url_for('getLiked', _external=True))


@app.route('/getLiked')
def getLiked():
    try:
        tokenInfo = getToken()
    except:
        print("user not logged in")
        redirect("/")
    return "help meee"
    #sp = spotipy.Spotify(auth=tokenInfo['access_token'])
    return str(sp.current_user_saved_tracks(limit=50, offset=0)['items'][0])

def getToken():
    tokenInfo = session.get(TOKENINFO, None)
    if not tokenInfo:
        raise "exception"
    now = int(time.time)
    isExpired = tokenInfo['expires_at'] - now < 60
    if (isExpired):
        spOauth = createSpotifyOauth()
        tokenInfo = spOauth.refresh_access_token(tokenInfo['refresh_token'])
    return tokenInfo


likedID = "d16c203095be4fdd8416513097acbcb5"
likedSecret = "ef2088df16d44622a652c2364b26d99f"
def createSpotifyOauth():
    return SpotifyOAuth(
        client_id=likedID,
        client_secret=likedSecret,
        redirect_uri=url_for('redirectPage', _external=True),
        scope='user-library-read'
    )

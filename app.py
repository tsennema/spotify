from flask import Flask, request, url_for, session, redirect
import spotipy
from spotipy.oauth2 import SpotifyOAuth
# from secrets import likedID, likedSecret

app = Flask(__name__)

app.secret_key = "OsdfdEdfdI234D"
app.config['SESSION_COOKIE_NAME'] = 'Cookie'


@app.route('/')
def login():
    spOauth = createSpotifyOauth()
    authURL = spOauth.get_authorize_url()
    return redirect(authURL)


@app.route('/redirect')
def redirectPage():
    return "redirect"


@app.route('/getLiked')
def getLiked():
    return "test"

likedID = "d16c203095be4fdd8416513097acbcb5"
likedSecret = "ef2088df16d44622a652c2364b26d99f"
def createSpotifyOauth():
    return SpotifyOAuth(
        client_id=likedID,
        client_secret=likedSecret,
        redirect_uri=url_for('redirectPage', _external=True),
        scope='user-library-read'
    )

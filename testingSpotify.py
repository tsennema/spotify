import requests
import base64, json
from spotifysecrets import clientID, clientSecret

# CTRL ALT L to format json

authURL = "https://accounts.spotify.com/api/token"
authHeader = {}
authData = {}


# Base64 Encode Client ID and Client Secret

def getAccessToken(clientID, clientSecret):
    message = f"{clientID}:{clientSecret}"
    message_bytes = message.encode('ascii')
    base64_bytes = base64.b64encode(message_bytes)
    base64_message = base64_bytes.decode('ascii')

    authHeader['Authorization'] = "Basic " + base64_message
    authData['grant_type'] = "client_credentials"

    res = requests.post(authURL, headers=authHeader, data=authData)
    responseObject = res.json()
    # print(json.dumps(responseObject, indent=2))

    accessToken = responseObject['access_token']

    return accessToken


def getPlaylistTracks(token, playlistID):
    playlistEndPoint = f"https://api.spotify.com/v1/playlists/{playlistID}"

    getHeader = {
        "Authorization": "Bearer " + token
    }
    res = requests.get(playlistEndPoint, headers=getHeader)

    playlistObject = res.json()

    return playlistObject


# API requests
token = getAccessToken(clientID, clientSecret)
playlistID = "5CORh2nLsbjOQQ4leKe5jN?si=9139e89eec2a4216"

tracklist = getPlaylistTracks(token, playlistID)

with open('tracklist.json', 'w') as f:
    json.dump(tracklist, f)

for t in tracklist['tracks']['items']:
    print('----')
    for a in t['track']['artists']:
        print(a['name'])
    songName = t['track']['name']
    print(songName)

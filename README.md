# spotify

This project will demonstrate ability to work with a 3rd party API, in this case, spotify.

A couple functions that have been suggested to me, that are difficult to do in the actual spotify app, will be the focus of this project

1. Spotify's "Liked songs" list is very easy to add to, with a little heart button beside playing songs.
However, the Liked songs list is not a typical playlist object, and so you cannot do a few things (like find someone elses list, or add it to another playlist in your queue)
This function will be to move songs in the Liked songs list to a given other playlist, to be accessible as normal

2. There are some great, giant playlists out there that have a large amount of variety, but downloading them for times away from consistent internet is tricky, since most devices
won't have enough space for 100+ hr of music.
This function will, with or without shuffling, copy songs to a new playlist until reaching a cap (perhaps just time, or file size if I can find it)

3. I'd like to explore the recommended system, since it seems to take into account everything a user listens to when recommending new tracks/playlists.
The problem there, is sometimes people listen to diverse genres that shouldn't be mixed, like soundtracks, white noise, christmas music, etc, that they don't want to
be recommended. Maybe adding a genre filter would be helpful here.

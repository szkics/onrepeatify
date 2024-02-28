## onrepeatify

wouldn't it be cool to automatically create a playlist with all your most listened songs on Spotify?

for this to happen, we will create a playlist which contains all your past and current favorites.

this means we will add all songs from 'On Repeat' and 'Repeat Rewind' to a new playlist created by you.

run the script once in a while to synchronize and add your new favorites, but don't forget about the old ones.

this is a script which can be used to copy tracks from one playlist to the other using the Spotify API through spotipy.

## spotify api setup

Visit: https://developer.spotify.com/dashboard and click 'Create App'.

Client ID and secret will be generated automatically, copy them, open terminal and:

```sh
export SPOTIFY_CLIENT_ID='<client id>'
export SPOTIFY_CLIENT_SECRET='<client secret>'
```

The redirect URI is also a required field, just add: http://localhost:8888/callback

## environment variables required by the script

```sh
export SPOTIFY_ON_REPEAT_PLAYLIST_ID='<id of source playlist>'
export SPOTIFY_FAVORITES_PLAYLIST_ID='<id of destination playlist>'
```
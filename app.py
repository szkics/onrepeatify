from flask import Flask, render_template, redirect, request, session, url_for
from flask_session import Session
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Spotify API credentials
SPOTIPY_CLIENT_ID = os.environ.get("SPOTIFY_CLIENT_ID")
SPOTIPY_CLIENT_SECRET = os.environ.get("SPOTIFY_CLIENT_SECRET")
SPOTIPY_REDIRECT_URI = "http://127.0.0.1:5000/callback"

# Spotify API scopes
SPOTIFY_SCOPES = ["playlist-read-private", "playlist-modify-private", "playlist-modify-public"]

# Initialize Spotipy
sp_oauth = SpotifyOAuth(
    SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, SPOTIPY_REDIRECT_URI, scope=SPOTIFY_SCOPES
)

def get_track_name_based_on_id(sp, track_id):
    track_info = sp.track(track_id)
    return f"{track_info['name']} by {track_info['artists'][0]['name']}"

def add_tracks_to_playlist(sp, playlist_id, track_ids):
    sp.playlist_add_items(playlist_id, track_ids)

def get_playlist_name_based_on_id(sp, playlist_id):
    playlist_info = sp.playlist(playlist_id)
    return playlist_info['name']

def get_playlist_tracks(sp, playlist_id):
    results = sp.playlist_tracks(playlist_id)
    track_ids = [item['track']['id'] for item in results['items']]

    while results['next']:
        results = sp.next(results)
        track_ids.extend([item['track']['id'] for item in results['items']])
    return track_ids

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/login")
def login():
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)


@app.route("/callback")
def callback():
    token_info = sp_oauth.get_access_token(request.args["code"])
    session["token_info"] = token_info
    return redirect(url_for("playlist"))


@app.route("/playlist")
def playlist():
    if "token_info" not in session:
        return redirect(url_for("login"))

    token_info = session["token_info"]
    sp = spotipy.Spotify(auth=token_info["access_token"])
    playlists = sp.current_user_playlists()

    return render_template("index.html", playlists=playlists)


@app.route("/copy", methods=["POST"])
def copy():
    if "token_info" not in session:
        return redirect(url_for("login"))

    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=SPOTIPY_CLIENT_ID,
                                                   client_secret=SPOTIPY_CLIENT_SECRET,
                                                   redirect_uri=SPOTIPY_REDIRECT_URI,
                                                   scope='playlist-read-private playlist-modify-private playlist-modify-public'))

    source_playlist_id = request.form.get("source_playlist_id")
    print(f"source_playlist_id: {source_playlist_id}")
    destination_playlist_id = request.form.get("destination_playlist_id")


    if source_playlist_id and destination_playlist_id:
        # Get tracks from 'On Repeat' playlist
        source_playlist_tracks = get_playlist_tracks(sp, source_playlist_id)

        # Get tracks from 'favorites' playlist
        destination_playlist_tracks = get_playlist_tracks(sp, destination_playlist_id)

        # Find new tracks in 'On Repeat' playlist and add them to 'favorites' playlist
        new_tracks = list(set(source_playlist_tracks) - set(destination_playlist_tracks))
        new_track_names = [get_track_name_based_on_id(sp, track_id) for track_id in new_tracks]
        
        if new_tracks:
            add_tracks_to_playlist(sp, destination_playlist_id, new_tracks)
            print(f"Added {len(new_tracks)} new tracks to your '{get_playlist_name_based_on_id(sp, destination_playlist_id)}' playlist.")
            print(f"Tracks added: {new_track_names}")
            return f"Added {len(new_tracks)} new tracks to your '{get_playlist_name_based_on_id(sp, destination_playlist_id)}' playlist."
        else:
            print("No new tracks to add.")
            return "No new tracks to add." 
    else:
        print("Playlist not found.")
        return "Source and destination playlist IDs are required."

if __name__ == "__main__":
    app.run(debug=True)

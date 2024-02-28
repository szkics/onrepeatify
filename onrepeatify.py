import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# Access environment variables
client_id = os.environ.get('SPOTIFY_CLIENT_ID')
client_secret = os.environ.get('SPOTIFY_CLIENT_SECRET')
username = os.environ.get('SPOTIFY_USER_NAME')
on_repeat_playlist_id = os.environ.get('SPOTIFY_ON_REPEAT_PLAYLIST_ID')
favorites_playlist_id = os.environ.get('SPOTIFY_FAVORITES_PLAYLIST_ID')

def get_playlist_tracks(sp, playlist_id):
    results = sp.playlist_tracks(playlist_id)
    return [item['track']['id'] for item in results['items']]

def get_track_name_based_on_id(sp, track_id):
    track_info = sp.track(track_id)
    return f"{track_info['name']} by {track_info['artists'][0]['name']}"

def add_tracks_to_playlist(sp, playlist_id, track_ids):
    sp.playlist_add_items(playlist_id, track_ids)

def get_playlist_name_based_on_id(sp, playlist_id):
    playlist_info = sp.playlist(playlist_id)
    return playlist_info['name']

def main():
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id,
                                                   client_secret=client_secret,
                                                   redirect_uri='http://localhost:8888/callback',
                                                   scope='playlist-read-private playlist-modify-private playlist-modify-public'))


    if on_repeat_playlist_id and favorites_playlist_id:
        # Get tracks from 'On Repeat' playlist
        on_repeat_tracks = get_playlist_tracks(sp, on_repeat_playlist_id)

        # Get tracks from 'favorites' playlist
        favorite_tracks = get_playlist_tracks(sp, favorites_playlist_id)

        # Find new tracks in 'On Repeat' playlist and add them to 'favorites' playlist
        new_tracks = list(set(on_repeat_tracks) - set(favorite_tracks))
        new_track_names = [get_track_name_based_on_id(sp, track_id) for track_id in new_tracks]
        
        if new_tracks:
            add_tracks_to_playlist(sp, favorites_playlist_id, new_tracks)
            print(f"Added {len(new_tracks)} new tracks to your '{get_playlist_name_based_on_id(sp, favorites_playlist_id)}' playlist.")
            print(f"Tracks added: {new_track_names}")
        else:
            print("No new tracks to add.")
    else:
        print("Playlist not found.")

if __name__ == "__main__":
    main()

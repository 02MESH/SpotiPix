#from dotenv import load_dotenv
import os
import sys
import json
import spotipy
import webbrowser
import spotipy.util as util
from json.decoder import JSONDecodeError
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth

load_dotenv()

# Get the username from terminal
username = "31nf5a5md2s5zugfwwqylxj7bj34"

# Get the API credentials
spotify_client_id = os.getenv('SPOTIFY_CLIENT_ID')
spotify_client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
spotify_redirect_uri = os.getenv('SPOTIFY_REDIRECT_URI')

#Set the scope of the app - what resources to access
scope = "user-library-read user-top-read playlist-modify-public playlist-read-private"

auth_manager = SpotifyOAuth(client_id=spotify_client_id, client_secret=spotify_client_secret,
                            redirect_uri=spotify_redirect_uri, scope=scope)

sp = spotipy.Spotify(auth_manager=auth_manager)

user = sp.current_user()

displayName = user['display_name']
followers = user['followers']['total']

print(f"Name: {displayName}, Followers: {followers}")

# Initialize an empty list to store all playlists
all_playlists = []

# Make the initial request
response = sp.current_user_playlists()
all_playlists.extend(response['items'])

# Continue to fetch playlists until no more are returned
while response['next']:
    response = sp.next(response)
    all_playlists.extend(response['items'])

# Now, `all_playlists` contains all of the user's playlists
# Iterate through each playlist and display its name and total tracks
for playlist in all_playlists:
    if(playlist['owner']['id']==username):
        print(f"Playlist Name: {playlist['name']} - Total Tracks: {playlist['tracks']['total']}")
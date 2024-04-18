import spotipy
from flask import Flask, redirect, request, session, url_for
import os
import time
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth

load_dotenv()

# Initialise the Flask application
app = Flask(__name__)

app.secret_key = "your_secret_key"
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_COOKIE_NAME'] = 'Spotify Cookie'
TOKEN_INFO = 'token_info'

# Get the API credentials
spotify_client_id = os.getenv('SPOTIFY_CLIENT_ID')
spotify_client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
spotify_redirect_uri = os.getenv('SPOTIFY_REDIRECT_URI')

# Authenticate
def createSpotifyOAuth():
    return SpotifyOAuth(client_id=spotify_client_id,
                     client_secret=spotify_client_secret,
                     redirect_uri=url_for('redirect_page', _external=True),
                     scope='user-library-read playlist-read-private playlist-modify-private')

def get_token():
    token_info = session.get(TOKEN_INFO)
    if not token_info:
        redirect(url_for('login', external=False))

    now = int(time.time())
    is_expired = token_info['expires_at'] - now < 60
    if(is_expired):
        spotify_oauth = createSpotifyOAuth()
        token_info = spotify_oauth.refresh_access_token(token_info['refresh_token'])
    return token_info

@app.route('/')
def login():
    auth_url = createSpotifyOAuth().get_authorize_url()
    return redirect(auth_url)

@app.route('/redirect')
def redirect_page():
    session.clear()
    code = request.args.get('code')
    token_info = createSpotifyOAuth().get_access_token(code)
    session[TOKEN_INFO] = token_info
    return redirect(url_for('save_discover_weekly', external=True))


@app.route('/saveDiscoverWeekly')
def save_discover_weekly():
    try:
        token_info = get_token()  # Implement this function to retrieve token
    except:
        print("User not logged in")
        return redirect('/')

    sp = spotipy.Spotify(auth=token_info['access_token'])
    user_id = sp.current_user()['id']  # Retrieve user ID from current_user()

    discover_weekly_playlist_id = None
    saved_weekly_playlist_id = None

    # Retrieve current user's playlists
    current_playlists = sp.current_user_playlists()['items']

    # Find "Discover Weekly" and "Saved Weekly" playlist IDs
    for playlist in current_playlists:
        if playlist['name'] == "Discover Weekly":
            discover_weekly_playlist_id = playlist['id']
        elif playlist['name'] == "Saved Weekly":
            saved_weekly_playlist_id = playlist['id']

    # Check if "Discover Weekly" playlist exists
    if not discover_weekly_playlist_id:
        return "Discover Weekly playlist not found"

    # Create "Saved Weekly" playlist if it doesn't exist
    if not saved_weekly_playlist_id:
        new_playlist = sp.user_playlist_create(user_id, 'Saved Weekly', True)
        saved_weekly_playlist_id = new_playlist['id']

    # Retrieve tracks from "Discover Weekly" playlist
    discover_weekly_tracks = sp.playlist_tracks(discover_weekly_playlist_id)['items']

    # Extract track URIs
    track_uris = [track['track']['uri'] for track in discover_weekly_tracks]

    # Add tracks to "Saved Weekly" playlist
    sp.user_playlist_add_tracks(user_id, saved_weekly_playlist_id, track_uris)

    return "Tracks from Discover Weekly saved to Saved Weekly playlist"


# @app.route('/callback')
# def callback():
#     code = request.args.get('code')
#     sp.auth_manager.get_access_token(code)
#     session['authorized'] = True
#     return redirect(url_for('user_playlists'))
#
#
# @app.route('/playlists')
# def user_playlists():
#     if 'authorized' in session and session['authorized']:
#         playlists = sp.current_user_playlists()
#         return str(playlists)
#     else:
#         return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

app.run(debug=True)
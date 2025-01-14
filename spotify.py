import spotipy
from dotenv import load_dotenv
import os
load_dotenv()
import requests
import base64
import json
import requests

client_id = os.getenv("SPOTIFY_CLIENT_ID")
client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")


def get_spotify_token():
    if not client_id or not client_secret:
        raise ValueError("Missing Spotify client credentials. Check your .env file.")
        
    auth_string = f"{client_id}:{client_secret}"
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")
    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}
    result = requests.post(url, headers=headers, data=data)
    json_result = result.json()
    token = json_result["access_token"]
    return token

token = get_spotify_token()

def get_spotify_headers(token):
    return {"Authorization": "Bearer " + token}

headers = get_spotify_headers(token)

def search_artist_id(token, artist_name):
    url = "https://api.spotify.com/v1/search"
    headers = get_spotify_headers(token)
    query = f"?q={artist_name}&type=artist&limit=1"
    query_url = url + query
    result = requests.get(query_url, headers=headers)
    json_result = result.json()["artists"]["items"]
    if len(json_result) == 0:
        return None
    return json_result[0]["id"]

def get_songs_by_artist(token, artist_id):
    url = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks?country=IN"
    headers = get_spotify_headers(token)
    result = requests.get(url, headers=headers)
    json_result = result.json()
    return json_result["tracks"]


def get_albums_by_artist(token, artist_id):
    url = f"https://api.spotify.com/v1/artists/{artist_id}/albums?include_groups=album&country=IN"
    headers = get_spotify_headers(token)
    
    result = requests.get(url, headers=headers)
    
    if result.status_code != 200:
        raise Exception(f"Error fetching albums: {result.json()}")
    
    json_result = result.json()
    
    # Extracting album information: name, release date, album ID, and link
    albums = [{
        "name": album["name"],
        "release_date": album["release_date"],
        "id": album["id"],
        "link": album["external_urls"]["spotify"]
    } for album in json_result.get("items", [])]
    
    return albums

def get_album_details(token, album_id):
    url = f"https://api.spotify.com/v1/albums/{album_id}"
    headers = get_spotify_headers(token)
    result = requests.get(url, headers=headers)
    if result.status_code != 200:
        raise Exception(f"API request failed with status code {result.status_code}: {result.text}")
    json_result = result.json()
    return {
        "name": json_result.get("name", "Unknown Album"),
        "external_urls": json_result.get("external_urls", {}),
    }

def get_album_tracks(token, id):
    url = f"https://api.spotify.com/v1/albums/{id}"
    headers = get_spotify_headers(token)
    result = requests.get(url, headers=headers)
    if result.status_code != 200:
        raise Exception(f"API request failed with status code {result.status_code}: {result.text}")
    
    json_result = result.json()
    album_tracks = json_result.get('tracks', {}).get('items', [])
    
    links = []  # Initialize an empty list to accumulate track links
    for idx, track in enumerate(album_tracks, start=1):
        track_name = track.get("name", "N/A")
        external_url = track.get("external_urls", {}).get("spotify", "#")
        links.append(f"{idx}. [{track_name}]({external_url})")  # Append the track link to the list

    return "\n".join(links)  # Join all track links into a single string with newlines

def get_playlist(token, playlist_id):
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}"
    headers = get_spotify_headers(token)
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        return None  # Handle error responses gracefully

    json_result = response.json()

    # Extract playlist details
    playlist_details = {
        "name": json_result.get("name", "N/A"),
        "url" : json_result.get("external_urls", {}).get("spotify", "#"),
        "description": json_result.get("description", "N/A"),
        "total_tracks": json_result.get("tracks", {}).get("total", 0),
        "owner": json_result.get("owner", {}).get("display_name", "N/A"),
    }
    # Extract and format track links
    tracks = json_result.get("tracks", {}).get("items", [])
    track_links = []
    for i, item in enumerate(tracks, start=1):
        track = item.get("track", {})
        if not track:
            continue  # Skip if track details are missing
        
        track_name = track.get("name", "N/A")
        artist = track.get("artists", [{}])[0].get("name", "N/A")
        track_url = track.get("external_urls", {}).get("spotify", "#")

        track_links.append(f"{i}. [{track_name} by {artist}]({track_url})")

    return playlist_details, "\n".join(track_links)    
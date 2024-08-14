import spotipy
from spotipy.oauth2 import SpotifyOAuth

sp = spotipy.Spotify(auth_manager=SpotifyOAuth
                     (client_id=''
                      , client_secret=''
                      , redirect_uri=''
                      , scope="playlist-read-private"))


def collect_tracks_from_playlists(playlist_urls):
    all_track_info = []
    limit = 100  # Spotify API limit per request

    for playlist_url in playlist_urls:
        playlist_id = playlist_url.split("/")[-1].split("?")[0]
        offset = 0
        total = 1  # Placeholder for the total number of tracks
        #print(playlist_url)
        while offset < total:
            tracks_playlist = sp.playlist_tracks(playlist_id, limit=limit, offset=offset)
            total = tracks_playlist['total']  # Total number of tracks in the playlist
            
            # Collect track IDs in a batch
            track_ids = [item['track']['uri'].split(":")[-1] for item in tracks_playlist['items']]
            
            # Fetch audio features for the batch of track IDs
            audio_features = sp.audio_features(track_ids)
            
            # Iterate through the tracks and their corresponding audio features
            for item, features in zip(tracks_playlist['items'], audio_features):
                track_uri = item['track']['uri']
                track_name = item['track']['name']
                artists = ", ".join([artist['name'] for artist in item['track']['artists']])
                bpm = features['tempo'] if features else None

							# Double the BPM of tracks that are slower than 100bpm to easier match appropriate running BPMs
                if bpm and bpm < 100:
                    bpm *= 2
                
                all_track_info.append({
                    'uri': track_uri,
                    'name': track_name,
                    'artists': artists,
                    'bpm': bpm
                })
            
            offset += limit

    return all_track_info

def filter_tracks_by_bpm(track_info, min_bpm, max_bpm):
    return [track for track in track_info if track['bpm'] and min_bpm <= track['bpm'] <= max_bpm]

# User input for multiple playlist URLs
playlist_urls = input("Enter playlist URLs separated by commas: ").split(',')

# Collect track info from all playlists
all_track_info = collect_tracks_from_playlists(playlist_urls)

# Now you can filter by BPM range multiple times without losing data
while True:
    min_bpm = float(input("Enter the minimum BPM (or 'q' to quit): "))
    max_bpm = float(input("Enter the maximum BPM (or 'q' to quit): "))

    filtered_tracks = filter_tracks_by_bpm(all_track_info, min_bpm, max_bpm)
    
    # Print the filtered results
    # Format BPM with alignment
    print("\nFiltered Tracks:")
    for track in filtered_tracks:
    # Truncate track name and artist names to avoid misalignment
        truncated_name = (track['name'][:37] + '...') if len(track['name']) > 40 else track['name']
        truncated_artists = (track['artists'][:27] + '...') if len(track['artists']) > 30 else track['artists']
        
        # Format BPM with alignment
        print(f"Track: {truncated_name:<40} Artists: {truncated_artists:<30} BPM: {track['bpm']:>6.1f}  URI: {track['uri']}")
  
    
    # Option to quit the loop
    another_query = input("Would you like to filter another BPM range? (y/n): ")
    if another_query.lower() != 'y':
        break

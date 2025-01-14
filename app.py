import streamlit as st
import time
import google.generativeai as genai
import base64
from spotify import (
    get_spotify_token, 
    get_spotify_headers, 
    search_artist_id, 
    get_playlist, 
    get_album_tracks, 
    get_songs_by_artist, 
    get_album_details,
    get_albums_by_artist
)
from youT import determine_video_topic, get_video_links, get_video_recommendations
from sveD_pl import save_energy_mood_stress, plot_mood_stress

# Initialize the Gemini model
model = genai.GenerativeModel("gemini-2.0-flash-exp")

prompt = """
You are a compassionate and uplifting AI specializing in mental wellness. Provide users with personalized, empathetic, and actionable advice tailored to their energy level, mood, and stress level. Your responses should be warm, clear, and structured, offering practical techniques such as mindfulness, grounding exercises, or self-reflection. Additionally, include a light-hearted, mood-appropriate joke to bring a smile and encourage positivity. Use supportive language to promote self-compassion and foster an optimistic outlook.
"""

prompt1 = """
You are a compassionate AI specializing in mental wellness, dedicated to understanding and supporting users based on their input. Carefully analyze the user's message to identify their mood, energy level, stress level, and any specific concerns or emotions they express. Provide personalized, empathetic, and actionable advice tailored to their current state.  

Ensure your responses are warm, clear, and focus on practical techniques such as mindfulness, grounding exercises, reflection, or other evidence-based strategies. When appropriate, guide the user through structured steps for self-care, stress relief, or positive action, encouraging self-compassion and resilience. Prioritize adapting your advice to align with the user's unique circumstances and expressed needs, fostering a sense of understanding and support.
"""

# Function to get Gemini AI response
def get_gemini_response(energy, mood, stress):
    input_text = f"Energy: {energy}, Mood: {mood}, Stress: {stress}z"
    response = model.generate_content([input_text, prompt])
    return response.text

def get_manual_gemini_response(user_input):
    response = model.generate_content([user_input, prompt])
    return response.text

def get_gif_for_manual():
    gif_path = "meeet.gif"  # Replace with the actual path to your GIF
    placeholder = st.empty()  # Placeholder for the GIF

    # Read and encode the GIF
    with open(gif_path, "rb") as f:
        gif_data = f.read()
        gif_base64 = base64.b64encode(gif_data).decode("utf-8")

    # Display the animated GIF
    placeholder.markdown(
        f'<img src="data:image/gif;base64,{gif_base64}" style="width:100%;"/>',
        unsafe_allow_html=True,
    )

    time.sleep(1) 

    response = get_manual_gemini_response(user_input)
    st.subheader("Your Wellness Advice")
    st.write(response)
    placeholder.empty()

def get_gif():
    gif_path = "meeet.gif"  # Replace with the actual path to your GIF
    placeholder = st.empty()  # Placeholder for the GIF

    # Read and encode the GIF
    with open(gif_path, "rb") as f:
        gif_data = f.read()
        gif_base64 = base64.b64encode(gif_data).decode("utf-8")

    # Display the animated GIF
    placeholder.markdown(
        f'<img src="data:image/gif;base64,{gif_base64}" style="width:100%;"/>',
        unsafe_allow_html=True,
    )

    time.sleep(1) 

    response = get_gemini_response(energy,mood,stress)
    st.subheader("Your Wellness Advice")
    st.write(response)
    placeholder.empty()

# Custom CSS for Styling
st.markdown("""
    <style>
        .main-header {
            text-align: center;
            font-size: 30px;
            color: #4CAF50;
            font-weight: bold;
            margin-bottom: 10px;
        }
        .sub-header {
            color: #555;
            margin-bottom: 20px;
            font-size: 18px;
        }
        .stButton > button {
            background-color: #4CAF50;
            color: white;
            border-radius: 10px;
            padding: 10px 20px;
            font-size: 16px;
        }
        .stButton > button:hover {
            background-color: #45a049;
        }
    </style>
""", unsafe_allow_html=True)

# App Header
st.title("🧠 Wellvy AI (Mental Wellness Assistant)")
st.markdown("<div class='sub-header'>Your AI-powered partner for mental wellness.</div>", unsafe_allow_html=True)
st.markdown("""
- **Welcome to Wellvy AI!**
- **You can get personalized mental wellness advice based on your energy level, mood, and stress level.**
- **A plot of your mood and stress level will be generated.**
- **You can also get video recommendations based on your mood and energy level.**
- **You can also get music recommendations based on your mood and energy level.**
""")

# Main UI with tabs
user_input_tab, manual_user_input = st.tabs(["User Input", "Manual User Input"])

with user_input_tab:
    # User Inputs
    st.header("Your Details")
    energy = st.selectbox("Select your energy level", ["High", "Medium", "Low"])
    mood = st.selectbox("Select your mood", ["Happy", "Sad", "Anxious", "Tired", "Overwhelmed", "Neutral"])
    stress = st.selectbox("Select your stress level", ["No", "Low", "Medium", "High"])

    st.markdown(f"### Your Input\n- **Energy Level:** {energy}\n- **Mood:** {mood}\n- **Stress Level:** {stress}")

    # Save and Plot Data
    if st.button("Save & Visualize", key="save_visualize"):
        save_energy_mood_stress(energy, mood, stress)
        st.success("Your data has been saved! Check the plot below.")
        plot_mood_stress()

    # Main Section: AI Recommendations
    st.image("https://coruzant.com/wp-content/uploads/2022/10/chatbot-robot.jpg", use_container_width=True)

    if st.button("💡 Get Wellness Advice", key="get_wellness_advice"): 
        get_gif()

    st.write("### Automatic Topic Selection")
    topic = determine_video_topic(energy, mood, stress)
    st.write(f"Automatically selected topic: **{topic}**")

    # Fetch and display video recommendations using the reusable function
    get_video_recommendations(topic, "get_videos_user_input")

with manual_user_input:
    st.write("Manual User Input")
    user_input = st.text_input("Enter what you want to get advice on")
    if st.button("Get Advice", key="get_advice_manual_input"):
        get_gif_for_manual()

    st.write("### Manual Topic Selection")
    topic = st.text_input("Enter your topic:", "")
    if not topic:
        st.warning("Please enter a topic to get video recommendations.")

    # Fetch and display video recommendations using the reusable function
    get_video_recommendations(topic, "get_videos_manual_input")

token = get_spotify_token()
# https://open.spotify.com/album/?si=zg9t2z8KQgeseNowt_oQ0w
# Add this before the Music Explorer section
st.markdown("## 📑 Quick Access Playlists")
playlist_categories = {
    "Pop": ["2h6OZ75e61RyaIhby0lkcc", "67kbhvyUfnMbzgX6zRxrPg"],
    "Rap Songs": ["3X8YiiSv8VREfaDFQ011dv","1oGdtupGPi35OLofuHr0kE","6zVDnyx2GYjD4eLNtYEqyt"],
    "kpop" : ["2EoheVFjqIxgJMb8VnDRtZ"],
    "rock" : ["4xqjQwP93eA2wejQvsYoY8", "1DayIaoubhlZ9kiX2mB9So"]
}

# Create tabs for quick access
quick_access_tab, manual_search_tab = st.tabs(["Quick Access", "Manual Search"])

with quick_access_tab:
    # Dropdown for category selection
    selected_category = st.selectbox("Select Category", list(playlist_categories.keys()))
    
    # Get the playlist IDs for the selected category
    selected_playlists = playlist_categories[selected_category]
    
    # Check if it's a list or a single ID
    if isinstance(selected_playlists, list):
        # If it's a list, allow user to select from the list
        selected_id = st.selectbox(
            f"Select {selected_category}",
            selected_playlists,
            format_func=lambda x: f"Option {selected_playlists.index(x) + 1}: {x}"
        )
    else:
        # If it's a single ID, directly display it
        selected_id = selected_playlists
        st.write(f"Selected Playlist ID for {selected_category}: **{selected_id}**")
    
    if st.button("🎵 Load Selected Content"):
        selected_id = selected_id.strip()
        if selected_id:
            with st.spinner("Fetching playlist..."):
                playlist_content = get_playlist(token, selected_id)
            if playlist_content:
                playlist_details, track_links = playlist_content
                st.markdown(f"**Playlist Name:** {playlist_details['name']}")
                st.markdown(f"**Playlist URL:** [Click here]({playlist_details['url']})")
                st.markdown(f"**Description:** {playlist_details['description']}")
                st.markdown(f"**Total Tracks:** {playlist_details['total_tracks']}")
                st.markdown(f"**Owner:** {playlist_details['owner']}")

                if track_links:
                    st.markdown("### 🎵 Playlist Tracks:")
                    st.markdown(track_links, unsafe_allow_html=True)
                else:
                    st.write("No tracks found for the given playlist.")



            else:
                # If not a playlist, try to fetch as an album
                album = get_album_details(token, selected_id)
                album_tracks = get_album_tracks(token, selected_id)
                if album:
                    st.markdown("### 💿 Album ")
                    st.markdown(album)
                    st.markdown("### 💿 Album Tracks:")
                    st.markdown(album_tracks)
        else:
            st.write("Please select a valid ID.")

with manual_search_tab:

    st.markdown("## 🎶 Music Explorer")
    # Input for artist name
    artist = st.text_input("Enter the artist name")

    # Button to find songs
    if st.button("🎧 Find Songs"):
        if artist:
            artist_id = search_artist_id(token, artist)
            songs = get_songs_by_artist(token, artist_id)
            if songs:
                st.write("### Songs by the Artist")
                for idx, song in enumerate(songs):
                    st.write(f"{idx + 1}. {song.get('name')}")
            else:
                st.write("No songs found for the given artist.")
        else:
            st.write("Please enter an artist name.")

    # Button to find albums
    if st.button("🎧 Find Albums"):
        if artist:
            artist_id = search_artist_id(token, artist)
            albums = get_albums_by_artist(token, artist_id)
            if albums:
                st.write("### Albums by the Artist")
                for album in albums:
                    st.write(f"Album Name: {album['name']}, Release Date: {album['release_date']}, "
                            f"Album ID: {album['id']}, Link: {album['link']}")
            else:
                st.write("No albums found for the given artist.")
        else:
            st.write("Please enter an artist name.")


    st.markdown("### 🎧 Find a specific playlist")
    playlist_id = st.text_input("Enter the playlist ID")

    if st.button("🎧 Find Playlist"):
        if playlist_id:
            playlist = get_playlist(token, playlist_id)
            if playlist:
                playlist_details, track_links = playlist
                # Extract and display playlist link
                st.markdown(f"**Playlist Name** {playlist_details['name']}")
                st.markdown(f"**Playlist Url**, {playlist_details['url']}")
            else:
                st.write("Playlist not found.")
        else:
            st.write("Please enter a playlist ID.")

    if st.button("🎧 Find Playlist tracks"):
        if playlist_id:
            result = get_playlist(token, playlist_id)
            if result:
                playlist_details, track_links = result

                # Display playlist details
                st.write(f"**Playlist Name:** {playlist_details['name']}")
                st.write(f"**Description:** {playlist_details['description']}")
                st.write(f"**Total Tracks:** {playlist_details['total_tracks']}")
                st.write(f"**Owner:** {playlist_details['owner']}")

                # Display track links
                if track_links:
                    st.markdown("### 🎵 Playlist Tracks:")
                    st.markdown(track_links, unsafe_allow_html=True)
                else:
                    st.write("No tracks found for the given playlist.")
            else:
                st.write("Failed to fetch playlist. Please check the playlist ID and token.")
        else:
            st.write("Please enter a playlist ID.")


    st.markdown("### 🎧 Find a specific Album")
    album_id = st.text_input("Enter the album ID")

    if st.button("🎧 Find Album"):
        if album_id:
            # Fetch album details
            album_data = get_album_details(token, album_id)  # Make sure to implement this function
            if album_data:
                album_name = album_data.get("name", "N/A")
                album_url = album_data.get("external_urls", {}).get("spotify", "#")
                
                # Display album name with clickable link
                st.markdown(f"### 💿 Album: [{album_name}]({album_url})")
            else:
                st.write("No album found for the given ID.")
        else:
            st.write("Please enter an album ID.")


    if st.button("🎧 Find Album Tracks"):
        if album_id:
            album_tracks = get_album_tracks(token, album_id) 
            if album_tracks:
                st.markdown("### 💿 Album Tracks:")
                st.markdown(album_tracks)
            else:
                st.write("No tracks found for the given album.")
        else:
            st.write("Please enter an album ID.")
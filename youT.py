import requests

def get_video_links(topic):
    api_key = "AIzaSyBkJQed_fJ9jWv95QpfYJiO944KVKuqjMs" 
    search_url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&q={topic}&type=video&order=viewCount&maxResults=5&key={api_key}"

    try:
        response = requests.get(search_url)
        response.raise_for_status()  # Raise HTTPError for bad responses
        videos = response.json().get('items', [])

        if not videos:
            return "No videos found for the topic."

        # Extract video titles and URLs
        video_list = [
            {
                "title": v['snippet']['title'],
                "url": f"https://www.youtube.com/watch?v={v['id']['videoId']}"
            }
            for v in videos
            if 'snippet' in v and 'id' in v and isinstance(v['id'], dict) and 'videoId' in v['id']
        ]

        return video_list if video_list else "No valid videos found for the topic."

    except requests.exceptions.RequestException as e:
        return f"Error fetching videos: {e}"


def determine_video_topic(energy, mood, stress):
    energy = energy.lower()
    mood = mood.lower()
    stress = stress.lower()

    if energy == "high":
        if mood in ["happy", "tired"] and stress in ["low", "no"]:
            return "mr beast latest + dude perfect"
        elif mood in ["anxious", "overwhelmed"] and stress in ["medium", "high"]:
            return "guided relaxation exercises + calming nature videos"
        elif mood == "neutral" and stress in ["low", "no"]:
            return "DIY projects + skill-building tutorials"
        elif mood == "excited" and stress in ["low", "no"]:
            return "adventure vlogs + high-energy activities"
        elif mood == "bored":
            return "creative challenges + interactive content"

    elif energy == "medium":
        if mood in ["happy", "tired"] and stress == "medium":
            return "balanced lifestyle tips + motivational talks"
        elif mood in ["anxious", "overwhelmed"] and stress in ["low", "no"]:
            return "mindfulness practices + light entertainment"
        elif mood == "neutral":
            return "interesting documentaries + thought-provoking discussions"
        elif mood == "bored" and stress in ["low", "no"]:
            return "fun quizzes + trending challenges"

    elif energy == "low":
        if mood == "happy" and stress in ["low", "no"]:
            return "feel-good music playlists + comedy skits"
        elif mood == "tired" and stress in ["low", "no"]:
            return "rejuvenating exercise routines + energy-boosting hacks"
        elif mood in ["sad", "neutral"] and stress in ["medium", "high"]:
            return "positive affirmations + mental health awareness"
        elif mood == "bored":
            return "relaxing puzzles + soothing videos"
        elif stress == "high":
            return "expert advice on stress relief + deep relaxation guides"

    return "personal growth content + trending videos"

import streamlit as st

def get_video_recommendations(topic, button_key):
    """Function to fetch and display video recommendations."""
    if st.button(f"🎥 Get Videos recommendations", key=button_key):
        if topic:
            videos = get_video_links(topic)
            if isinstance(videos, list) and videos:
                st.subheader(f"Recommended Videos for '{topic}'")
                st.markdown("""
                    <style>
                        .video-container {
                            display: flex;
                            flex-wrap: wrap;
                            gap: 20px;
                            justify-content: space-around;
                        }
                        .video-card {
                            width: 250px;
                            border: 1px solid #ddd;
                            border-radius: 10px;
                            overflow: hidden;
                            box-shadow: 2px 2px 8px rgba(0,0,0,0.1);
                            transition: transform 0.2s;
                            background-color: #ffffff;
                        }
                        .video-card:hover {
                            transform: scale(1.05);
                        }
                        .video-info {
                            padding: 10px;
                            text-align: center;
                        }
                        .video-info a {
                            text-decoration: none;
                            color: #4CAF50;
                            font-weight: bold;
                        }
                    </style>
                    <div class='video-container'>
                """, unsafe_allow_html=True)

                for video in videos[:5]:  # Show top 5 videos
                    video_title = video.get('title', 'No Title')
                    video_url = video.get('url', '#')

                    st.markdown(f"""
                        <div class='video-card'>
                            <div class='video-info'>
                                <a href='{video_url}' target='_blank'>{video_title}</a>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)

                st.markdown("</div>", unsafe_allow_html=True)  # Close the container
            else:
                st.error("No videos found or an error occurred.")
        else:
            st.warning("Please provide a valid topic.")
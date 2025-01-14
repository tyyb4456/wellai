import streamlit as st
import google.generativeai as genai
import mimetypes
import time
import tempfile
from PIL import Image
from gtts import gTTS
import requests
import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
import json
from pathlib import Path
import plotly.express as px

# Progress Tracker --> Keeps track of the user's progress and suggests the next steps.

model = genai.GenerativeModel("gemini-2.0-flash-exp")

st.title("🧠 Learn Lens: Second Brain for Students")
st.subheader("An AI-Powered Learning Companion to Boost Your Knowledge")
st.markdown("""
**Welcome to Learn Lens (Second Brain) for students!**  
Select a learning mode below to get started:  
- **Knowledge Explorer**: Summarize and quiz yourself on any topic.  
- **Note-Taking**: Summarize notes, create flashcards, and analyze audio files.  
- **Visual Learning**: Analyze and explain diagrams and flowcharts.  
- **Video Summarization**: Summarize videos and generate quizzes.  
""")

# Add a sidebar for navigation
st.sidebar.title("Navigation")
input_type = st.sidebar.radio("Choose a Feature:", 
                               ["Knowledge Explorer", "Note-Taking", "Visual Learning", "Video Summarization" , "Progress Tracker"])

# input_type = st.selectbox("Select Input Type:", ["Knowledge Explorer", "Note-Taking" , "Visual Learning" , "video Summarization" ])

if input_type == "Knowledge Explorer":
    st.header("🧠 Knowledge Explorer")
    st.subheader("Generate insights, audio, and quizzes for any topic!")
    # Function to generate a summary
    def get_summary(topic):
        prompt = f"Provide a clear, concise, and beginner-friendly explanation of the topic: {topic}. Highlight key points and actionable insights."
        result = model.generate_content(prompt)
        return result.text

    # Function to generate audio from text
    def generate_audio(text):
        tts = gTTS(text)
        audio_file = "audio.mp3"
        tts.save(audio_file)
        return audio_file

    # Function to generate quiz questions
    def generate_quiz(summary):
        prompt = f"""
        Create 5 well-thought-out and engaging questions based on the following topic: 
        {summary}

       Focus on testing the understanding of critical points from the material.
       Avoid options or answers in this step.

       QUESTIONS:
       """

        quiz = model.generate_content(f"{summary}\n{prompt}")
        return quiz.text

    # Function to generate answers for quiz questions
    def generate_answers(quiz):
        prompt = """
        Using the following quiz questions:

        Provide accurate, detailed, and beginner-friendly answers for each question to ensure a deeper understanding.

        ANSWERS:
        """
        answers = model.generate_content([quiz , prompt])
        return answers.text


    def get_video_links(topic):
        api_key = "AIzaSyBkJQed_fJ9jWv95QpfYJiO944KVKuqjMs" 
        search_url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&q={topic}&type=video&maxResults=5&key={api_key}"

        try:
            response = requests.get(search_url)
            response.raise_for_status()  # Raise HTTPError for bad responses
            videos = response.json().get('items', [])
            
            if not videos:
                return "No videos found for the topic."
            
            # Debugging: Check structure of `videos`
            # st.write(videos)  # Uncomment this to see the structure
            
            # Extract video titles and URLs
            video_list = []
            for v in videos:
                if 'snippet' in v and 'id' in v and isinstance(v['id'], dict) and 'videoId' in v['id']:
                    video_list.append({
                        "title": v['snippet']['title'],
                        "url": f"https://www.youtube.com/watch?v={v['id']['videoId']}"
                    })
            if not video_list:
                return "No valid videos found for the topic."
            return video_list

        except requests.exceptions.RequestException as e:
            return f"Error fetching videos: {e}"

    

    # Streamlit UI
    st.header("Gemini - Ask About the Topic")
    user_input = st.text_input("Enter a topic:", key="input")
    
    # Generate summary
    if st.button("🔍 Generate Summary"):
        if user_input.strip():
            summary = get_summary(user_input)
            st.subheader("Summary")
            st.write(summary)
        else:
            st.error("Please enter a topic.")

    # Generate audio
    if st.button("🔈 Generate Audio"):
        if user_input.strip():
            summary = get_summary(user_input)
            audio_file = generate_audio(summary)
            st.write("Audio file generated.")
            st.audio(audio_file, format='audio/mp3')
        else:
            st.error("Please generate a summary first.")

    # Generate quiz
    if st.button("📝 Generate Quiz"):
        if user_input.strip():
            summary = get_summary(user_input)
            quiz = generate_quiz(summary)
            st.subheader("Quiz Questions")
            st.write(quiz)
        else:
            st.error("Please generate a summary first.")

    # Generate answers
    if st.button("💡 Generate Answers"):
        if user_input.strip():
            summary = get_summary(user_input)
            quiz = generate_quiz(summary)
            answers = generate_answers(quiz)
            st.subheader("Quiz Answers")
            st.write(answers)
        else:
            st.error("Please generate a summary and quiz first.")

    # Generate video links
    if st.button("📺 Find Videos"):
        if user_input.strip():
            videos = get_video_links(user_input)
            if isinstance(videos, list):
                st.subheader("Top 3 Videos")
                for video in videos[:3]:
                    st.write(f"[{video['title']}]({video['url']})")
            else:
                st.error(videos)  # Display error message or "No videos found"
        else:
            st.error("Please enter a topic to find videos.")


elif input_type == "Note-Taking":
    st.header("📝 Note-Taking")
    st.subheader("Upload notes or audio to summarize and create flashcards.")

    # Function to summarize the notes
    def summarize_notes(notes):
        prompt = "Summarize the following text into clear, efficient, and easy-to-understand bullet points. Focus on the most critical ideas:"
        response = model.generate_content([notes ,prompt])
        return response.text
    
    def transcribe_audio(uploaded_file):
        mime_type, _ = mimetypes.guess_type(uploaded_file.name)

        if mime_type is None:
            st.error("Could not determine the MIME type of the uploaded file.")

        myfile = genai.upload_file(uploaded_file, mime_type=mime_type)
        prompt = "Transcribe the content of this audio file accurately and structure it in a readable text format."
        result = model.generate_content([myfile,prompt])
        st.markdown(result.text)


    # Function to create flashcards
    def create_flashcards(summary_text):
        prompt = f"""
        Extract key terms and concepts from the following summarized text and format them into flashcards. Each flashcard should have a term on one side and its concise definition or explanation on the other:

        {summary_text}
        """

        response = model.generate_content(prompt)
        return response.text.split("\n")

    def generate_questions(notes):
        prompt = f"Based on these notes, generate 5 follow-up questions to test understanding:\n{notes}"
        response = model.generate_content(prompt)
        return response.text.split("\n")

    # Streamlit UI
    st.title("Note-Taking and AI Analysis")
    st.write("Upload a text file, and our AI will summarize it or create flashcards for you.")

    # File uploader
    uploaded_file = st.file_uploader("Upload your file", type=["txt"])
    if uploaded_file is not None:
        # Save the uploaded file to a temporary directory
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as temp_file:
            temp_file.write(uploaded_file.read())
            file_path = temp_file.name

        st.write("Uploading text file...")
        text_file_genai = genai.upload_file(path=file_path)
        st.success(f"Completed upload: {text_file_genai.uri}")

        st.write("Generating summary for the text...")
        summary = summarize_notes(text_file_genai)

        # Display the response
        st.write("### AI Response")
        st.markdown(summary)


        # Button to generate flashcards
        if st.button("📚 Create Flashcards"):
            if summary is not None:  # Ensure the summary is available
                st.write("Creating flashcards from the summarized notes...")
                flashcards = create_flashcards(summary)
                
                st.subheader("Generated Flashcards")
                for card in flashcards:
                    st.write(f"• {card}")
            else:
                st.error("Please generate the summary first to create flashcards.")

        # Button to generate follow-up questions
        if st.button("🔍 Generate Questions"):
            if summary is not None:  # Ensure the summary is available
                st.write("Generating follow-up questions from the summarized notes...")
                questions = generate_questions(summary)
                
                st.subheader("Generated Questions")
                for question in questions:
                    st.write(f"• {question}")

    st.title("Audio Description with Google Generative AI") 

    # Upload the audio file
    uploaded_file = st.file_uploader("Upload an audio file (e.g., .m4a)", type=["m4a" , "mp3"])

    if uploaded_file is not None:
        
        st.audio(uploaded_file, format="audio/m4a")  # Display the audio player
        st.write("Processing the uploaded audio file...")

        audio_result = transcribe_audio(uploaded_file)
        st.write("### AI Response")
        st.markdown(audio_result)

elif input_type == "Visual Learning":
    st.header("🖼️ Visual Learning")
    def get_gemini_res(inpu, image , prompt):
        if inpu != "":
            reponse = model.generate_content([inpu , image , prompt])
        else:
            reponse = model.generate_content(image)
        return reponse.text

    st.header("Gemini")
    input = st.text_input("input" , key="input")
    uploaded_file = st.file_uploader("choose an image" , type=["jpg" , "jpeg" , "png"])

    image = ""
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="uploaded image" , use_column_width=True)

    submit = st.button("tell me about the image")

    input_prompt = """
    You are a specialized AI assistant for analyzing images. Provide a detailed, step-by-step explanation of the key elements in this image and their significance. If the input question is irrelevant to the image, politely say, 'Sorry, I cannot provide an answer.'
    """

    if submit:
        response = get_gemini_res(input , image , input_prompt)
        st.subheader("the response is")
        st.write(response)


elif input_type =="Video Summarization" :
    st.header("🎥 Video Summarization")
    st.subheader("Upload a video to summarize and create quizzes.")

    video_file = st.file_uploader("Upload your video file", type=["mp4", "avi", "mov"])

    if video_file is not None:

        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{video_file.name.split('.')[-1]}") as temp_file:
            temp_file.write(video_file.read())
            video_path = temp_file.name

        st.write("Uploading file...")
        video_file_genai = genai.upload_file(path=video_path)
        st.success(f"Completed upload: {video_file_genai.uri}")

        st.write("Processing the file. Please wait...")
        while video_file_genai.state.name == "PROCESSING":
            st.write("Processing...")
            time.sleep(10)
            video_file_genai = genai.get_file(video_file_genai.name)

        if video_file_genai.state.name == "FAILED":
            st.error("File processing failed. Please try again.")

        prompt = """
        Analyze the content of this video file and summarize the main ideas in a concise and clear format. After summarizing, create a 5-question quiz with an answer key to test understanding of the summarized content.
        """


        st.write("Making LLM inference request...")
        response = model.generate_content([video_file_genai, prompt],
                                          request_options={"timeout": 600})

        st.write("### AI Response")
        st.markdown(response.text)

elif input_type == "Progress Tracker":
    st.header("🚀 Progress Tracker")
    st.subheader("Track your learning progress and get personalized recommendations.")

    # File to store progress data
    progress_file = Path("user_progress.json")

# Function to load progress data
    def load_progress():
        if progress_file.exists() and progress_file.stat().st_size > 0:  # Check if file exists and is not empty
            try:
                with open(progress_file, "r") as f:
                    return json.load(f)  # Attempt to load JSON data
            except json.JSONDecodeError:  # Handle invalid JSON
                st.warning("Progress file contains invalid data. Resetting progress.")
                return []  # Return an empty list on error
        return []  # Return an empty list if file doesn't exist or is empty


    # Function to save progress data
    def save_progress(progress_list):
        with open(progress_file, "w") as f:
            json.dump(progress_list, f)

    # Function to plot progress history using Plotly
    def plot_progress(progress_list):
        if not progress_list or len(progress_list) < 2:  # Check for sufficient data
            st.warning("Not enough progress data to plot! Please add more updates.")
            return

        # Create a DataFrame for plotting
        df = pd.DataFrame(progress_list, columns=["Progress"])

        # Detect Streamlit's theme mode (light or dark) using Streamlit config
        mode = st.get_option("theme.base")  # Returns "light" or "dark"

        # Set colors based on the theme
        bg_color = "#ffffff" if mode == "light" else "#333333"
        text_color = "#000000" if mode == "light" else "#ffffff"

        # Create the Plotly figure
        fig = px.histogram(
            df,
            x="Progress",
            nbins=10,
            title="Learning Progress Distribution",
            marginal="violin",  # Add a violin plot for better visualization
        )

        # Update layout for theme
        fig.update_layout(
            plot_bgcolor=bg_color,
            paper_bgcolor=bg_color,
            font=dict(color=text_color),
            title=dict(font=dict(size=20)),
            xaxis=dict(title="Progress (%)", gridcolor="#cccccc"),
            yaxis=dict(title="Frequency", gridcolor="#cccccc"),
        )

        # Show the plot in Streamlit
        st.plotly_chart(fig, use_container_width=True)




    # Function to get AI recommendations based on progress
    def get_AI_recommendation(progress):
        prompt = f"""
        You are an expert student mentor and learning coach. A student has reported their learning progress as {progress}% out of 100. Based on their progress level, provide personalized suggestions to:
        
        1. Motivate them to continue their learning journey.
        2. Offer specific strategies to overcome common challenges faced at their current progress level.
        3. Recommend activities or resources that align with their progress to help them improve effectively.
        4. Include an encouraging closing message tailored to their progress level.

        Be concise, positive, and actionable.
        """
        track = model.generate_content(prompt)
        return track.text

    # App UI
    st.title("Progress Tracker")
    st.write("Track and update your learning progress manually.")

    # Load progress data
    progress_data = load_progress()

    # Display current progress history
    st.subheader("Your Progress History")
    if progress_data:
        st.write(progress_data)
    else:
        st.write("No progress recorded yet. Start by adding your progress!")

    # User input for manual progress update
    new_progress = st.slider("Update your progress:", min_value=0, max_value=100, value=0)

    # Save the new progress
    if st.button("Save Progress"):
        progress_data.append(new_progress)
        save_progress(progress_data)
        st.success(f"Progress of {new_progress}% saved!")

    # Plot progress history
    st.subheader("Progress Analysis")
    if st.button("Show Progress Plot"):
        plot_progress(progress_data)

    # Button to get AI recommendations
    if st.button("Get AI Recommendations"):
        if progress_data:
            latest_progress = progress_data[-1]
            recommendation = get_AI_recommendation(progress_data)
            st.subheader("AI Recommendations")
            st.write(recommendation)
        else:
            st.warning("Please update your progress to get personalized recommendations.")


else:
    st.write("some thing wrong")

# Footer
st.markdown("---")
st.markdown("© 2024 LearnWise - Empowering Learning with AI 🌟")


import json
from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st

energy_file = Path("energy_mood_stress_file.json")

# Function to load saved energy, mood, and stress data
def load_energy_mood_stress():
    if energy_file.exists():
        try:
            with open(energy_file, "r") as f:
                data = json.load(f)
                if isinstance(data, dict) and all(key in data for key in ["energy", "mood", "stress"]):
                    return data
        except json.JSONDecodeError:
            pass
    return {"energy": [], "mood": [], "stress": []}

# Function to save mood, stress, and time data
def save_energy_mood_stress(energy, mood, stress):
    
    data = load_energy_mood_stress()
    data["energy"].append(energy)
    data["mood"].append(mood)
    data["stress"].append(stress)
    with open(energy_file, "w") as f:
        json.dump(data, f)



def plot_mood_stress(theme="light"):
    # Load the data
    data = load_energy_mood_stress()
    df = pd.DataFrame(data)

    # Check if the data is available
    if not df.empty:
        # Transform data for plotting
        melted_df = df.melt(var_name="Category", value_name="Value")

        # Set Plotly template based on theme
        template = "plotly_dark" if theme == "dark" else "plotly_white"

        # Create the plot
        fig = px.histogram(
            melted_df, 
            x="Value", 
            color="Category", 
            barmode="overlay", 
            nbins=15, 
            title="Distribution of Energy Level, Mood, and Stress Levels",
            template=template,
            color_discrete_sequence=px.colors.sequential.Viridis
        )

        # Update layout for better readability
        fig.update_layout(
            title_font_size=18,
            xaxis_title="Values",
            yaxis_title="Frequency",
            legend_title="Categories",
            font=dict(size=12),
        )

        # Display the plot in Streamlit
        st.plotly_chart(fig, use_container_width=True)
    else:
        # Handle the case when there is no data
        st.warning("No data available to plot. Please ensure your dataset is not empty.")

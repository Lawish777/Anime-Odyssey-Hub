import streamlit as st
import pandas as pd
import requests
import time
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors
#import speech_recognition as sr
import logging
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import plotly.express as px
from fuzzywuzzy import process
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize session state
if 'page' not in st.session_state:
    st.session_state['page'] = 'landing'
if 'favorites' not in st.session_state:
    st.session_state['favorites'] = []
if 'achievements' not in st.session_state:
    st.session_state['achievements'] = []
if 'theme' not in st.session_state:
    st.session_state['theme'] = 'Cyberpunk'
if 'search_count' not in st.session_state:
    st.session_state['search_count'] = 0
if 'selected_anime' not in st.session_state:
    st.session_state['selected_anime'] = None

# Custom CSS for Anime-Inspired Aesthetic with Theme Support
def set_background_image(image_url=None):
    theme_styles = {
        'Cyberpunk': {
            'background': 'linear-gradient(180deg, #0a0015, #1a0030)',
            'button_color': '#00b7ff',
            'title_color': '#ff4da6',
            'text_color': '#e0e0e0',
            'neon_glow': '0 0 10px #00b7ff, 0 0 20px #ff4da6',
            'retro_font': "'Orbitron', sans-serif",
            'button_glow': 'rgba(0, 183, 255, 0.4)'
        },
        'Pastel': {
            'background': 'linear-gradient(180deg, #ffe6f0, #e6f0ff)',
            'button_color': '#ff99cc',
            'title_color': '#ff6699',
            'text_color': '#333333',
            'neon_glow': '0 0 10px #ff99cc, 0 0 20px #ff6699',
            'retro_font': "'Comfortaa', cursive",
            'button_glow': 'rgba(255, 153, 204, 0.4)'
        },
        'Dark': {
            'background': 'linear-gradient(180deg, #1c2526, #0a0f0f)',
            'button_color': '#4da8da',
            'title_color': '#f4a261',
            'text_color': '#d3d3d3',
            'neon_glow': '0 0 10px #4da8da, 0 0 20px #f4a261',
            'retro_font': "'Rajdhani', sans-serif",
            'button_glow': 'rgba(77, 168, 218, 0.4)'
        },
        'Neon': {
            'background': 'linear-gradient(180deg, #000000, #1a1a1a)',
            'button_color': '#00ff00',
            'title_color': '#ff00ff',
            'text_color': '#ffffff',
            'neon_glow': '0 0 10px #00ff00, 0 0 20px #ff00ff',
            'retro_font': "'Neon', sans-serif",
            'button_glow': 'rgba(0, 255, 0, 0.4)'
        },
        'Retro': {
            'background': 'linear-gradient(180deg, #2c3e50, #3498db)',
            'button_color': '#e74c3c',
            'title_color': '#f1c40f',
            'text_color': '#ecf0f1',
            'neon_glow': '0 0 10px #e74c3c, 0 0 20px #f1c40f',
            'retro_font': "'Permanent Marker', cursive",
            'button_glow': 'rgba(231, 76, 60, 0.4)'
        },
        'Minimalist': {
            'background': 'linear-gradient(180deg, #ffffff, #f5f5f5)',
            'button_color': '#333333',
            'title_color': '#666666',
            'text_color': '#444444',
            'neon_glow': '0 0 10px #333333',
            'retro_font': "'Roboto', sans-serif",
            'button_glow': 'rgba(51, 51, 51, 0.4)'
        }
    }
    current_theme = theme_styles[st.session_state['theme']]

    if image_url:
        css = f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family={current_theme['retro_font']}:wght@700&display=swap');
        .stApp {{
            background: {current_theme['background']};
            overflow: auto;
        }}
        .stApp::before {{
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            background: url("{image_url}") no-repeat center center;
            background-size: cover;
            opacity: 0.4;
            z-index: -2;
        }}
        .stApp::after {{
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            background: linear-gradient(rgba(0, 0, 0, 0.7), rgba(0, 0, 0, 0.7));
            backdrop-filter: blur(8px);
            z-index: -1;
        }}
        /* Landing Page Styling */
        .landing-container {{
            text-align: center;
            padding: 50px 20px;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
        }}
        .hero-title {{
            color: {current_theme['title_color']} !important;
            font-size: 4.5em !important;
            font-family: '{current_theme['retro_font']}', sans-serif;
            text-shadow: {current_theme['neon_glow']}, 0 0 50px rgba(255, 77, 166, 0.5);
            animation: neon-glow 1.5s ease-in-out infinite alternate;
            margin-bottom: 20px;
        }}
        .hero-subtitle {{
            color: {current_theme['text_color']} !important;
            font-size: 1.6em !important;
            font-family: 'Arial', sans-serif;
            text-shadow: 0 0 10px rgba(0, 191, 255, 0.5);
            margin-bottom: 40px;
            max-width: 650px;
        }}
        @keyframes neon-glow {{
            from {{ text-shadow: {current_theme['neon_glow']}, 0 0 20px rgba(255, 77, 166, 0.6), 0 0 30px rgba(255, 77, 166, 0.4); }}
            to {{ text-shadow: 0 0 20px rgba(255, 77, 166, 1), 0 0 40px rgba(255, 77, 166, 0.8), 0 0 60px rgba(255, 77, 166, 0.6); }}
        }}
        /* Streamlit Button Styling for Landing Page */
        .stButton > button {{
            background: transparent !important;
            color: {current_theme['button_color']} !important;
            border: 2px solid {current_theme['button_color']};
            padding: 15px 30px;
            border-radius: 10px;
            font-size: 1.2em;
            font-weight: bold;
            font-family: '{current_theme['retro_font']}', sans-serif;
            letter-spacing: 1px;
            text-transform: uppercase;
            transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            margin: 15px;
            position: relative;
            overflow: hidden;
        }}
        .stButton > button:before {{
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
            transition: all 0.5s ease;
        }}
        .stButton > button:hover {{
            background: {current_theme['button_color']} !important;
            color: #ffffff !important;
            border-color: {current_theme['button_color']};
            transform: scale(1.05) translateY(-3px);
            box-shadow: 0 7px 20px rgba(0, 183, 255, 0.4), 0 0 15px {current_theme['button_color']};
            letter-spacing: 2px;
        }}
        .stButton > button:hover:before {{
            left: 100%;
        }}
        .stButton > button:active {{
            transform: scale(1) translateY(0px);
            box-shadow: 0 3px 10px rgba(0, 183, 255, 0.2);
        }}
        /* General App Styling */
        .stApp h1 {{
            color: {current_theme['title_color']} !important;
            text-shadow: 0 0 10px rgba(255, 77, 166, 0.8), 0 0 20px rgba(255, 77, 166, 0.6) !important;
            font-size: 3em !important;
            font-family: '{current_theme['retro_font']}', sans-serif;
            text-align: center;
            margin-bottom: 20px !important;
        }}
        .stApp h3 {{
            color: {current_theme['button_color']} !important;
            text-shadow: 0 0 8px rgba(0, 183, 255, 0.7) !important;
            font-size: 1.8em !important;
            font-family: 'Arial', sans-serif;
        }}
        .stApp [data-testid="stMarkdown"] p {{
            color: {current_theme['text_color']} !important;
            text-shadow: 0 0 5px rgba(0, 0, 0, 0.5) !important;
            font-size: 1.1em !important;
            font-family: 'Arial', sans-serif;
        }}
        .stApp * {{
            color: {current_theme['text_color']} !important;
            font-family: 'Arial', sans-serif;
        }}
        /* Card Styling for Recommendations */
        .recommendation-card {{
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            padding: 15px;
            margin-bottom: 20px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            border: 1px solid {current_theme['title_color']};
        }}
        .recommendation-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 8px 20px rgba(255, 77, 166, 0.5);
        }}
        .recommendation-card img {{
            border-radius: 10px;
            max-width: 100%;
        }}
        /* Sidebar Styling */
        [data-testid="stSidebar"] {{
            background: {current_theme['background']};
            padding: 20px;
            border-right: 2px solid {current_theme['title_color']};
        }}
        [data-testid="stSidebar"] .stMarkdown h1 {{
            color: {current_theme['title_color']} !important;
            font-size: 28px !important;
            text-align: center;
            text-shadow: 0 0 10px rgba(255, 77, 166, 0.8);
        }}
        [data-testid="stSidebar"] .stMarkdown strong {{
            color: {current_theme['text_color']} !important;
            background: {current_theme['title_color']};
            padding: 8px 12px;
            border-radius: 8px;
            display: inline-block;
            margin: 8px 0;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.3);
        }}
        [data-testid="stSidebar"] .stMarkdown p {{
            color: {current_theme['text_color']} !important;
            font-size: 1em !important;
        }}
        [data-testid="stSidebar"] .stMultiSelect [data-testid="stWidgetLabel"] {{
            color: {current_theme['button_color']} !important;
            font-weight: bold;
            text-shadow: 0 0 5px rgba(0, 0, 0, 0.5);
        }}
        [data-testid="stSidebar"] .stButton > button {{
            background: transparent !important;
            color: {current_theme['title_color']} !important;
            border: 2px solid {current_theme['title_color']};
            padding: 10px 20px;
            border-radius: 10px;
            font-weight: bold;
            transition: all 0.3s ease;
            width: 100%;
            margin: 5px 0;
        }}
        [data-testid="stSidebar"] .stButton > button:hover {{
            background: {current_theme['title_color']} !important;
            color: #ffffff !important;
            transform: scale(1.05);
            box-shadow: 0 0 15px rgba(255, 77, 166, 0.7);
        }}
        [data-testid="stSidebar"] .stCheckbox label {{
            color: {current_theme['button_color']} !important;
            text-shadow: 0 0 5px rgba(0, 0, 0, 0.5);
        }}
        [data-testid="stSidebar"] .stMarkdown h2 {{
            color: {current_theme['button_color']} !important;
            text-shadow: 0 0 8px rgba(0, 183, 255, 0.7);
        }}
        [data-testid="stSidebar"] .stMarkdown li {{
            color: {current_theme['button_color']} !important;
        }}
        /* Selectbox Styling */
        .stSelectbox [data-testid="stWidgetLabel"] {{
            color: {current_theme['button_color']} !important;
            font-weight: bold;
            text-shadow: 0 0 5px rgba(0, 0, 0, 0.5);
        }}
        /* Trailer Video Styling */
        iframe {{
            border-radius: 10px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
            border: 1px solid {current_theme['title_color']};
        }}
        /* Anime Image Styling */
        .anime-image {{
            transition: all 0.3s ease;
            border-radius: 15px;
            border: 3px solid transparent;
            box-shadow: 0 0 15px rgba(0, 183, 255, 0.4);
            max-width: 100%;
            cursor: pointer;
        }}
        .anime-image:hover {{
            transform: scale(1.05);
            border-color: var(--highlight-color);
            box-shadow: 0 0 30px var(--glow-color);
        }}
        .sakamoto-days {{
            --highlight-color: #ff4da6;
            --glow-color: rgba(255, 77, 166, 0.8);
        }}
        .solo-leveling {{
            --highlight-color: #00b7ff;
            --glow-color: rgba(0, 183, 255, 0.8);
        }}
        </style>
        """
    else:
        css = f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family={current_theme['retro_font']}:wght@700&display=swap');
        .stApp {{
            background: {current_theme['background']};
            overflow: auto;
        }}
        /* Landing Page Styling */
        .landing-container {{
            text-align: center;
            padding: 50px 20px;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
        }}
        .hero-title {{
            color: {current_theme['title_color']} !important;
            font-size: 4.5em !important;
            font-family: '{current_theme['retro_font']}', sans-serif;
            text-shadow: {current_theme['neon_glow']}, 0 0 50px rgba(255, 77, 166, 0.5);
            animation: neon-glow 1.5s ease-in-out infinite alternate;
            margin-bottom: 20px;
        }}
        .hero-subtitle {{
            color: {current_theme['text_color']} !important;
            font-size: 1.6em !important;
            org: 'Arial', sans-serif;
            text-shadow: 0 0 10px rgba(0, 191, 255, 0.5);
            margin-bottom: 40px;
            max-width: 650px;
        }}
        @keyframes neon-glow {{
            from {{ text-shadow: {current_theme['neon_glow']}, 0 0 20px rgba(255, 77, 166, 0.6), 0 0 30px rgba(255, 77, 166, 0.4); }}
            to {{ text-shadow: 0 0 20px rgba(255, 77, 166, 1), 0 0 40px rgba(255, 77, 166, 0.8), 0 0 60px rgba(255, 77, 166, 0.6); }}
        }}
        /* Streamlit Button Styling for Landing Page */
        .stButton > button {{
            background: transparent !important;
            color: {current_theme['button_color']} !important;
            border: 2px solid {current_theme['button_color']};
            padding: 15px 30px;
            border-radius: 10px;
            font-size: 1.2em;
            font-weight: bold;
            font-family: '{current_theme['retro_font']}', sans-serif;
            letter-spacing: 1px;
            text-transform: uppercase;
            transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            margin: 15px;
            position: relative;
            overflow: hidden;
        }}
        .stButton > button:before {{
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
            transition: all 0.5s ease;
        }}
        .stButton > button:hover {{
            background: {current_theme['button_color']} !important;
            color: #ffffff !important;
            border-color: {current_theme['button_color']};
            transform: scale(1.05) translateY(-3px);
            box-shadow: 0 7px 20px rgba(0, 183, 255, 0.4), 0 0 15px {current_theme['button_color']};
            letter-spacing: 2px;
        }}
        .stButton > button:hover:before {{
            left: 100%;
        }}
        .stButton > button:active {{
            transform: scale(1) translateY(0px);
            box-shadow: 0 3px 10px rgba(0, 183, 255, 0.2);
        }}
        /* General App Styling */
        .stApp h1 {{
            color: {current_theme['title_color']} !important;
            text-shadow: 0 0 10px rgba(255, 77, 166, 0.8), 0 0 20px rgba(255, 77, 166, 0.6) !important;
            font-size: 3em !important;
            font-family: '{current_theme['retro_font']}', sans-serif;
            text-align: center;
            margin-bottom: 20px !important;
        }}
        .stApp h3 {{
            color: {current_theme['button_color']} !important;
            text-shadow: 0 0 8px rgba(0, 183, 255, 0.7) !important;
            font-size: 1.8em !important;
            font-family: 'Arial', sans-serif;
        }}
        .stApp [data-testid="stMarkdown"] p {{
            color: {current_theme['text_color']} !important;
            text-shadow: 0 0 5px rgba(0, 0, 0, 0.5) !important;
            font-size: 1.1em !important;
            font-family: 'Arial', sans-serif;
        }}
        .stApp * {{
            color: {current_theme['text_color']} !important;
            font-family: 'Arial', sans-serif;
        }}
        /* Card Styling for Recommendations */
        .recommendation-card {{
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            padding: 15px;
            margin-bottom: 20px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            border: 1px solid {current_theme['title_color']};
        }}
        .recommendation-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 8px 20px rgba(255, 77, 166, 0.5);
        }}
        .recommendation-card img {{
            border-radius: 10px;
            max-width: 100%;
        }}
        /* Sidebar Styling */
        [data-testid="stSidebar"] {{
            background: {current_theme['background']};
            padding: 20px;
            border-right: 2px solid {current_theme['title_color']};
        }}
        [data-testid="stSidebar"] .stMarkdown h1 {{
            color: {current_theme['title_color']} !important;
            font-size: 28px !important;
            text-align: center;
            text-shadow: 0 0 10px rgba(255, 77, 166, 0.8);
        }}
        [data-testid="stSidebar"] .stMarkdown strong {{
            color: {current_theme['text_color']} !important;
            background: {current_theme['title_color']};
            padding: 8px 12px;
            border-radius: 8px;
            display: inline-block;
            margin: 8px 0;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.3);
        }}
        [data-testid="stSidebar"] .stMarkdown p {{
            color: {current_theme['text_color']} !important;
            font-size: 1em !important;
        }}
        [data-testid="stSidebar"] .stMultiSelect [data-testid="stWidgetLabel"] {{
            color: {current_theme['button_color']} !important;
            font-weight: bold;
            text-shadow: 0 0 5px rgba(0, 0, 0, 0.5);
        }}
        [data-testid="stSidebar"] .stButton > button {{
            background: transparent !important;
            color: {current_theme['title_color']} !important;
            border: 2px solid {current_theme['title_color']};
            padding: 10px 20px;
            border-radius: 10px;
            font-weight: bold;
            transition: all 0.3s ease;
            width: 100%;
            margin: 5px 0;
        }}
        [data-testid="stSidebar"] .stButton > button:hover {{
            background: {current_theme['title_color']} !important;
            color: #ffffff !important;
            transform: scale(1.05);
            box-shadow: 0 0 15px rgba(255, 77, 166, 0.7);
        }}
        [data-testid="stSidebar"] .stCheckbox label {{
            color: {current_theme['button_color']} !important;
            text-shadow: 0 0 5px rgba(0, 0, 0, 0.5);
        }}
        [data-testid="stSidebar"] .stMarkdown h2 {{
            color: {current_theme['button_color']} !important;
            text-shadow: 0 0 8px rgba(0, 183, 255, 0.7);
        }}
        [data-testid="stSidebar"] .stMarkdown li {{
            color: {current_theme['button_color']} !important;
        }}
        /* Selectbox Styling */
        .stSelectbox [data-testid="stWidgetLabel"] {{
            color: {current_theme['button_color']} !important;
            font-weight: bold;
            text-shadow: 0 0 5px rgba(0, 0, 0, 0.5);
        }}
        /* Trailer Video Styling */
        iframe {{
            border-radius: 10px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
            border: 1px solid {current_theme['title_color']};
        }}
        /* Anime Image Styling */
        .anime-image {{
            transition: all 0.3s ease;
            border-radius: 15px;
            border: 3px solid transparent;
            box-shadow: 0 0 15px rgba(0, 183, 255, 0.4);
            max-width: 100%;
            cursor: pointer;
        }}
        .anime-image:hover {{
            transform: scale(1.05);
            border-color: var(--highlight-color);
            box-shadow: 0 0 30px var(--glow-color);
        }}
        .sakamoto-days {{
            --highlight-color: #ff4da6;
            --glow-color: rgba(255, 77, 166, 0.8);
        }}
        .solo-leveling {{
            --highlight-color: #00b7ff;
            --glow-color: rgba(0, 183, 255, 0.8);
        }}
        </style>
        """
    st.markdown(css, unsafe_allow_html=True)

# Fetch Trending Anime from Jikan API
@st.cache_data(ttl=3600)
def fetch_trending_anime():
    logger.info("Fetching trending anime")
    session = requests.Session()
    retries = Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
    session.mount('https://', HTTPAdapter(max_retries=retries))
    time.sleep(0.34)
    url = "https://api.jikan.moe/v4/top/anime?filter=airing&limit=5"
    try:
        response = session.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        return data.get("data", [])
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch trending anime: {str(e)}")
        return []

# Fetch Poster, Synopsis, and Trailer with improved reliability
@st.cache_data(ttl=3600)
def fetch_anime_trailer_cached(title):
    logger.info(f"Fetching trailer for {title}")
    session = requests.Session()
    retries = Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
    session.mount('https://', HTTPAdapter(max_retries=retries))
    time.sleep(0.34)
    url = f"https://api.jikan.moe/v4/anime?q={title}&limit=1"
    try:
        response = session.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        if data["data"]:
            anime_data = data["data"][0]
            trailer_url = anime_data.get("trailer", {}).get("youtube_id", None)
            if not trailer_url:
                # Fallback for missing trailers
                if title == "Naruto":
                    return "j2hiC9BmJlQ"  # Official Naruto Shippuden Trailer
                elif title == "Death Note":
                    return "NlJZ-YgAt-c"  # Fallback ID for Death Note
                elif title == "One Punch Man":
                    return "atxYe-nOa9w"  # Official One Punch Man Season 1 Trailer
                elif title == "Spy x Family":
                    return "ofXigq9aIpo"  # Fallback ID for Spy x Family
                elif title == "One Piece":
                    return "eEApDotghec"  # New One Piece Trailer
                else:
                    return "dQw4w9WgXcQ"  # Default fallback trailer (e.g., a generic anime trailer)
            return trailer_url
        return "dQw4w9WgXcQ"  # Default fallback if no data is found
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch trailer for {title}: {str(e)}")
        return "dQw4w9WgXcQ"  # Default fallback on error

# Main App Logic
# Landing Page
if st.session_state['page'] == 'landing':
    set_background_image("https://i.imgur.com/8y5X5Zk.jpg")

    # Render header content
    st.markdown("""
    <div class="landing-container">
        <h1 class="hero-title">Anime Odyssey Hub</h1>
        <div class="hero-badges">
            <span class="hero-badge">AI-Powered</span>
            <span class="hero-badge">Personalized</span>
            <span class="hero-badge">Curated</span>
        </div>
        <p class="hero-subtitle">
            Dive into a universe of anime with tailored recommendations, 
            powered by cutting-edge AI and a love for epic stories.
        </p>
        <div class="hero-arrow-down">
            <i class="arrow-down"></i>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Add style for header elements
    st.markdown("""
    <style>
    .hero-badges {
        display: flex;
        justify-content: center;
        gap: 15px;
        margin-bottom: 25px;
    }
    .hero-badge {
        background: linear-gradient(135deg, rgba(255,77,166,0.2), rgba(0,183,255,0.2));
        border: 1px solid rgba(255,255,255,0.3);
        padding: 8px 16px;
        border-radius: 20px;
        font-size: 0.9em;
        font-weight: bold;
        color: white;
        text-transform: uppercase;
        letter-spacing: 1px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1), 0 0 10px rgba(255,77,166,0.4);
        backdrop-filter: blur(8px);
        animation: badge-glow 3s infinite alternate;
    }
    @keyframes badge-glow {
        0% {
            box-shadow: 0 4px 6px rgba(0,0,0,0.1), 0 0 10px rgba(255,77,166,0.4);
        }
        100% {
            box-shadow: 0 4px 6px rgba(0,0,0,0.1), 0 0 20px rgba(0,183,255,0.6);
        }
    }
    .hero-badge:nth-child(1) {
        animation-delay: 0s;
    }
    .hero-badge:nth-child(2) {
        animation-delay: 1s;
    }
    .hero-badge:nth-child(3) {
        animation-delay: 2s;
    }
    .hero-arrow-down {
        margin-top: 40px;
        text-align: center;
    }
    .arrow-down {
        display: inline-block;
        width: 30px;
        height: 30px;
        border-right: 3px solid rgba(255,255,255,0.7);
        border-bottom: 3px solid rgba(255,255,255,0.7);
        transform: rotate(45deg);
        animation: arrow-bounce 2s infinite;
    }
    @keyframes arrow-bounce {
        0%, 20%, 50%, 80%, 100% {
            transform: translateY(0) rotate(45deg);
        }
        40% {
            transform: translateY(-20px) rotate(45deg);
        }
        60% {
            transform: translateY(-10px) rotate(45deg);
        }
    }
    </style>
    """, unsafe_allow_html=True)

    # Custom styling for featured and trending anime sections
    st.markdown("""
    <style>
    .featured-anime-section, .trending-anime-section {
        margin: 50px 0;
        text-align: center;
    }
    .featured-title, .trending-title {
        font-size: 2.5em;
        font-weight: bold;
        margin-bottom: 30px;
        color: #ff4da6;
        text-shadow: 0 0 15px rgba(255, 77, 166, 0.5);
        font-family: 'Orbitron', sans-serif;
    }
    .anime-card {
        border-radius: 15px;
        overflow: hidden;
        transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        margin-bottom: 15px;
        background: rgba(0, 0, 0, 0.2);
        border: 2px solid transparent;
    }
    .anime-card:hover {
        transform: translateY(-10px) scale(1.05);
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3);
        border-color: #ff4da6;
    }
    .anime-title {
        font-family: 'Orbitron', sans-serif;
        font-weight: bold;
        margin-top: 8px;
        text-align: center;
        color: white;
        text-shadow: 0 0 10px rgba(0, 0, 0, 0.5);
    }
    .button-container {
        height: 60px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-top: 10px;
    }
    [data-testid="stButton"] > button {
        background-color: transparent !important;
        color: #00b7ff !important;
        border: 2px solid #00b7ff !important;
        border-radius: 20px !important;
        padding: 8px 16px !important;
        font-weight: bold !important;
        font-family: 'Orbitron', sans-serif !important;
        transition: all 0.3s !important;
        width: 100% !important;
        max-width: 300px !important;
        height: 40px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        margin: 0 auto !important;
        text-align: center !important;
        font-size: 0.8rem !important;
        box-shadow: 0 0 10px rgba(0, 183, 255, 0.3) !important;
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
    }
    [data-testid="stButton"] > button:hover {
        background-color: #00b7ff !important;
        color: white !important;
        box-shadow: 0 0 20px rgba(0, 183, 255, 0.6) !important;
        transform: translateY(-3px) !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # Enhanced featured anime section
    st.markdown("<h2 class='featured-title'>Featured Anime Series</h2>", unsafe_allow_html=True)

    # Create columns for the anime cards
    col1, col2, col3, col4, col5 = st.columns(5)

    # Define the anime data with updated, more reliable image URLs
    featured_anime = [
        {
            "title": "One Punch Man",
            "image": "https://cdn.myanimelist.net/images/anime/12/76049.jpg",
            "col": col1
        },
        {
            "title": "Spy x Family",
            "image": "https://cdn.myanimelist.net/images/anime/1441/122795.jpg",
            "col": col2
        },
        {
            "title": "Death Note",
            "image": "https://cdn.myanimelist.net/images/anime/9/9453.jpg",
            "col": col3
        },
        {
            "title": "Naruto",
            "image": "https://cdn.myanimelist.net/images/anime/13/17405.jpg",
            "col": col4
        },
        {
            "title": "One Piece",
            "image": "https://cdn.myanimelist.net/images/anime/6/73245.jpg",
            "col": col5
        }
    ]

    # Display each anime in its column with styling
    for anime in featured_anime:
        with anime["col"]:
            container = st.container()
            with container:
                st.markdown(f"""
                <div style="text-align: center; margin-bottom: 15px;">
                    <div style="
                        border-radius: 15px;
                        overflow: hidden;
                        margin-bottom: 10px;
                        box-shadow: 0 5px 15px rgba(0,0,0,0.3);
                        transition: transform 0.3s ease;
                        border: 2px solid #ff4da6;
                        background: rgba(0,0,0,0.3);
                        height: 250px;
                    ">
                        <img src="{anime['image']}" 
                            style="width: 100%; height: 100%; object-fit: cover; display: block;"
                            alt="Featured Anime">
                    </div>
                </div>
                """, unsafe_allow_html=True)
                st.markdown('<div class="button-container">', unsafe_allow_html=True)
                if st.button("VIEW", key=f"view_{anime['title']}"):
                    st.session_state['page'] = 'main'
                    st.session_state['selected_anime'] = anime['title']
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

    # Display Trending Anime in card format
    st.markdown("<h2 class='trending-title'>Trending Now</h2>", unsafe_allow_html=True)

    with st.spinner("Loading trending anime..."):
        trending_anime = fetch_trending_anime()
        if trending_anime:
            col1, col2, col3, col4, col5 = st.columns(5)
            columns = [col1, col2, col3, col4, col5]
            for idx, anime in enumerate(trending_anime[:5]):
                title = anime['title']
                image_url = anime.get('images', {}).get('jpg', {}).get('large_image_url',
                                                                       'https://via.placeholder.com/150')
                with columns[idx]:
                    container = st.container()
                    with container:
                        st.markdown(f"""
                        <div style="text-align: center; margin-bottom: 15px;">
                            <div style="
                                border-radius: 15px;
                                overflow: hidden;
                                margin-bottom: 10px;
                                box-shadow: 0 5px 15px rgba(0,0,0,0.3);
                                transition: transform 0.3s ease;
                                border: 2px solid #ff4da6;
                                background: rgba(0,0,0,0.3);
                                height: 250px;
                            ">
                                <img src="{image_url}" 
                                    style="width: 100%; height: 100%; object-fit: cover; display: block;"
                                    alt="Trending Anime">
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        st.markdown('<div class="button-container">', unsafe_allow_html=True)
                        if st.button(f"VIEW", key=f"trending_view_{idx}_{title}"):
                            st.session_state['page'] = 'main'
                            st.session_state['selected_anime'] = title
                            st.rerun()
                        st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style='text-align: center; padding: 30px;'>
                <div style='font-size: 1.2em; color: #ff4da6;'>
                    Unable to fetch trending anime at this time.
                </div>
            </div>
            """, unsafe_allow_html=True)

    # Navigation buttons using Streamlit buttons
    st.markdown("""
    <div class="nav-buttons-container">
        <div class="nav-title">Ready to Begin Your Anime Journey?</div>
        <div class="nav-buttons-row">
            <div class="nav-button-wrapper start-exploring"></div>
            <div class="nav-button-wrapper learn-more"></div>
        </div>
    </div>
    <style>
    .nav-buttons-container {
        text-align: center;
        margin: 80px auto 60px auto;
        padding: 40px;
        max-width: 900px;
        background: linear-gradient(135deg, rgba(255, 77, 166, 0.2), rgba(0, 183, 255, 0.2));
        backdrop-filter: blur(12px);
        border-radius: 25px;
        border: 2px solid rgba(255, 77, 166, 0.5);
        box-shadow: 0 15px 40px rgba(0, 0, 0, 0.4), 0 0 20px rgba(255, 77, 166, 0.3);
        position: relative;
        overflow: hidden;
        animation: container-glow 4s ease-in-out infinite alternate;
    }
    .nav-buttons-container::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: linear-gradient(45deg, transparent, rgba(255, 255, 255, 0.1), transparent);
        opacity: 0.5;
        z-index: -1;
        animation: shimmer 6s infinite linear;
    }
    .nav-title {
        font-size: 2.2em;
        font-weight: bold;
        margin-bottom: 40px;
        color: #ff4da6;
        text-shadow: 0 0 15px rgba(255, 77, 166, 0.8), 0 0 25px rgba(0, 183, 255, 0.5);
        font-family: 'Orbitron', sans-serif;
        letter-spacing: 2px;
        animation: title-pulse 3s ease-in-out infinite;
    }
    .nav-buttons-row {
        display: flex;
        justify-content: center;
        gap: 40px;
        flex-wrap: wrap;
    }
    .nav-button-wrapper {
        position: relative;
        width: 200px;
    }
    .nav-button-wrapper [data-testid="stButton"] > button {
        background: transparent !important;
        color: #00b7ff !important;
        border: 3px solid #00b7ff !important;
        padding: 15px 35px !important;
        border-radius: 50px !important;
        font-size: 1.3em !important;
        font-weight: bold !important;
        font-family: 'Orbitron', sans-serif !important;
        text-transform: uppercase !important;
        letter-spacing: 2px !important;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
        width: 100% !important;
        height: 60px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        box-shadow: 0 0 15px rgba(0, 183, 255, 0.5) !important;
        position: relative !important;
        overflow: hidden !important;
    }
    .nav-button-wrapper [data-testid="stButton"] > button:before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
        transition: all 0.6s ease;
    }
    .nav-button-wrapper [data-testid="stButton"] > button:hover {
        background: #00b7ff !important;
        color: #ffffff !important;
        transform: scale(1.1) translateY(-5px) !important;
        box-shadow: 0 10px 25px rgba(0, 183, 255, 0.7), 0 0 30px rgba(255, 77, 166, 0.5) !important;
        border-color: #ff4da6 !important;
    }
    .nav-button-wrapper [data-testid="stButton"] > button:hover:before {
        left: 100%;
    }
    .nav-button-wrapper [data-testid="stButton"] > button:active {
        transform: scale(1) translateY(0) !important;
        box-shadow: 0 5px 15px rgba(0, 183, 255, 0.3) !important;
    }
    .start-exploring [data-testid="stButton"] > button {
        animation: pulse-start 2s infinite;
    }
    .learn-more [data-testid="stButton"] > button {
        animation: pulse-learn 2.5s infinite;
    }
    @keyframes container-glow {
        0% { box-shadow: 0 15px 40px rgba(0, 0, 0, 0.4), 0 0 20px rgba(255, 77, 166, 0.3); }
        100% { box-shadow: 0 20px 50px rgba(0, 0, 0, 0.5), 0 0 30px rgba(0, 183, 255, 0.5); }
    }
    @keyframes shimmer {
        0% { transform: translateX(-100%); }
        100% { transform: translateX(100%); }
    }
    @keyframes title-pulse {
        0% { transform: scale(1); text-shadow: 0 0 15px rgba(255, 77, 166, 0.8); }
        50% { transform: scale(1.05); text-shadow: 0 0 25px rgba(255, 77, 166, 1); }
        100% { transform: scale(1); text-shadow: 0 0 15px rgba(255, 77, 166, 0.8); }
    }
    @keyframes pulse-start {
        0% { box-shadow: 0 0 15px rgba(0, 183, 255, 0.5); }
        50% { box-shadow: 0 0 25px rgba(0, 183, 255, 0.8); }
        100% { box-shadow: 0 0 15px rgba(0, 183, 255, 0.5); }
    }
    @keyframes pulse-learn {
        0% { box-shadow: 0 0 15px rgba(255, 77, 166, 0.5); }
        50% { box-shadow: 0 0 25px rgba(255, 77, 166, 0.8); }
        100% { box-shadow: 0 0 15px rgba(255, 77, 166, 0.5); }
    }
    @media (max-width: 768px) {
        .nav-buttons-row {
            flex-direction: column;
            align-items: center;
            gap: 20px;
        }
        .nav-title {
            font-size: 1.8em;
        }
        .nav-button-wrapper [data-testid="stButton"] > button {
            font-size: 1.1em !important;
            padding: 12px 25px !important;
            width: 100% !important;
            height: 50px !important;
        }
    }
    </style>
    """, unsafe_allow_html=True)

    # Place Streamlit buttons inside the navigation container
    col1, col2 = st.columns([1, 1])
    with col1:
        with st.container():
            st.markdown('<div class="nav-button-wrapper start-exploring">', unsafe_allow_html=True)
            if st.button("Start Exploring", key="start_exploring"):
                st.session_state['page'] = 'main'
                set_background_image()
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        with st.container():
            st.markdown('<div class="nav-button-wrapper learn-more">', unsafe_allow_html=True)
            if st.button("Learn More", key="learn_more"):
                st.session_state['page'] = 'about'
                set_background_image()
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
# About Page
elif st.session_state['page'] == 'about':
    set_background_image("https://i.imgur.com/8y5X5Zk.jpg")
    st.markdown("""
    <div class="landing-container">
        <h1 class="hero-title">About Anime Odyssey Hub</h1>
        <p class="hero-subtitle">
            Anime Odyssey Hub is your ultimate destination for discovering anime tailored to your tastes. 
            Using a powerful recommendation engine, we analyze genres, synopses, and more to suggest 
            anime you'll love. Features include voice search, detailed anime info, trailers, and a 
            downloadable watchlist.
        </p>
        <p class="hero-subtitle">
            Built with love for anime fans, by anime fans.
        </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Back to Home", key="back_to_home"):
            st.session_state['page'] = 'landing'
            set_background_image()
            st.rerun()
    with col2:
        if st.button("Start Exploring", key="start_from_about"):
            st.session_state['page'] = 'main'
            set_background_image()
            st.rerun()

# Main App
else:
    # Load main anime dataset
    @st.cache_data
    def load_data():
        try:
            df = pd.read_csv("anime-dataset-2023.csv")
            df['Genres'] = df['Genres'].fillna('')
            df['Name'] = df['Name'].fillna('')
            df['Synopsis'] = df['Synopsis'].fillna('')
            df['Score'] = pd.to_numeric(df['Score'], errors='coerce').fillna(0.0)
            df['Episodes'] = pd.to_numeric(df['Episodes'], errors='coerce').fillna(0).astype(int)
            df = df.drop_duplicates(subset='Name', keep='first')
            return df
        except FileNotFoundError:
            st.error("Anime.csv not found. Please ensure the file is in the correct directory.")
            return pd.DataFrame()
        except Exception as e:
            st.error(f"Error loading data: {str(e)}")
            return pd.DataFrame()

    anime_df = load_data()
    if anime_df.empty:
        st.stop()

    # Load detailed anime info
    @st.cache_data
    def load_review_data():
        try:
            df = pd.read_csv("anime-dataset-2023.csv")
            df['Name'] = df['Name'].fillna('')
            df['Score'] = pd.to_numeric(df['Score'], errors='coerce').fillna(0.0)
            df['Episodes'] = pd.to_numeric(df['Episodes'], errors='coerce').fillna(0).astype(int)
            return df
        except FileNotFoundError:
            st.error("Anime.csv not found for review data.")
            return pd.DataFrame()
        except Exception as e:
            st.error(f"Error loading review data: {str(e)}")
            return pd.DataFrame()

    review_df = load_review_data()

    # Initialize recommendation model
    @st.cache_resource
    def init_recommendation_model():
        tfidf = TfidfVectorizer(stop_words='english')
        combined_features = anime_df['Genres'] + ' ' + anime_df['Synopsis']
        tfidf_matrix = tfidf.fit_transform(combined_features)
        nn_model = NearestNeighbors(metric='cosine', algorithm='brute')
        nn_model.fit(tfidf_matrix)
        return tfidf, tfidf_matrix, nn_model

    tfidf, tfidf_matrix, nn_model = init_recommendation_model()
    indices = pd.Series(anime_df.index, index=anime_df['Name']).drop_duplicates()

    # Recommendation function
    def get_recommendations(title, n=5):
        if title not in indices:
            return f"'{title}' not found.", pd.DataFrame()
        idx = indices[title]
        distances, neighbors = nn_model.kneighbors(tfidf_matrix[idx], n_neighbors=n + 1)
        rec_indices = neighbors.flatten()[1:]
        return anime_df.iloc[rec_indices][['Name', 'Genres', 'Score']]

    # Fetch detailed info
    def get_detailed_info(title):
        info = review_df[review_df['Name'] == title]
        if not info.empty:
            return info.iloc[0]
        return None

    # Popularity-Based Recommendations
    def get_popular_anime(n=5):
        return anime_df[['Name', 'Score', 'Popularity']].sort_values('Score', ascending=False).head(n)

    # Fuzzy Search
    def fuzzy_search(query, choices, limit=5):
        return process.extract(query, choices, limit=5)

    # Sidebar
    st.sidebar.title("Dashboard")
    st.sidebar.markdown(f"Total Anime in Dataset: {len(anime_df)}")
    st.sidebar.markdown(f"Unique Genres: {anime_df['Genres'].str.split(',').explode().nunique()}")

    # Theme Selection
    st.sidebar.subheader("Customize Theme")
    theme = st.sidebar.selectbox("Choose Theme",
                                ["Cyberpunk", "Pastel", "Dark", "Neon", "Retro", "Minimalist"],
                                index=["Cyberpunk", "Pastel", "Dark", "Neon", "Retro", "Minimalist"].index(st.session_state['theme']))
    if theme != st.session_state['theme']:
        st.session_state['theme'] = theme
        st.rerun()

    # Genre Filter
    selected_genre = st.sidebar.multiselect("Filter by Genre",
                                            options=sorted(set(','.join(anime_df['Genres']).split(','))))
    filtered_df = anime_df.copy()
    if selected_genre:
        filtered_df = filtered_df[
            filtered_df['Genres'].apply(lambda g: any(genre.strip() in g for genre in selected_genre))]

    # Advanced Filters
    st.sidebar.subheader("Advanced Filters")
    min_score = st.sidebar.slider("Minimum Score", 0.0, 10.0, 0.0, key="min_score")
    max_episodes = st.sidebar.slider("Max Episodes", 1, 1000, 1000, key="max_episodes")
    studios = st.sidebar.multiselect("Filter by Studio", sorted(set(anime_df['Studios'].dropna())), key="studios")
    filtered_df = filtered_df[
        (filtered_df['Score'] >= min_score) &
        (filtered_df['Episodes'] <= max_episodes)
        ]
    if studios:
        filtered_df = filtered_df[filtered_df['Studios'].isin(studios)]

    # Achievements Display
    st.sidebar.subheader("Achievements")
    if st.session_state['achievements']:
        for achievement in st.session_state['achievements']:
            st.sidebar.markdown(f"🏆 {achievement}")
    else:
        st.sidebar.markdown("No achievements yet. Keep exploring!")

    # Main App UI
    st.title("Anime Recommender System")

    # Back to Landing Page
    if st.button("Back to Home", key="back_to_home_main"):
        st.session_state['page'] = 'landing'
        set_background_image()
        st.rerun()

    # Popularity-Based Recommendations
    st.subheader("Popular Anime")
    with st.spinner("Loading popular anime..."):
        popular_anime = get_popular_anime(5)
        for _, row in popular_anime.iterrows():
            st.markdown(f"- **{row['Name']}** (Score: {row['Score']}, Popularity: {row['Popularity']})")

    # Genre Visualization
    st.subheader("Explore Anime Genres")
    theme_styles = {
        'Cyberpunk': {
            'background': '#0a0015',
            'button_color': '#00b7ff',
            'title_color': '#ff4da6',
            'text_color': '#e0e0e0',
            'bar_colors': ['#ff4da6', '#00b7ff', '#ff00ff', '#00ffcc', '#ff66cc', '#33ccff', '#ff3399', '#00ccff',
                           '#ff99cc', '#66ccff'],
            'hover_color': '#00b7ff'
        },
        'Pastel': {
            'background': '#ffe6f0',
            'button_color': '#ff99cc',
            'title_color': '#ff6699',
            'text_color': '#333333',
            'bar_colors': ['#ff99cc', '#ffb3d9', '#ffccdd', '#ffd6e6', '#ffecf5', '#b3d9ff', '#cce6ff', '#e6f2ff',
                           '#ffccff', '#ffe6ff'],
            'hover_color': '#66ccff'
        },
        'Dark': {
            'background': '#1c2526',
            'button_color': '#4da8da',
            'title_color': '#f4a261',
            'text_color': '#d3d3d3',
            'bar_colors': ['#f4a261', '#e07b39', '#d97336', '#c96633', '#b8592f', '#4da8da', '#4a98c4', '#4788ae',
                           '#f4c261', '#f4d961'],
            'hover_color': '#4da8da'
        },
        'Neon': {
            'background': '#000000',
            'button_color': '#00ff00',
            'title_color': '#ff00ff',
            'text_color': '#ffffff',
            'bar_colors': ['#00ff00', '#ff00ff', '#00ffff', '#ff0000', '#ffff00', '#ff00aa', '#00ffaa', '#ffaa00',
                           '#aa00ff', '#00aaff'],
            'hover_color': '#00ff00'
        },
        'Retro': {
            'background': '#2c3e50',
            'button_color': '#e74c3c',
            'title_color': '#f1c40f',
            'text_color': '#ecf0f1',
            'bar_colors': ['#e74c3c', '#f1c40f', '#2ecc71', '#3498db', '#9b59b6', '#e67e22', '#1abc9c', '#d35400',
                           '#34495e', '#16a085'],
            'hover_color': '#e74c3c'
        },
        'Minimalist': {
            'background': '#ffffff',
            'button_color': '#333333',
            'title_color': '#666666',
            'text_color': '#444444',
            'bar_colors': ['#333333', '#666666', '#999999', '#cccccc', '#e6e6e6', '#f2f2f2', '#d9d9d9', '#b3b3b3',
                           '#808080', '#4d4d4d'],
            'hover_color': '#333333'
        }
    }
    current_theme = theme_styles[st.session_state['theme']]

    genre_counts = anime_df['Genres'].str.split(',').explode().str.strip().value_counts()
    fig = px.bar(
        x=genre_counts.index[:10],
        y=genre_counts.values[:10],
        title="Top 10 Genres",
        labels={'x': 'Genre', 'y': 'Count'},
        color=genre_counts.index[:10],
        color_discrete_sequence=current_theme['bar_colors']
    )
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Orbitron, Arial, sans-serif", size=14, color=current_theme['text_color']),
        title=dict(text="Top 10 Genres", x=0.5, xanchor='center',
                   font=dict(size=24, color=current_theme['title_color'], family="Orbitron, sans-serif")),
        xaxis=dict(title="Genre", tickangle=45, title_font=dict(size=16, color=current_theme['button_color']),
                   tickfont=dict(size=12, color=current_theme['text_color']), gridcolor='rgba(255,255,255,0.1)'),
        yaxis=dict(title="Count", title_font=dict(size=16, color=current_theme['button_color']),
                   tickfont=dict(size=12, color=current_theme['text_color']), gridcolor='rgba(255,255,255,0.1)'),
        hoverlabel=dict(bgcolor=current_theme['hover_color'], font_size=12, font_family="Arial, sans-serif",
                        bordercolor=current_theme['title_color'], font=dict(color='#ffffff')),
        margin=dict(l=50, r=50, t=80, b=100),
        showlegend=False,
        transition=dict(duration=500, easing='cubic-in-out')
    )
    fig.update_traces(
        marker=dict(line=dict(color=current_theme['title_color'], width=2), opacity=0.85),
        hovertemplate="<b>%{x}</b><br>Count: %{y}<extra></extra>",
        selector=dict(mode='markers+text'),
        hoverlabel=dict(namelength=-1)
    )
    st.plotly_chart(fig, use_container_width=True)

    # Fuzzy Search
    st.subheader("Advanced Search")
    search_query = st.text_input("Search Anime (supports typos):", key="fuzzy_search")
    if search_query:
        with st.spinner("Searching anime..."):
            matches = fuzzy_search(search_query, anime_df['Name'].tolist(), 5)
            for match in matches:
                st.markdown(f"- **{match[0]}** (Similarity: {match[1]}%)")

    anime_title = st.selectbox("Select an Anime:",
                               ["Select an anime"] + filtered_df['Name'].sort_values().unique().tolist(),
                               key="anime_select")

    # Voice Search Feature
    # Voice Search Feature
    def voice_search():
        st.subheader("Voice Search")
        st.write("Click the button below to search for anime using your voice.")
        current_theme_state = st.session_state['theme']

        # Add custom CSS for the "Start Voice Search" button
        st.markdown("""
        <style>
        div[data-testid="stButton"][data-testid="stButton"] button[key="voice_search"] {
            background-color: transparent !important;
            color: #00b7ff !important;
            border: 2px solid #00b7ff !important;
            border-radius: 20px !important;
            padding: 10px 1px !important;
            font-weight: bold !important;
            font-family: 'Orbitron', sans-serif !important;
            transition: all 0.3s !important;
            width: 220px !important;
            height: 40px !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            margin: 0 auto !important;
            font-size: 0.70rem !important; /* Reduced font size for better fit */
            letter-spacing: 1px !important;
            box-shadow: 0 0 15px rgba(0, 183, 255, 0.3) !important;
            white-space: nowrap !important;
            overflow: hidden !important;
            text-overflow: ellipsis !important;
        }
        div[data-testid="stButton"][data-testid="stButton"] button[key="voice_search"]:hover {
            background-color: #00b7ff !important;
            color: white !important;
            box-shadow: 0 0 25px rgba(0, 183, 255, 0.7) !important;
            transform: translateY(-3px) !important;
        }
        </style>
        """, unsafe_allow_html=True)

        if st.button("Voice Search", key="voice_search"):
            set_background_image()
            try:
                recognizer = sr.Recognizer()
                microphone = sr.Microphone()
                with st.spinner("Listening for your search..."):
                    with microphone as source:
                        st.info("Listening... Please speak now.")
                        audio = recognizer.listen(source)
                set_background_image()
                try:
                    query = recognizer.recognize_google(audio)
                    st.write(f"You said: {query}")
                    set_background_image()
                    if query in anime_df['Name'].values:
                        return query
                    else:
                        st.error("Anime not found in the dataset.")
                        set_background_image()
                        return None
                except sr.UnknownValueError:
                    st.error("Sorry, I could not understand your speech.")
                    set_background_image()
                    return None
                except sr.RequestError:
                    st.error(
                        "Sorry, there was an issue with the speech recognition service. This may be due to network issues or unsupported platforms.")
                    set_background_image()
                    return None
            except Exception as e:
                st.error(f"Voice search error: {str(e)}")
                set_background_image()
                return None
        if st.session_state['theme'] != current_theme_state:
            st.session_state['theme'] = current_theme_state
            set_background_image()
        return None

    voice_query = voice_search()

    # Check for Achievements
    if len(st.session_state['favorites']) >= 5 and "Collector" not in st.session_state['achievements']:
        st.session_state['achievements'].append("Collector")
        st.sidebar.success("Achievement Unlocked: Collector (Added 5 anime to favorites)!")
    if st.session_state['search_count'] >= 5 and "Explorer" not in st.session_state['achievements']:
        st.session_state['achievements'].append("Explorer")
        st.sidebar.success("Achievement Unlocked: Explorer (Searched 5 anime)!")

    # Show Recommendations
    if anime_title != "Select an anime" or voice_query:
        st.session_state['search_count'] += 1
        selected_anime = voice_query if voice_query else anime_title
        if selected_anime not in anime_df['Name'].values:
            st.error(f"'{selected_anime}' not found in the dataset.")
        else:
            detailed_info = get_detailed_info(selected_anime)
            poster_url = detailed_info['Image URL'] if detailed_info is not None and pd.notnull(
                detailed_info['Image URL']) else None
            synopsis = detailed_info['Synopsis'] if detailed_info is not None and pd.notnull(
                detailed_info['Synopsis']) else "Synopsis not available."
            trailer_url = fetch_anime_trailer_cached(selected_anime)
            set_background_image(poster_url)
            with st.spinner("Fetching recommendations..."):
                result = get_recommendations(selected_anime)
                if isinstance(result, tuple):
                    st.error(result[0])
                else:
                    st.info(f"Anime similar to {selected_anime}:")
                    if poster_url:
                        st.image(poster_url, width=250)
                    synopsis = synopsis if len(synopsis) < 300 else synopsis[:300] + "..."
                    st.markdown(f"Synopsis: {synopsis}")
                    if trailer_url:
                        st.subheader("Trailer")
                        # Offer direct video link first for reliability
                        st.markdown(
                            f"**[📺 Click to Watch Trailer on YouTube](https://www.youtube.com/watch?v={trailer_url})**",
                            unsafe_allow_html=True)

                        # Enhanced iframe with additional parameters for better compatibility
                        video_html = f"""
                        <div style="position: relative; padding-bottom: 56.25%; height: 0; overflow: hidden; max-width: 100%; background-color: #000;">
                            <iframe 
                                style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;"
                                src="https://www.youtube.com/embed/{trailer_url}?autoplay=0&mute=0&controls=1&origin={st._config.get_option('server.baseUrlPath')}&rel=0&modestbranding=1" 
                                title="YouTube video player" 
                                frameborder="0" 
                                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" 
                                allowfullscreen>
                            </iframe>
                        </div>
                        """
                        st.markdown(video_html, unsafe_allow_html=True)

                        # Alternative methods to view the trailer
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown(f"[📺 Watch on YouTube](https://www.youtube.com/watch?v={trailer_url})")
                        with col2:
                            if st.button("🔄 Reload Video", key=f"reload_{trailer_url}"):
                                st.rerun()
                    else:
                        st.markdown("Trailer: Not available.")
                    if detailed_info is not None:
                        st.markdown("---")
                        st.subheader("Detailed Info")
                        st.markdown(f"Type: {detailed_info['Type']}")
                        st.markdown(f"Episodes: {detailed_info['Episodes']}")
                        st.markdown(f"Status: {detailed_info['Status']}")
                        st.markdown(f"Studios: {detailed_info['Studios']}")
                        st.markdown(f"Source: {detailed_info['Source']}")
                        st.markdown(f"Duration: {detailed_info['Duration']}")
                        st.markdown(f"Rating: {detailed_info['Rating']}")
                        st.markdown(f"Rank: {detailed_info['Rank']}")
                        st.markdown(f"Popularity: {detailed_info['Popularity']}")
                        st.markdown(f"Favorites: {detailed_info['Favorites']}")
                        st.markdown(f"Members: {detailed_info['Members']}")
                    fav_key = f"fav_btn_{selected_anime}"
                    if selected_anime not in st.session_state['favorites']:
                        if st.button("Add to Favorites", key=fav_key):
                            if selected_anime not in st.session_state['favorites']:
                                st.session_state['favorites'].append(selected_anime)
                                st.success(f"Added {selected_anime} to your favorites!")
                    else:
                        if st.button("Remove from Favorites", key=fav_key):
                            if selected_anime in st.session_state['favorites']:
                                st.session_state['favorites'].remove(selected_anime)
                                st.warning(f"Removed {selected_anime} from your favorites!")
                    st.subheader("Recommendations")
                    for _, row in result.iterrows():
                        st.markdown('<div class="recommendation-card">', unsafe_allow_html=True)
                        col1, col2 = st.columns([1, 3])
                        with col1:
                            rec_details = get_detailed_info(row['Name'])
                            rec_poster = rec_details['Image URL'] if rec_details is not None and pd.notnull(
                                rec_details['Image URL']) else None
                            if rec_poster:
                                st.image(rec_poster, width=120)
                        with col2:
                            st.markdown(f"### {row['Name']}")
                            st.markdown(f"Genres: {row['Genres']}")
                            st.markdown(f"Score: {row['Score']}")
                            show_details = st.checkbox("Show Details", key=f"details_{row['Name']}")
                            if show_details:
                                rec_details = get_detailed_info(row['Name'])
                                if rec_details is not None:
                                    st.markdown("Detailed Info")
                                    st.markdown(f"Type: {rec_details['Type']}")
                                    st.markdown(f"Episodes: {rec_details['Episodes']}")
                                    st.markdown(f"Status: {rec_details['Status']}")
                                    st.markdown(f"Studios: {rec_details['Studios']}")
                                    st.markdown(f"Source: {rec_details['Source']}")
                                    st.markdown(f"Duration: {rec_details['Duration']}")
                                    st.markdown(f"Rating: {rec_details['Rating']}")
                                    st.markdown(f"Rank: {rec_details['Rank']}")
                                    st.markdown(f"Popularity: {rec_details['Popularity']}")
                                    st.markdown(f"Favorites: {rec_details['Favorites']}")
                                    st.markdown(f"Members: {rec_details['Members']}")
                                else:
                                    st.markdown("Detailed Info: Not available.")
                        st.markdown('</div>', unsafe_allow_html=True)
    else:
        set_background_image()

    # Paginated Favorites Display
    def paginate_list(items, page_size=5):
        for i in range(0, len(items), page_size):
            yield items[i:i + page_size]

    if st.sidebar.checkbox("Show Favorites", key="show_favorites"):
        st.sidebar.subheader("Your Favorite Anime")
        if st.session_state['favorites']:
            page = st.sidebar.number_input("Page", min_value=1, max_value=(len(st.session_state['favorites']) // 5) + 1,
                                          key="favorites_page")
            paginated_favorites = list(paginate_list(st.session_state['favorites'], 5))[page - 1]
            for fav in paginated_favorites:
                st.sidebar.markdown(f"- {fav}")
        else:
            st.sidebar.markdown("No favorites added yet.")

    # Reset Favorites
    if st.sidebar.button("Reset Favorites", key="reset_favorites"):
        st.session_state['favorites'] = []
        st.sidebar.success("Favorites list cleared.")

    # Downloadable Watchlist Feature
    if st.session_state['favorites']:
        try:
            fav_df = pd.DataFrame(st.session_state['favorites'], columns=["Anime Title"])
            csv_data = fav_df.to_csv(index=False, encoding='utf-8')
            st.sidebar.download_button(
                label="Download Favorites as CSV",
                data=csv_data.encode('utf-8'),
                file_name="my_favorites_watchlist.csv",
                mime="text/csv",
                key="download_favorites"
            )
        except Exception as e:
            st.sidebar.error(f"Failed to generate CSV: {str(e)}")
    else:
        st.sidebar.info("No favorites added yet. Add some anime to download your watchlist!")

    # Global CSS for consistent button styling
    st.markdown("""
    <style>
    div[data-testid="stButton"] {
        display: flex;
        justify-content: center;
        margin: 10px 0 20px 0;
    }
    div[data-testid="stButton"] > button {
        background-color: transparent !important;
        color: #00b7ff !important;
        border: 2px solid #00b7ff !important;
        border-radius: 20px !important;
        padding: 10px 20px !important;
        font-weight: bold !important;
        font-family: 'Orbitron', sans-serif !important;
        transition: all 0.3s !important;
        width: 220px !important;
        height: 50px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        margin: 0 auto !important;
        font-size: 0.95rem !important;
        letter-spacing: 1px !important;
        box-shadow: 0 0 15px rgba(0, 183, 255, 0.3) !important;
    }
    div[data-testid="stButton"] > button:hover {
        background-color: #00b7ff !important;
        color: white !important;
        box-shadow: 0 0 25px rgba(0, 183, 255, 0.7) !important;
        transform: translateY(-3px) !important;
    }
    p {
        min-height: 30px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 10px !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # Featured Anime Cards in Main Page
    st.write("Featured Anime Series")
    col1, col2, col3, col4, col5 = st.columns(5)

    # Custom styling for consistent cards and button alignment
    st.markdown("""
    <style>
    .anime-card-main {
        display: flex;
        flex-direction: column;
        align-items: center;
        height: 330px; /* Reduced from 350px to accommodate tighter spacing */
    }
    .anime-image-container {
        height: 250px;
        width: 100%;
        margin-bottom: 10px;
        border-radius: 15px;
        overflow: hidden;
        border: 2px solid #ff4da6;
        transition: transform 0.3s ease;
    }
    .anime-image-container img {
        width: 100%;
        height: 100%;
        object-fit: cover;
    }
    .anime-image-container:hover {
        transform: translateY(-5px);
    }
    .anime-title-container {
        height: 30px; /* Reduced from 40px */
        display: flex;
        align-items: center;
        justify-content: center;
        text-align: center;
        margin-bottom: 5px; /* Reduced from 10px */
    }
    .main-button-container {
        height: 40px; /* Reduced from 60px */
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .main-button-container button {
        background: transparent !important;
        color: var(--button-color) !important;
        border: 2px solid var(--button-color);
        padding: 15px 30px;
        border-radius: 10px;
        font-size: 1.2em;
        font-weight: bold;
        font-family: 'Orbitron', sans-serif;
        letter-spacing: 1px;
        text-transform: uppercase;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        position: relative;
        overflow: hidden;
        width: 100%;
        max-width: 300px;
        height: 50px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto;
        box-shadow: 0 0 15px var(--button-glow);
    }
    .main-button-container button:before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
        transition: all 0.5s ease;
    }
    .main-button-container button:hover {
        background: var(--button-color) !important;
        color: #ffffff !important;
        border-color: var(--button-color);
        transform: scale(1.05) translateY(-3px);
        box-shadow: 0 7px 20px var(--button-glow), 0 0 15px var(--button-color);
        letter-spacing: 2px;
    }
    .main-button-container button:hover:before {
        left: 100%;
    }
    .main-button-container button:active {
        transform: scale(1) translateY(0px);
        box-shadow: 0 3px 10px var(--button-glow);
    }
    </style>
    """, unsafe_allow_html=True)

    # Set theme-specific CSS variables
    current_theme = {
        'Cyberpunk': {
            'button_color': '#00b7ff',
            'button_glow': 'rgba(0, 183, 255, 0.4)'
        },
        'Pastel': {
            'button_color': '#ff99cc',
            'button_glow': 'rgba(255, 153, 204, 0.4)'
        },
        'Dark': {
            'button_color': '#4da8da',
            'button_glow': 'rgba(77, 168, 218, 0.4)'
        },
        'Neon': {
            'button_color': '#00ff00',
            'button_glow': 'rgba(0, 255, 0, 0.4)'
        },
        'Retro': {
            'button_color': '#e74c3c',
            'button_glow': 'rgba(231, 76, 60, 0.4)'
        },
        'Minimalist': {
            'button_color': '#333333',
            'button_glow': 'rgba(51, 51, 51, 0.4)'
        }
    }[st.session_state['theme']]

    st.markdown(f"""
    <style>
    :root {{
        --button-color: {current_theme['button_color']};
        --button-glow: {current_theme['button_glow']};
    }}
    </style>
    """, unsafe_allow_html=True)

    with col1:
        st.markdown("""
        <div class="anime-card-main">
            <div class="anime-image-container">
                <img src="https://cdn.myanimelist.net/images/anime/12/76049.jpg" alt="One Punch Man">
            </div>
            <div class="anime-title-container">
                <p>One Punch Man</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        with st.container():
            st.markdown('<div class="main-button-container">', unsafe_allow_html=True)
            if st.button("VIEW", key="main_view_opm"):
                st.session_state['selected_anime'] = "One Punch Man"
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="anime-card-main">
            <div class="anime-image-container">
                <img src="https://cdn.myanimelist.net/images/anime/1441/122795.jpg" alt="Spy x Family">
            </div>
            <div class="anime-title-container">
                <p>Spy x Family</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        with st.container():
            st.markdown('<div class="main-button-container">', unsafe_allow_html=True)
            if st.button("VIEW", key="main_view_spyx"):
                st.session_state['selected_anime'] = "Spy x Family"
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="anime-card-main">
            <div class="anime-image-container">
                <img src="https://cdn.myanimelist.net/images/anime/9/9453.jpg" alt="Death Note">
            </div>
            <div class="anime-title-container">
                <p>Death Note</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        with st.container():
            st.markdown('<div class="main-button-container">', unsafe_allow_html=True)
            if st.button("VIEW", key="main_view_death"):
                st.session_state['selected_anime'] = "Death Note"
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

    with col4:
        st.markdown("""
        <div class="anime-card-main">
            <div class="anime-image-container">
                <img src="https://cdn.myanimelist.net/images/anime/13/17405.jpg" alt="Naruto">
            </div>
            <div class="anime-title-container">
                <p>Naruto</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        with st.container():
            st.markdown('<div class="main-button-container">', unsafe_allow_html=True)
            if st.button("VIEW", key="main_view_naruto"):
                st.session_state['selected_anime'] = "Naruto"
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

    with col5:
        st.markdown("""
        <div class="anime-card-main">
            <div class="anime-image-container">
                <img src="https://cdn.myanimelist.net/images/anime/6/73245.jpg" alt="One Piece">
            </div>
            <div class="anime-title-container">
                <p>One Piece</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        with st.container():
            st.markdown('<div class="main-button-container">', unsafe_allow_html=True)
            if st.button("VIEW", key="main_view_op"):
                st.session_state['selected_anime'] = "One Piece"
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

    # Show Recommendations based on selection
    if st.session_state['selected_anime'] is not None:
        anime_title = st.session_state['selected_anime']
        st.session_state['search_count'] += 1
        selected_anime = anime_title
        if selected_anime not in anime_df['Name'].values:
            st.error(f"'{selected_anime}' not found in the dataset.")
            st.session_state['selected_anime'] = None
        else:
            detailed_info = get_detailed_info(selected_anime)
            poster_url = detailed_info['Image URL'] if detailed_info is not None and pd.notnull(
                detailed_info['Image URL']) else None
            synopsis = detailed_info['Synopsis'] if detailed_info is not None and pd.notnull(
                detailed_info['Synopsis']) else "Synopsis not available."
            trailer_url = fetch_anime_trailer_cached(selected_anime)
            set_background_image(poster_url)
            with st.spinner("Fetching recommendations..."):
                result = get_recommendations(selected_anime)
                if isinstance(result, tuple):
                    st.error(result[0])
                else:
                    st.info(f"Anime similar to {selected_anime}:")

                    if poster_url:
                        st.image(poster_url, width=250)
                    synopsis = synopsis if len(synopsis) < 300 else synopsis[:300] + "..."
                    st.markdown(f"Synopsis: {synopsis}")

                    if trailer_url:
                        st.subheader("Trailer")
                        # Offer direct video link first for reliability
                        st.markdown(
                            f"**[📺 Click to Watch Trailer on YouTube](https://www.youtube.com/watch?v={trailer_url})**",
                            unsafe_allow_html=True)

                        # Enhanced iframe with additional parameters for better compatibility
                        video_html = f"""
                        <div style="position: relative; padding-bottom: 56.25%; height: 0; overflow: hidden; max-width: 100%; background-color: #000;">
                            <iframe 
                                style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;"
                                src="https://www.youtube.com/embed/{trailer_url}?autoplay=0&mute=0&controls=1&origin={st._config.get_option('server.baseUrlPath')}&rel=0&modestbranding=1" 
                                title="YouTube video player" 
                                frameborder="0" 
                                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" 
                                allowfullscreen>
                            </iframe>
                        </div>
                        """
                        st.markdown(video_html, unsafe_allow_html=True)

                        # Alternative methods to view the trailer
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown(f"[📺 Watch on YouTube](https://www.youtube.com/watch?v={trailer_url})")
                        with col2:
                            if st.button("🔄 Reload Video", key=f"reload_{trailer_url}"):
                                st.rerun()
                    else:
                        st.markdown("Trailer: Not available.")

                    if detailed_info is not None:
                        st.markdown("---")
                        st.subheader("Detailed Info")
                        st.markdown(f"Type: {detailed_info['Type']}")
                        st.markdown(f"Episodes: {detailed_info['Episodes']}")
                        st.markdown(f"Status: {detailed_info['Status']}")
                        st.markdown(f"Studios: {detailed_info['Studios']}")
                        st.markdown(f"Source: {detailed_info['Source']}")
                        st.markdown(f"Duration: {detailed_info['Duration']}")
                        st.markdown(f"Rating: {detailed_info['Rating']}")
                        st.markdown(f"Rank: {detailed_info['Rank']}")
                        st.markdown(f"Popularity: {detailed_info['Popularity']}")
                        st.markdown(f"Favorites: {detailed_info['Favorites']}")
                        st.markdown(f"Members: {detailed_info['Members']}")

                    fav_key = f"fav_btn_{selected_anime}"
                    if selected_anime not in st.session_state['favorites']:
                        if st.button("Add to Favorites", key=fav_key):
                            if selected_anime not in st.session_state['favorites']:
                                st.session_state['favorites'].append(selected_anime)
                                st.success(f"Added {selected_anime} to your favorites!")
                    else:
                        if st.button("Remove from Favorites", key=fav_key):
                            if selected_anime in st.session_state['favorites']:
                                st.session_state['favorites'].remove(selected_anime)
                                st.warning(f"Removed {selected_anime} from your favorites!")

                    st.subheader("Recommendations")
                    for _, row in result.iterrows():
                        st.markdown('<div class="recommendation-card">', unsafe_allow_html=True)
                        col1, col2 = st.columns([1, 3])

                        with col1:
                            rec_details = get_detailed_info(row['Name'])
                            rec_poster = rec_details['Image URL'] if rec_details is not None and pd.notnull(
                                rec_details['Image URL']) else None
                            if rec_poster:
                                st.image(rec_poster, width=120)

                        with col2:
                            st.markdown(f"### {row['Name']}")
                            st.markdown(f"Genres: {row['Genres']}")
                            st.markdown(f"Score: {row['Score']}")

                            show_details = st.checkbox("Show Details", key=f"details_{row['Name']}")
                            if show_details:
                                rec_details = get_detailed_info(row['Name'])
                                if rec_details is not None:
                                    st.markdown("Detailed Info")
                                    st.markdown(f"Type: {rec_details['Type']}")
                                    st.markdown(f"Episodes: {rec_details['Episodes']}")
                                    st.markdown(f"Status: {rec_details['Status']}")
                                    st.markdown(f"Studios: {rec_details['Studios']}")
                                    st.markdown(f"Source: {rec_details['Source']}")
                                    st.markdown(f"Duration: {rec_details['Duration']}")
                                    st.markdown(f"Rating: {rec_details['Rating']}")
                                    st.markdown(f"Rank: {rec_details['Rank']}")
                                    st.markdown(f"Popularity: {rec_details['Popularity']}")
                                    st.markdown(f"Favorites: {rec_details['Favorites']}")
                                    st.markdown(f"Members: {rec_details['Members']}")
                                else:
                                    st.markdown("Detailed Info: Not available.")
                            st.markdown('</div>', unsafe_allow_html=True)

                # Clear selected anime after displaying
                st.session_state['selected_anime'] = None

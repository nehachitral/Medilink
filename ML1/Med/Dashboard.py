import streamlit as st
import sqlite3
from PIL import Image
import numpy as np
import pandas as pd
import plotly.express as px
from streamlit_lottie import st_lottie
import requests
import os

# Streamlit page setup
st.set_page_config(page_title="Health Dashboard", page_icon='👨‍⚕️', layout="wide")

# Helper function to load Lottie animations
def load_lottieurl(url: str):
    try:
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()
    except requests.exceptions.RequestException:
        return None

# Lottie animations
lottie_health = load_lottieurl("https://assets10.lottiefiles.com/packages/lf20_0fy1spgt.json")

# Database connection
conn = sqlite3.connect('user_data.db', check_same_thread=False)
c = conn.cursor()

# Create tables if not exist
c.execute('''CREATE TABLE IF NOT EXISTS users
             (username TEXT, password TEXT, age INTEGER, weight INTEGER, height INTEGER)''')
c.execute('''CREATE TABLE IF NOT EXISTS medical_data
             (username TEXT, file_name TEXT, file_type TEXT, file_path TEXT)''')
conn.commit()

# Background image CSS
background_image_url = "https://www.google.com/url?sa=i&url=https%3A%2F%2Fwww.jabil.com%2Findustries%2Fhealthcare.html&psig=AOvVaw3sCxOLEWfOl1BX0c2vEZwR&ust=1729462260468000&source=images&cd=vfe&opi=89978449&ved=0CBQQjRxqFwoTCKDKspG7m4kDFQAAAAAdAAAAABAZ"  # Replace with your image URL or local image path
st.markdown(
    f"""
    <style>
    .stApp {{
        background-image: url("{background_image_url}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# Function to handle login and registration
def login_page():
    st.title("👨‍⚕️ Welcome to Health Dashboard")
    
    if lottie_health:
        st_lottie(lottie_health, height=150, width=150, key="health")

    menu = ["Login", "Register"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Login":
        st.subheader("🔓 Login Section")
        with st.form(key="login_form"):
            username = st.text_input("User Name", placeholder="Enter your username")
            password = st.text_input("Password", type='password', placeholder="Enter your password")
            login_btn = st.form_submit_button("Login")
        
        if login_btn:
            if username and password:
                c.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
                user_data = c.fetchone()
                if user_data:
                    st.session_state['logged_in'] = True
                    st.session_state['username'] = username
                    st.session_state['user_data'] = user_data
                    st.success(f"Welcome back, {username}!")
                else:
                    st.error("Invalid Username or Password")
            else:
                st.warning("Please enter both username and password.")

    elif choice == "Register":
        st.subheader("📝 Create New Account")
        with st.form(key="register_form"):
            username = st.text_input("User Name", placeholder="Choose a username")
            password = st.text_input("Password", type='password', placeholder="Choose a password")
            age = st.number_input("Age", min_value=0, max_value=120)
            weight = st.number_input("Weight (kg)", min_value=0, max_value=200)
            height = st.number_input("Height (cm)", min_value=0, max_value=250)
            register_btn = st.form_submit_button("Register")
        
        if register_btn:
            if username and password and age and weight and height:
                c.execute("INSERT INTO users (username, password, age, weight, height) VALUES (?, ?, ?, ?, ?)", 
                          (username, password, age, weight, height))
                conn.commit()
                st.success("You have successfully created an account. Go to the Login Menu to login.")
            else:
                st.warning("Please fill in all the fields.")

# If not logged in, show the login page
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if not st.session_state['logged_in']:
    login_page()
else:
    # Show the main dashboard
    username = st.session_state['username']
    user_data = st.session_state['user_data']
    age, weight, height = user_data[2], user_data[3], user_data[4]

    # Calculate BMI
    bmi = round(weight / ((height / 100) ** 2), 2)

    # Health Trends Data (Randomly generated for example)
    health_metrics = {
        'Heart Rate': "104 bpm",
        'Steps': "8000",
        'Blood Pressure': "120/80 mmHg",
        'Sleep Condition': "Good",
        'Overall Health': "Healthy"
    }

    # Sidebar layout
    st.sidebar.title(f"👋 Hello, {username}")
    st.sidebar.subheader("📝 Your Profile")
    st.sidebar.info(f"""
        **Age**: {age} years  
        **Weight**: {weight} kg  
        **Height**: {height} cm  
        **BMI**: {bmi}
    """)

    st.sidebar.markdown("---")
    if st.sidebar.button("🚪 Logout"):
        st.session_state.clear()
        st.experimental_set_query_params()  # Refresh the page to "log out"

    # CSS for boxed metrics
    st.markdown(
        """
        <style>
        .metric-box {
            background-color: #f5f5f5;
            border: 1px solid #ddd;
            padding: 15px 10px;
            border-radius: 5px;
            text-align: center;
            margin-bottom: 15px;
            min-height: 120px;
            max-width: 100%;
        }
        .metric-box h3 {
            margin: 0;
            font-size: 18px;
        }
        .metric-box p {
            margin: 5px 0 0;
            font-size: 24px;
            font-weight: bold;
        }
        .stColumns > div {
            padding-left: 5px;
            padding-right: 5px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Dashboard Layout
    st.title(f"📊 {username}'s Health Dashboard")  # Display the username in the dashboard title
    st.markdown("### Your Profile Details")
    profile_col1, profile_col2, profile_col3, profile_col4 = st.columns(4)
    with profile_col1:
        st.markdown('<div class="metric-box"><h3>Age</h3><p>{} years</p></div>'.format(age), unsafe_allow_html=True)
    with profile_col2:
        st.markdown('<div class="metric-box"><h3>Weight</h3><p>{} kg</p></div>'.format(weight), unsafe_allow_html=True)
    with profile_col3:
        st.markdown('<div class="metric-box"><h3>Height</h3><p>{} cm</p></div>'.format(height), unsafe_allow_html=True)
    with profile_col4:
        st.markdown('<div class="metric-box"><h3>BMI</h3><p>{}</p></div>'.format(bmi), unsafe_allow_html=True)

    # Health Metrics Visualization
    st.markdown("### Health Metrics")
    health_trend_col1, health_trend_col2, health_trend_col3, health_trend_col4, health_trend_col5 = st.columns(5, gap="small")
    with health_trend_col1:
        st.markdown('<div class="metric-box"><h3>❤️ Heart Rate</h3><p>{}</p></div>'.format(health_metrics['Heart Rate']), unsafe_allow_html=True)
    with health_trend_col2:
        st.markdown('<div class="metric-box"><h3>👟 Steps</h3><p>{}</p></div>'.format(health_metrics['Steps']), unsafe_allow_html=True)
    with health_trend_col3:
        st.markdown('<div class="metric-box"><h3>🩺 Blood Pressure</h3><p>{}</p></div>'.format(health_metrics['Blood Pressure']), unsafe_allow_html=True)
    with health_trend_col4:
        st.markdown('<div class="metric-box"><h3>😴 Sleep</h3><p>{}</p></div>'.format(health_metrics['Sleep Condition']), unsafe_allow_html=True)
    with health_trend_col5:
        st.markdown('<div class="metric-box"><h3>🧘‍♂️ Overall Health</h3><p>{}</p></div>'.format(health_metrics['Overall Health']), unsafe_allow_html=True)

    # Generate dummy data for visualization (e.g., steps and mental pressure)
    df = pd.DataFrame({
        'Days': ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'],
        'Steps': np.random.randint(4000, 12000, size=7),
        'Mental Pressure': np.random.uniform(0.2, 1.0, size=7),
        'Screen Time': np.random.uniform(0.5, 1.5, size=7)
    })

    # Display charts
    st.markdown("### Health Trends")
    col1, col2, col3 = st.columns(3)
    with col1:
        fig1 = px.line(df, x='Days', y='Steps', title="📈 Steps Over the Week", markers=True)
        st.plotly_chart(fig1, use_container_width=True)
    with col2:
        fig2 = px.area(df, x='Days', y='Mental Pressure', title="📊 Mental Pressure Over the Week")
        st.plotly_chart(fig2, use_container_width=True)
    with col3:
        fig3 = px.bar(df, x='Days', y=['Mental Pressure', 'Screen Time'], title="📊 Screen Time and Mental Pressure")
        st.plotly_chart(fig3, use_container_width=True)

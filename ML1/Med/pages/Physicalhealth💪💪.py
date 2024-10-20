import streamlit as st
import numpy as np
import pandas as pd
import cv2
import mediapipe as mp
from PIL import Image
from streamlit_option_menu import option_menu

mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

# Streamlit page setup
st.set_page_config(
    page_title="PhysioTherapy Assistant",
    page_icon='🧑‍⚕️',
    layout="wide"
)

# Add custom CSS for improved UI
st.markdown(
    """
    <style>
    .big-font {
        font-size:22px !important;
        font-weight: bold;
        color: #2e4053;
    }
    .analysis-box {
        padding: 20px;
        border-radius: 10px;
        background-color: #f0f2f6;
        border: 2px solid #c3cfd9;
        margin-top: 20px;
    }
    .section-title {
        font-size: 24px;
        font-weight: bold;
        color: #1f618d;
    }
    </style>
    """,
    unsafe_allow_html=True
)

def streamlit_menu():
    with st.sidebar:
        selected = option_menu(
            menu_title="Physiotherapy💪🧑‍⚕️",
            options=["Physio Exercises", "Posture Correction", "Personalized Exercise Plan"],
            icons=["activity", "person-rolodex", "list-task"],
            menu_icon="cast",
            default_index=0
        )
    return selected

def calculate_angle(a, b, c):
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)
    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    angle = np.abs(radians * 180.0 / np.pi)
    if angle > 180.0:
        angle = 360 - angle
    return angle

def physiotherapy_exercises():
    st.title("🧑‍⚕️ Physiotherapy Exercise Tracker")
    exercise = st.selectbox("Choose an exercise", ["Shoulder Raise", "Leg Raise", "Arm Curl"])

    if 'run' not in st.session_state:
        st.session_state['run'] = False

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button(f'Start {exercise}'):
            st.session_state['run'] = True
    with col3:
        if st.button(f'Stop {exercise}'):
            st.session_state['run'] = False

    stframe = st.empty()
    analysis_frame = st.empty()  # Placeholder for exercise analysis output

    cap = cv2.VideoCapture(0)
    counter = 0
    stage = None

    with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
        while cap.isOpened():
            if not st.session_state['run']:
                break
            ret, frame = cap.read()
            if not ret:
                st.write("Failed to capture video")
                break

            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            result = pose.process(image)
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

            try:
                landmarks = result.pose_landmarks.landmark

                if exercise == "Shoulder Raise":
                    elbow = [landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].y]
                    shoulder = [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
                    hip = [landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].y]
                    angle = calculate_angle(elbow, shoulder, hip)
                elif exercise == "Leg Raise":
                    hip = [landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].y]
                    knee = [landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].y]
                    ankle = [landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].y]
                    angle = calculate_angle(hip, knee, ankle)
                elif exercise == "Arm Curl":
                    shoulder = [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
                    elbow = [landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].y]
                    wrist = [landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].y]
                    angle = calculate_angle(shoulder, elbow, wrist)

                # Repetition counting logic
                if angle > 160:
                    stage = 'up'
                if angle < 90 and stage == 'up':
                    stage = 'down'
                    counter += 1

                # Display analysis with bold font for key information
                analysis_frame.markdown(
                    f"""
                    <div class='analysis-box'>
                    <h3 class='big-font'>{exercise} Analysis</h3>
                    <p><strong>Angle:</strong> {angle:.2f}</p>
                    <p><strong>Stage:</strong> {stage}</p>
                    <p><strong>Reps:</strong> {counter}</p>
                    <p><strong>Coordinates:</strong> 
                        <br>- Shoulder: {shoulder} 
                        <br>- Elbow: {elbow if exercise != "Leg Raise" else knee} 
                        <br>- {("Wrist" if exercise == "Arm Curl" else "Hip")}: {wrist if exercise == "Arm Curl" else hip}
                    </p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            except Exception as e:
                print("Error in exercise analysis:", e)

            mp_drawing.draw_landmarks(image, result.pose_landmarks, mp_pose.POSE_CONNECTIONS)
            stframe.image(image, channels='BGR')

    cap.release()

def personalized_exercise_plan():
    st.title("📋 Personalized Exercise Plan")
    
    # Gather user information
    age = st.number_input("Enter your age", min_value=1, max_value=120)
    fitness_level = st.selectbox("Select your current fitness level", ["Beginner", "Intermediate", "Advanced"])
    goal = st.selectbox("Select your goal", ["Increase Strength", "Improve Flexibility", "Rehabilitation", "Weight Loss", "Cardio Endurance", "Muscle Toning"])

    # Display recommendations based on user input
    if st.button("Generate Plan"):
        st.markdown("<h2 class='section-title'>Recommended Exercises Based on Your Inputs:</h2>", unsafe_allow_html=True)
        
        # Example recommendations based on input
        if goal == "Increase Strength":
            if fitness_level == "Beginner":
                st.markdown("- **Bodyweight Squats**: 3 sets of 10 reps")
                st.markdown("- **Push-ups**: 3 sets of 8 reps")
                st.markdown("- **Dumbbell Lunges**: 3 sets of 10 reps each leg")
                st.markdown("- **Dumbbell Rows**: 3 sets of 12 reps")
            elif fitness_level == "Intermediate":
                st.markdown("- **Barbell Squats**: 4 sets of 12 reps")
                st.markdown("- **Bench Press**: 4 sets of 10 reps")
                st.markdown("- **Dumbbell Deadlifts**: 4 sets of 12 reps")
                st.markdown("- **Seated Rows**: 4 sets of 12 reps")
            elif fitness_level == "Advanced":
                st.markdown("- **Deadlifts**: 5 sets of 5 reps")
                st.markdown("- **Weighted Pull-ups**: 4 sets of 8 reps")
                st.markdown("- **Barbell Overhead Press**: 4 sets of 10 reps")
                st.markdown("- **Weighted Lunges**: 4 sets of 12 reps each leg")

        # Additional goals and plans follow a similar pattern
        # ...

def posture_correction():
    st.title("Posture Correction")
    st.write("This module detects your posture and provides corrective feedback.")
    st.write("**Ensure you are visible in front of the camera.**")

    if 'run' not in st.session_state:
        st.session_state['run'] = False

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button('Start Posture Detection'):
            st.session_state['run'] = True
    with col3:
        if st.button('Stop Posture Detection'):
            st.session_state['run'] = False

    stframe = st.empty()
    analysis_frame = st.empty()  # Placeholder for posture feedback

    cap = cv2.VideoCapture(0)

    with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
        while cap.isOpened():
            if not st.session_state['run']:
                break

            ret, frame = cap.read()
            if not ret:
                st.write("Failed to capture video")
                break

            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            result = pose.process(image)
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

            try:
                landmarks = result.pose_landmarks.landmark

                left_shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x, landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
                right_shoulder = [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]

                shoulder_difference = abs(left_shoulder[1] - right_shoulder[1])

                if shoulder_difference > 0.05:
                    analysis_frame.warning("⚠️ Your shoulders are not level. Try to adjust your posture.")
                else:
                    analysis_frame.success("✅ Good posture! Keep it up.")

            except:
                pass

            mp_drawing.draw_landmarks(image, result.pose_landmarks, mp_pose.POSE_CONNECTIONS)
            stframe.image(image, channels='BGR')

    cap.release()

# Main program
selected = streamlit_menu()

if selected == "Physio Exercises":
    physiotherapy_exercises()
elif selected == "Posture Correction":
    posture_correction()
elif selected == "Personalized Exercise Plan":
    personalized_exercise_plan()

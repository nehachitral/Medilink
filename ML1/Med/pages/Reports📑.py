import streamlit as st
from paddleocr import PaddleOCR
import matplotlib.pyplot as plt
from PIL import Image
import numpy as np
import cv2
import sqlite3
import os

# Database connection (You can modify this section to suit your database setup)
conn = sqlite3.connect('user_data.db', check_same_thread=False)
c = conn.cursor()

# Create medical_data table if not exists
c.execute('''CREATE TABLE IF NOT EXISTS medical_data
             (username TEXT, file_name TEXT, file_type TEXT, file_path TEXT)''')
conn.commit()

# Helper function to draw OCR results
def draw_ocr(image, boxes, txts, scores):
    image = image.copy()
    for (box, txt, score) in zip(boxes, txts, scores):
        box = np.array(box).astype(np.int32).reshape(-1, 2)
        cv2.polylines(image, [box], True, color=(0, 255, 0), thickness=2)
        cv2.putText(image, txt, tuple(box[0]), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1, cv2.LINE_AA)
    return image

# Blurriness detection function
def detect_blur(image, threshold=100):
    """Detect if the image is blurry using the Laplacian variance method."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    variance_of_laplacian = cv2.Laplacian(gray, cv2.CV_64F).var()
    return variance_of_laplacian < threshold

# Function to fetch all usernames from the database
def fetch_usernames():
    c.execute("SELECT DISTINCT username FROM medical_data")
    return [row[0] for row in c.fetchall()]

# Title of the app
st.title('PaddleOCR Text Detection and Medical Data Management')

# User authentication section with dropdown
if 'username' not in st.session_state:
    existing_usernames = fetch_usernames()
    st.session_state['username'] = st.selectbox("Select your username if you are a returning user:", options=[""] + existing_usernames, index=0)
    
    if not st.session_state['username']:  # If no existing username is selected, allow manual entry
        st.session_state['username'] = st.text_input("Or, enter a new username to continue:", "")
    
    if st.button("Confirm Username"):
        if st.session_state['username']:
            st.success(f"Welcome, {st.session_state['username']}!")
        else:
            st.error("Please select or enter a username to continue.")

# Ensure the username is available before processing
if st.session_state.get('username'):

    # File uploader for OCR
    st.markdown("### 🔍 OCR Detection: Upload an Image for Text Extraction")
    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

    # Displaying the image and performing OCR
    if uploaded_file is not None:
        img = Image.open(uploaded_file)
        st.image(img, caption='Uploaded Image.', use_column_width=True)

        # Convert the image to numpy array in BGR format (OpenCV format)
        img = np.array(img.convert('RGB'))
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

        # Check for image blurriness
        if detect_blur(img):
            st.warning("The uploaded image is blurry. Please upload a clearer image for better OCR results.")

        # Initialize PaddleOCR
        ocr = PaddleOCR(use_angle_cls=True, lang='en')

        # Perform OCR
        result = ocr.ocr(img, cls=True)

        # Extract and display results
        boxes, texts, scores = [], [], []
        for line in result:
            for res in line:
                boxes.append(res[0])
                texts.append(res[1][0])
                scores.append(res[1][1])

        # Display OCR results
        st.markdown("### Detected Texts:")
        for i, text in enumerate(texts):
            st.write(f"**Text**: {text}, **Confidence**: {scores[i]:.2f}")

        # Draw annotations on the image
        annotated_image = draw_ocr(img, boxes, texts, scores)

        # Convert the annotated image to RGB for display
        annotated_image_rgb = cv2.cvtColor(annotated_image, cv2.COLOR_BGR2RGB)
        st.image(annotated_image_rgb, caption='Annotated Image with OCR Boxes.', use_column_width=True)

    # Medical Data Upload Section
    st.markdown("### 📥 Upload Medical Data")
    st.info("You can upload your medical bills, prescriptions, and reports here.")

    uploaded_files = st.file_uploader("Choose files to upload", accept_multiple_files=True, type=["pdf", "jpg", "jpeg", "png"])

    if uploaded_files:
        upload_folder = "uploaded_files"
        os.makedirs(upload_folder, exist_ok=True)

        for uploaded_file in uploaded_files:
            file_name = uploaded_file.name
            file_type = uploaded_file.type
            file_path = os.path.join(upload_folder, file_name)
            
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # Save file info in the database
            c.execute("INSERT INTO medical_data (username, file_name, file_type, file_path) VALUES (?, ?, ?, ?)", 
                      (st.session_state['username'], file_name, file_type, file_path))
            conn.commit()
            st.success(f"Uploaded {file_name} successfully!")

    # Display stored medical files
    st.markdown("### 🗂 Your Medical Records")
    c.execute("SELECT file_name, file_type, file_path FROM medical_data WHERE username = ?", (st.session_state['username'],))
    records = c.fetchall()

    if records:
        for index, record in enumerate(records):
            file_name, file_type, file_path = record
            st.write(f"**{file_name}** ({file_type})")
            with open(file_path, "rb") as f:
                st.download_button(
                    label=f"Download {file_name}",
                    data=f,
                    file_name=file_name,
                    key=f"download-{index}"  # Ensure unique key by appending the index or another identifier
                )
    else:
        st.info("No medical records found.")
else:
    st.warning("Please enter your username to continue.")

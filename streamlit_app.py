"""
streamlit_app.py - EdgeCam Web Application for Streamlit Community Cloud
-------------------------------------------------------------------------
Provides a free web-based camera edge detection interface hosted on Streamlit Cloud.
"""

import streamlit as st
import cv2
import numpy as np

st.set_page_config(page_title="EdgeCam Studio", page_icon="⚡", layout="centered")

st.title("⚡ EdgeCam - Edge Detection Studio")
st.write("Capture photos with your camera and tune Canny Edge Detection thresholds in real time.")

# Control Sliders
col1, col2 = st.columns(2)
with col1:
    t1 = st.slider("Canny Threshold 1", min_value=0, max_value=255, value=50)
    blur_k = st.slider("Gaussian Blur Kernel", min_value=1, max_value=31, value=5, step=2)
with col2:
    t2 = st.slider("Canny Threshold 2", min_value=0, max_value=255, value=120)
    if st.button("🔄 Reset Defaults"):
        st.rerun()

# Camera Input Component
camera_image = st.camera_input("Camera Feed")

if camera_image is not None:
    # Convert image buffer to OpenCV image matrix
    bytes_data = camera_image.getvalue()
    frame = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)

    # Process Canny Edges
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (blur_k, blur_k), 0)
    edges = cv2.Canny(blur, t1, t2)

    # Display processed edge frame
    st.image(edges, caption="Edge Filter Result", use_column_width=True)

"""
image, video, camera --> frame --> object detection send
show the detection result on the frame and in the streamlit app
"""
 
import os
import cv2
import numpy as np
import streamlit as st
from src.detection_service import DetectionService
from src.audio_service import AudioService
from src.utils import get_video_stream
from tempfile import NamedTemporaryFile
 
 
detection_service = DetectionService()
audio_service = AudioService()
 
st.title("Secure ATM - Helmet Detection App")
st.write("This app detects whether a person is wearing a helmet or not while entering the ATM premises. If a person is detected with a helmet, an alert sound will be played.")
 
st.sidebar.title("Input settings")
 
input_type = st.sidebar.radio("Select input type", ("Image", "Video", "Camera"))
 
 
def process_image(image):
    frame, detections_classes = detection_service.detect(image)
    if "helmet" in detections_classes and "no_helmet" not in detections_classes:
        audio_service.play_beep()
    return frame
 
def process_video(video_file_path):
    cap = cv2.VideoCapture(video_file_path)
 
    stframe = st.empty()
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
 
        frame, detections_classes = detection_service.detect(frame)
        if "helmet" in detections_classes and "no_helmet" not in detections_classes:
            audio_service.play_beep()
 
        stframe.image(frame, channels="BGR", width=700)
    cap.release()
 
 
import time


last_beep_time = 0

def process_camera(camera_source):
    cap = get_video_stream(camera_source)
    stframe = st.empty()
    global last_beep_time
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
 
        frame, detections_classes = detection_service.detect(frame)
        
        if "helmet" in detections_classes and "no_helmet" not in detections_classes:
            current_time = time.time()
            if current_time - last_beep_time >= 1.5:
                audio_service.play_beep()
                last_beep_time = current_time
 
        stframe.image(frame, channels="BGR", width=700)
    cap.release()
 
 
# streamlit app logic
if input_type == "Image":
    uploaded_file = st.sidebar.file_uploader("Upload an image...", type=["jpg", "jpeg", "png"])
    if uploaded_file is not None:
        file_bytes = uploaded_file.read()
        np_array = np.frombuffer(file_bytes, np.uint8)
        image = cv2.imdecode(np_array, cv2.IMREAD_COLOR)
 
        processed_image = process_image(image)
        st.image(processed_image, channels="BGR", width=700)
 
 
if input_type == "Video":
    uploaded_file = st.sidebar.file_uploader("Upload a video...", type=["mp4", "avi", "mov"])
    if uploaded_file is not None:
        with NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
            tmp_file.write(uploaded_file.read())
            video_file_path = tmp_file.name
        process_video(video_file_path)
        os.remove(video_file_path)
 
 
if input_type == "Camera":
    camera_source = st.sidebar.number_input("Camera source (default is 0)", min_value=0, value=0)
    process_camera(camera_source)
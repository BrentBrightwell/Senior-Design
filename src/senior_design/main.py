# main.py
import os
import time
import cv2
import numpy as np
import shutil
from picamera2 import Picamera2
from enum import Enum
from utilities import Mode, handle_detection

# Initialize Picamera2
picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration(main={"format": "XRGB8888", "size": (640, 480)}))
picam2.start()

# Load the DNN model
net = cv2.dnn.readNetFromCaffe("dnn_model/deploy.prototxt", "dnn_model/res10_300x300_ssd_iter_140000.caffemodel")

# Directories for detected and approved faces
detected_faces_dir = "detected_faces"
approved_faces_dir = "approved_faces"
os.makedirs(detected_faces_dir, exist_ok=True)
os.makedirs(approved_faces_dir, exist_ok=True)

mode = Mode.TRAINING  # Set to either Mode.TRAINING or Mode.ACTIVE
approval_status = None  # Initialize approval_status

while True:
    # Capture image from the camera
    im = picam2.capture_array()
    im_rgb = im[:, :, :3].astype(np.uint8)  # Ensure it's in uint8 format

    (h, w) = im_rgb.shape[:2]
    blob = cv2.dnn.blobFromImage(cv2.resize(im_rgb, (300, 300)), 1.0, (300, 300), (104.0, 177.0, 123.0))
    net.setInput(blob)
    detections = net.forward()

    # Process detections
    for i in range(0, detections.shape[2]):
        confidence = detections[0, 0, i, 2]

        if confidence > 0.7:  # Confidence threshold
            box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
            (startX, startY, endX, endY) = box.astype("int")

            # Ensure that coordinates are within image dimensions
            startX = max(startX, 0)
            startY = max(startY, 0)
            endX = min(endX, w)
            endY = min(endY, h)

            # Extract the detected face region of interest (ROI)
            face_roi = im_rgb[startY:endY, startX:endX]
            grey_face_roi = cv2.cvtColor(face_roi, cv2.COLOR_BGR2GRAY)

            # Handle detection based on mode
            handle_detection(grey_face_roi, mode, detected_faces_dir, approved_faces_dir, im_rgb, startX, startY, endX, endY, approval_status)

    # Show the camera feed with rectangles drawn around detected faces
    cv2.imshow("Camera", im_rgb)

    # Check for user input to switch modes
    key = cv2.waitKey(1)
    if key == ord('t'):  # Press 't' to toggle mode
        mode = Mode.ACTIVE if mode == Mode.TRAINING else Mode.TRAINING
        print(f"Switched to {mode.value} mode")
    elif key == 27:  # Press 'Esc' to exit
        break

cv2.destroyAllWindows()

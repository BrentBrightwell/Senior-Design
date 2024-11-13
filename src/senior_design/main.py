import cv2
import os
import numpy as np
from picamera2 import Picamera2
from utilities import Mode, compare_faces, handle_approval
from gui import draw_banners
import threading

# User-adjustable variables
CONFIDENCE_THRESHOLD = 0.7  # Face detection confidence
DETECTED_FACES_DIR = "detected_faces"
APPROVED_FACES_DIR = "approved_faces"

# Create directories for detected and approved faces
os.makedirs(DETECTED_FACES_DIR, exist_ok=True)
os.makedirs(APPROVED_FACES_DIR, exist_ok=True)

# Initialize Picamera2
picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration(main={"format": "XRGB8888", "size": (640, 480)}))
picam2.start()

# Load the DNN model
net = cv2.dnn.readNetFromCaffe("dnn_model/deploy.prototxt", "dnn_model/res10_300x300_ssd_iter_140000.caffemodel")

# Initialize mode and approval flag
mode = Mode.TRAINING
approval_in_progress = False

def initiate_approval(face_roi):
    """Thread target to handle the approval GUI without blocking the main loop."""
    global approval_in_progress
    handle_approval(face_roi, DETECTED_FACES_DIR, APPROVED_FACES_DIR)
    approval_in_progress = False

while True:
    # Capture image from the camera
    im = picam2.capture_array()
    im_rgb = im[:, :, :3].astype(np.uint8)  # Remove alpha channel

    # Draw the mode banner at the top of the feed
    im_rgb = draw_banners(im_rgb, mode)

    (h, w) = im_rgb.shape[:2]
    blob = cv2.dnn.blobFromImage(cv2.resize(im_rgb, (300, 300)), 1.0, (300, 300), (104.0, 177.0, 123.0))
    net.setInput(blob)
    detections = net.forward()

    for i in range(detections.shape[2]):
        confidence = detections[0, 0, i, 2]
        if confidence > CONFIDENCE_THRESHOLD:
            box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
            (startX, startY, endX, endY) = box.astype("int")

            # Ensure bounding box is within image bounds
            startX, startY = max(0, startX), max(0, startY)
            endX, endY = min(w, endX), min(h, endY)

            # Extract detected face and convert to grayscale
            face_roi = im_rgb[startY:endY, startX:endX]
            grey_face_roi = cv2.cvtColor(face_roi, cv2.COLOR_BGR2GRAY)

            if compare_faces(grey_face_roi, APPROVED_FACES_DIR):
                # Approved face found; show green box
                cv2.rectangle(im_rgb, (startX, startY), (endX, endY), (0, 255, 0), 2)
                print("Approved face detected.")
            else:
                # Unapproved face handling
                cv2.rectangle(im_rgb, (startX, startY), (endX, endY), (0, 0, 255), 2)
                if mode == Mode.ACTIVE:
                    print("ALERT! Intruder Detected.")
                elif mode == Mode.TRAINING and not approval_in_progress:
                    approval_in_progress = True
                    threading.Thread(target=initiate_approval, args=(grey_face_roi,)).start()

    # Display the camera feed
    cv2.imshow("Camera", im_rgb)

    # Keypress handling
    key = cv2.waitKey(1) & 0xFF
    if key == ord('t'):
        mode = Mode.ACTIVE if mode == Mode.TRAINING else Mode.TRAINING
        print(f"Switched to {mode.value} mode")
    elif key == 27:  # ESC to quit
        break

    # Check if the window was closed
    if cv2.getWindowProperty("Camera", cv2.WND_PROP_VISIBLE) < 1:
        break

cv2.destroyAllWindows()
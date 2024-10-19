import cv2
import os
import time
import numpy as np
from picamera2 import Picamera2
from utilities import Mode, compare_faces
from gui import show_face_in_gui
import shutil

# User-adjustable variables
CONFIDENCE_THRESHOLD = 0.7  # Face detection confidence
detected_faces_dir = "detected_faces"
approved_faces_dir = "approved_faces"

# Create directories for detected and approved faces
os.makedirs(detected_faces_dir, exist_ok=True)
os.makedirs(approved_faces_dir, exist_ok=True)

# Initialize Picamera2
picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration(main={"format": "XRGB8888", "size": (640, 480)}))
picam2.start()

# Load the DNN model
net = cv2.dnn.readNetFromCaffe("dnn_model/deploy.prototxt", "dnn_model/res10_300x300_ssd_iter_140000.caffemodel")

# Initialize mode
mode = Mode.TRAINING

while True:
    # Capture image from the camera
    im = picam2.capture_array()
    im_rgb = im[:, :, :3].astype(np.uint8)  # Remove alpha channel

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

            if mode == Mode.ACTIVE:
                # Active mode: Check if face is approved
                if compare_faces(grey_face_roi, approved_faces_dir):
                    cv2.rectangle(im_rgb, (startX, startY), (endX, endY), (0, 255, 0), 2)
                    print("Approved face detected.")
                else:
                    cv2.rectangle(im_rgb, (startX, startY), (endX, endY), (0, 0, 255), 2)
                    print("ALERT! Intruder Detected.")
            else:  # Training mode
                if compare_faces(grey_face_roi, approved_faces_dir):
                    print("Approved face detected.")
                else:
                    timestamp = int(time.time())
                    filename = os.path.join(detected_faces_dir, f"face_{timestamp}.jpg")
                    cv2.imwrite(filename, grey_face_roi)
                    print("New face detected. Approve or deny.")

                    # Show the face in the GUI for approval
                    approval_status = show_face_in_gui(grey_face_roi)

                    if approval_status == "approve":
                        approved_filename = os.path.join(approved_faces_dir, f"approved_{timestamp}.jpg")
                        shutil.move(filename, approved_filename)
                        print("Face approved.")
                    elif approval_status == "deny":
                        os.remove(filename)
                        print("Face denied.")

    # Display the camera feed
    cv2.imshow("Camera", im_rgb)

    # Keypress handling
    key = cv2.waitKey(1) & 0xFF
    if key == ord('t'):
        mode = Mode.ACTIVE if mode == Mode.TRAINING else Mode.TRAINING
        print(f"Switched to {mode.value} mode")
    elif key == 27:  # ESC to quit
        break

cv2.destroyAllWindows()
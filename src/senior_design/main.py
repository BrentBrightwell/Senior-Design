# main.py
import cv2
import os
import time
import numpy as np
from picamera2 import Picamera2
from utilities import Mode, compare_faces, handle_approval
from gui import start_gui, draw_banners, process_intruder_alert, initiate_approval
from gpio_devices import initialize_motion_sensor, motion_detected
import threading

# User-adjustable variables
CONFIDENCE_THRESHOLD = 0.7
INTRUDER_DETECTION_THRESHOLD = 1.0
DETECTED_FACES_DIR = "detected_faces"
APPROVED_FACES_DIR = "approved_faces"

# Create directories
os.makedirs(DETECTED_FACES_DIR, exist_ok=True)
os.makedirs(APPROVED_FACES_DIR, exist_ok=True)

# Initialize Picamera2
picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration(main={"format": "RGB888", "size": (640, 480)}))
picam2.start()

# Load DNN model
net = cv2.dnn.readNetFromCaffe("resources/dnn_model/deploy.prototxt", "resources/dnn_model/res10_300x300_ssd_iter_140000.caffemodel")

# Event flags and threads
intruder_start_time = None
approval_in_progress = False

def process_camera_feed(mode):
    global intruder_start_time, approval_in_progress
    while True:
        if motion_detected:
            print("Motion detected!")

        # Capture camera frame
        image = picam2.capture_array()
        image = draw_banners(image, mode)

        (h, w) = image.shape[:2]
        blob = cv2.dnn.blobFromImage(cv2.resize(image, (300, 300)), 1.0, (300, 300), (104.0, 177.0, 123.0))
        net.setInput(blob)
        detections = net.forward()

        for i in range(detections.shape[2]):
            confidence = detections[0, 0, i, 2]
            if confidence > CONFIDENCE_THRESHOLD:
                box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                (startX, startY, endX, endY) = box.astype("int")

                face_roi = image[startY:endY, startX:endX]
                grey_face_roi = cv2.cvtColor(face_roi, cv2.COLOR_BGR2GRAY)

                if compare_faces(grey_face_roi, APPROVED_FACES_DIR):
                    intruder_start_time = None
                    print("Approved face detected.")
                else:
                    if mode == Mode.ACTIVE:
                        if intruder_start_time is None:
                            intruder_start_time = time.time()
                        elif time.time() - intruder_start_time >= INTRUDER_DETECTION_THRESHOLD:
                            process_intruder_alert()
                    elif mode == Mode.TRAINING and not approval_in_progress:
                        approval_in_progress = True
                        threading.Thread(target=initiate_approval, args=(grey_face_roi,), daemon=True).start()

        cv2.imshow("Security Feed", image)
        if cv2.waitKey(1) & 0xFF == 27:
            break

    picam2.stop()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    start_gui(process_camera_feed)

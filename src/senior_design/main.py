import cv2
import os
import time
import numpy as np
from picamera2 import Picamera2
from utilities import Mode, compare_faces, handle_approval
from gui import show_face_in_gui, draw_mode_banner
import shutil

# User-adjustable variables
CONFIDENCE_THRESHOLD = 0.7
DETECTED_FACES_DIR = "detected_faces"
APPROVED_FACES_DIR = "approved_faces"

os.makedirs(DETECTED_FACES_DIR, exist_ok=True)
os.makedirs(APPROVED_FACES_DIR, exist_ok=True)

picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration(main={"format": "XRGB8888", "size": (640, 480)}))
picam2.start()

net = cv2.dnn.readNetFromCaffe("dnn_model/deploy.prototxt", "dnn_model/res10_300x300_ssd_iter_140000.caffemodel")
mode = Mode.TRAINING

approved_face_names = set()

while True:
    im = picam2.capture_array()
    im_rgb = im[:, :, :3].astype(np.uint8)

    im_rgb = draw_mode_banner(im_rgb, mode)

    (h, w) = im_rgb.shape[:2]
    blob = cv2.dnn.blobFromImage(cv2.resize(im_rgb, (300, 300)), 1.0, (300, 300), (104.0, 177.0, 123.0))
    net.setInput(blob)
    detections = net.forward()

    for i in range(detections.shape[2]):
        confidence = detections[0, 0, i, 2]
        if confidence > CONFIDENCE_THRESHOLD:
            box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
            (startX, startY, endX, endY) = box.astype("int")

            startX, startY = max(0, startX), max(0, startY)
            endX, endY = min(w, endX), min(h, endY)

            face_roi = im_rgb[startY:endY, startX:endX]
            grey_face_roi = cv2.cvtColor(face_roi, cv2.COLOR_BGR2GRAY)

            if mode == Mode.ACTIVE:
                if compare_faces(grey_face_roi, APPROVED_FACES_DIR):
                    cv2.rectangle(im_rgb, (startX, startY), (endX, endY), (0, 255, 0), 2)
                    print("Approved face detected.")
                else:
                    cv2.rectangle(im_rgb, (startX, startY), (endX, endY), (0, 0, 255), 2)
                    print("ALERT! Intruder Detected.")
            else:
                if compare_faces(grey_face_roi, APPROVED_FACES_DIR) or f"{startX}_{startY}" in approved_face_names:
                    cv2.rectangle(im_rgb, (startX, startY), (endX, endY), (0, 255, 0), 2)
                else:
                    cv2.rectangle(im_rgb, (startX, startY), (endX, endY), (255, 255, 0), 2)
                    handle_approval(grey_face_roi, DETECTED_FACES_DIR, APPROVED_FACES_DIR, approved_face_names, f"{startX}_{startY}")

    cv2.imshow("Camera", im_rgb)
    key = cv2.waitKey(1) & 0xFF
    if key == ord('t'):
        mode = Mode.ACTIVE if mode == Mode.TRAINING else Mode.TRAINING
        print(f"Switched to {mode.value} mode")
    elif key == 27:
        break

cv2.destroyAllWindows()

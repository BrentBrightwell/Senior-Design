import cv2
import os
import time
import numpy as np
from picamera2 import Picamera2
from utilities import Mode, compare_faces, handle_approval, play_alert_sound
from gui import draw_banners, show_intruder_alert
from gpio_devices import initialize_motion_sensor, motion_detected, activate_siren, deactivate_siren
import threading

# User-adjustable variables
CONFIDENCE_THRESHOLD = 0.7  # Face detection confidence
INTRUDER_DETECTION_THRESHOLD = 1.0  # in seconds
DETECTED_FACES_DIR = "detected_faces"
APPROVED_FACES_DIR = "approved_faces"
INTRUSION_VIDEOS_DIR = "intrusion_videos"

# Create directories for detected and approved faces and videos
os.makedirs(DETECTED_FACES_DIR, exist_ok=True)
os.makedirs(APPROVED_FACES_DIR, exist_ok=True)
os.makedirs(INTRUSION_VIDEOS_DIR, exist_ok=True)

# Initialize Picamera2
picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration(main={"format": "XRGB8888", "size": (640, 480)}))
picam2.start()

# Load the DNN model
net = cv2.dnn.readNetFromCaffe("resources/dnn_model/deploy.prototxt", "resources/dnn_model/res10_300x300_ssd_iter_140000.caffemodel")

# Initialize event acknowledgment 
alert_acknowledged = threading.Event()
stop_threads = threading.Event()
intruder_start_time = None
intruder_alert_active = False

# Start the motion sensor thread
motion_thread = threading.Thread(target=initialize_motion_sensor, daemon=True)
motion_thread.start()

# Initialize mode and approval flag
mode = Mode.TRAINING
approval_in_progress = False

def initiate_approval(face_roi):
    """Thread target to handle the approval GUI without blocking the main loop."""
    global approval_in_progress
    handle_approval(face_roi, DETECTED_FACES_DIR, APPROVED_FACES_DIR)
    approval_in_progress = False

def frame_source():
    """Fetch frames from the Picamera2 feed for video recording."""
    im = picam2.capture_array()
    im_rgb = im[:, :, :3].astype(np.uint8)
    return True, im_rgb

def start_video_recording():
    """Thread for video recording."""
    video_filename = os.path.join(INTRUSION_VIDEOS_DIR, f"intruder_{int(time.time())}.avi")
    fourcc = cv2.VideoWriter_fourcc(*"XVID")
    video_writer = cv2.VideoWriter(video_filename, fourcc, 20.0, (640, 480))
    print(f"Started recording: {video_filename}")
    while not stop_threads.is_set():
        ret, frame = frame_source()
        if ret:
            video_writer.write(frame)
    video_writer.release()
    print(f"Saved video: {video_filename}")

def handle_intruder_alert():
    """Handles the intruder alert, playing sound and recording video."""
    global stop_threads

    # Start alert sound and video recording in separate threads
    sound_thread = threading.Thread(target=play_alert_sound, args=(stop_threads,))
    video_thread = threading.Thread(target=start_video_recording)
    sound_thread.start()
    video_thread.start()

    siren_activated = False
    start_time = time.time()
    # Wait for acknowledgment
    while not alert_acknowledged.is_set():
        if stop_threads.is_set():
            break
        elapsed_time = time.time() - start_time
        if elapsed_time >= 10.0 and not siren_activated:
            print("Activating siren...")
            activate_siren()
            siren_activated = True
        time.sleep(0.1)  # Prevent busy-waiting

    if siren_activated:
        deactivate_siren()
        print("Siren deactivated.")

    # Clean up after acknowledgment
    stop_threads.set()  # Signal threads to stop
    sound_thread.join()
    video_thread.join()
    print("Intruder alert handled.")

while True:
    if motion_detected:
        print("Motion detected in main loop!")

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
                intruder_start_time = None
                intruder_alert_active = False
                alert_acknowledged.clear()
                stop_threads.clear()
                print("Approved face detected.")
            else:
                # Unapproved face handling
                cv2.rectangle(im_rgb, (startX, startY), (endX, endY), (0, 0, 255), 2)
                if mode == Mode.ACTIVE:
                    if intruder_start_time is None:
                        intruder_start_time = time.time()
                    elif time.time() - intruder_start_time >= INTRUDER_DETECTION_THRESHOLD:
                        # Intruder alert trigger
                        if not intruder_alert_active:
                            intruder_alert_active = True
                            alert_acknowledged.clear()
                            stop_threads.clear()
                            threading.Thread(target=handle_intruder_alert, daemon=True).start()
                            threading.Thread(target=show_intruder_alert, args=(alert_acknowledged,), daemon=True).start()
                    print("ALERT! Intruder Detected.")
                elif mode == Mode.TRAINING and not approval_in_progress:
                    approval_in_progress = True
                    threading.Thread(target=initiate_approval, args=(grey_face_roi,)).start()

    if alert_acknowledged.is_set():
        intruder_alert_active = False
        alert_acknowledged.clear()

    # Display the camera feed
    cv2.imshow("Security Feed", im_rgb)

    # Keypress handling
    key = cv2.waitKey(1) & 0xFF
    if key == ord('t'):
        mode = Mode.ACTIVE if mode == Mode.TRAINING else Mode.TRAINING
        print(f"Switched to {mode.value} mode")
    elif key == 27:  # ESC to quit
        break

    # Check if the window was closed
    if cv2.getWindowProperty("Security Feed", cv2.WND_PROP_VISIBLE) < 1:
        break

cv2.destroyAllWindows()
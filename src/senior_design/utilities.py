import cv2
import os
import shutil
import time
from datetime import datetime
import pygame
from enum import Enum
from threading import Event

INTRUSION_VIDEO_DIR = "intrusion_videos"
# Global variable to hold the video writer object
video_writer = None
video_capture = cv2.VideoCapture(0)  # Open the default camera

ALERT_SOUND_PATH = "resources/intruder_alert.wav"
stop_alert_sound_event = Event()

# Define modes as an Enum
class Mode(Enum):
    TRAINING = "training"
    ACTIVE = "active"

def compare_faces(new_face, approved_faces_dir):
    """Compares the new face against the approved faces directory."""
    for file in os.listdir(approved_faces_dir):
        approved_face = cv2.imread(os.path.join(approved_faces_dir, file), cv2.IMREAD_GRAYSCALE)
        if approved_face is None:
            continue

        approved_face = cv2.resize(approved_face, (new_face.shape[1], new_face.shape[0]))

        # Compare histograms
        hist_new_face = cv2.calcHist([new_face], [0], None, [256], [0, 256])
        hist_approved_face = cv2.calcHist([approved_face], [0], None, [256], [0, 256])

        # Compare histograms to find similarity
        similarity = cv2.compareHist(hist_new_face, hist_approved_face, cv2.HISTCMP_CORREL)
        if similarity > 0.9:
            return True
    return False

def handle_approval(face_roi, detected_faces_dir, approved_faces_dir, show_gui_callback):
    """Handles the approval process for a new face."""
    timestamp = int(time.time())
    temp_filename = os.path.join(detected_faces_dir, f"face_{timestamp}.jpg")
    cv2.imwrite(temp_filename, face_roi)
    print("New face detected. Approve or deny.")

    approval_status, first_name, last_name = show_gui_callback(face_roi)  # Get approval status and names

    if approval_status == "approve":
        approved_filename = os.path.join(approved_faces_dir, f"face_{last_name}{first_name}.jpg")  # Use first and last name
        shutil.move(temp_filename, approved_filename)
        print("Face approved.")
    elif approval_status == "deny":
        os.remove(temp_filename)
        print("Face denied.")


def play_alert_sound():
    """Plays an alert sound on loop until acknowledged."""
    pygame.mixer.init()
    alert_sound = pygame.mixer.Sound(ALERT_SOUND_PATH)
    stop_alert_sound_event.clear()
    while not stop_alert_sound_event.is_set():
        alert_sound.play()
        time.sleep(8)  # in seconds

    alert_sound.stop()
    pygame.mixer.quit()


def start_video_recording():
    # Ensure the directory exists
    if not os.path.exists(INTRUSION_VIDEO_DIR):
        os.makedirs(INTRUSION_VIDEO_DIR)

    global video_writer
    video_format = 'avi'  # You can change this to 'mp4' or another format if needed
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    video_filename = os.path.join(INTRUSION_VIDEO_DIR, f"intrusion_{timestamp}.{video_format}")
    
    # Define codec and create VideoWriter object to save video
    fourcc = cv2.VideoWriter_fourcc(*'XVID')  # You can use 'MJPG' or 'MP4V' as well
    video_writer = cv2.VideoWriter(video_filename, fourcc, 20.0, (640, 480))  # Adjust resolution as needed
    
    print(f"Recording started: {video_filename}")


def stop_video_recording():
    """Stops the video recording and releases the video writer."""
    global video_writer
    if video_writer:
        video_writer.release()
        video_writer = None
        print("Recording stopped.")
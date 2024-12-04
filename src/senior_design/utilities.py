import cv2
import os
import shutil
import time
import pygame
import threading
from enum import Enum
from gui import show_face_in_gui
from gpio_devices import activate_siren, deactivate_siren


ALERT_SOUND_PATH = "resources/intruder_alert.wav"
INTRUSION_VIDEO_DIR = "intrusion_videos"
os.makedirs(INTRUSION_VIDEO_DIR, exist_ok=True)

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

def handle_approval(face_roi, detected_faces_dir, approved_faces_dir):
    """Handles the approval process for a new face."""
    timestamp = int(time.time())
    temp_filename = os.path.join(detected_faces_dir, f"face_{timestamp}.jpg")
    cv2.imwrite(temp_filename, face_roi)
    print("New face detected. Approve or deny.")

    approval_status, first_name, last_name = show_face_in_gui(face_roi)  # Get approval status and names

    if approval_status == "approve":
        approved_filename = os.path.join(approved_faces_dir, f"face_{last_name}{first_name}.jpg")  # Use first and last name
        shutil.move(temp_filename, approved_filename)
        print("Face approved.")
    elif approval_status == "deny":
        os.remove(temp_filename)
        print("Face denied.")


def play_alert_sound(alert_acknowledged):
    """Plays the intruder alert sound on loop until acknowledged."""
    pygame.mixer.init()
    alert_sound = pygame.mixer.Sound(ALERT_SOUND_PATH)

    while not alert_acknowledged.is_set():
        alert_sound.play()
        time.sleep(8)  # Sound length or interval
    alert_sound.stop()
    pygame.mixer.quit()


def start_video_recording(video_filename, stop_recording_event, frame_source):
    """Records video from the camera feed until the stop event is triggered."""
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(video_filename, fourcc, 20.0, (640, 480))  # Adjust resolution as needed

    while not stop_recording_event.is_set():
        ret, frame = frame_source()
        if ret:
            out.write(frame)
        time.sleep(0.05)  # Reduce CPU usage

    out.release()


def handle_intruder_alert(frame_source):
    """Handles the intruder alert process."""
    alert_acknowledged = threading.Event()
    stop_recording_event = threading.Event()

    # Start threads for alert sound and video recording
    video_filename = os.path.join(INTRUSION_VIDEO_DIR, f"intrusion_{int(time.time())}.avi")
    threading.Thread(target=play_alert_sound, args=(alert_acknowledged,), daemon=True).start()
    threading.Thread(target=start_video_recording, args=(video_filename, stop_recording_event, frame_source), daemon=True).start()

    # Start siren countdown
    siren_activated = False
    start_time = time.time()

    while not alert_acknowledged.is_set():
        if time.time() - start_time >= 10 and not siren_activated:
            activate_siren()
            siren_activated = True
        time.sleep(0.1)  # Reduce CPU usage

    # Clean up once acknowledged
    stop_recording_event.set()
    if siren_activated:
        deactivate_siren()
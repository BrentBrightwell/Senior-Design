# utilities.py
import os
import cv2
import time
import shutil
from enum import Enum
from gui import show_face_in_gui

class Mode(Enum):
    TRAINING = "training"
    ACTIVE = "active"

def compare_faces(new_face, approved_faces_dir):
    for file in os.listdir(approved_faces_dir):
        approved_face = cv2.imread(os.path.join(approved_faces_dir, file), cv2.IMREAD_GRAYSCALE)
        if approved_face is None:
            continue

        # Resize both faces for comparison
        approved_face = cv2.resize(approved_face, (new_face.shape[1], new_face.shape[0]))

        # Compare histograms
        hist_new_face = cv2.calcHist([new_face], [0], None, [256], [0, 256])
        hist_approved_face = cv2.calcHist([approved_face], [0], None, [256], [0, 256])

        # Compare histograms (returns a similarity score)
        similarity = cv2.compareHist(hist_new_face, hist_approved_face, cv2.HISTCMP_CORREL)

        if similarity > 0.9:
            return True
    return False

def handle_detection(grey_face_roi, mode, detected_faces_dir, approved_faces_dir):
    """Handle the detection of faces based on the current mode."""
    global approval_status
    timestamp = int(time.time())

    if mode == Mode.ACTIVE:
        if compare_faces(grey_face_roi, approved_faces_dir):
            print("Approved face detected.")
        else:
            print("ALERT! Intruder Detected")
    else:  # TRAINING mode
        if compare_faces(grey_face_roi, approved_faces_dir):
            print("Approved face detected.")
        else:
            # Save the face image for approval
            filename = os.path.join(detected_faces_dir, f"face_{timestamp}.jpg")
            cv2.imwrite(filename, grey_face_roi)  # Save only the detected face portion
            print("New face detected. Approve or deny.")

            # Display the face in the GUI window for approval
            approval_status = show_face_in_gui(grey_face_roi)

            if approval_status == "approve":
                print("Face approved.")
                approved_filename = os.path.join(approved_faces_dir, f"approved_{timestamp}.jpg")
                shutil.move(filename, approved_filename)
            elif approval_status == "deny":
                print("Face denied.")
                os.remove(filename)

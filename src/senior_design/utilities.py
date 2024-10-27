import cv2
import os
import time
import numpy as np
from enum import Enum
from gui import show_face_in_gui

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
    filename = os.path.join(detected_faces_dir, f"face_{timestamp}.jpg")
    cv2.imwrite(filename, face_roi)
    print("New face detected. Approve or deny.")

    # Show the face in the GUI for approval
    approval_status = show_face_in_gui(face_roi)

    if approval_status == "approve":
        approved_filename = os.path.join(approved_faces_dir, f"approved_{timestamp}.jpg")
        shutil.move(filename, approved_filename)
        print("Face approved.")
    elif approval_status == "deny":
        os.remove(filename)
        print("Face denied.")

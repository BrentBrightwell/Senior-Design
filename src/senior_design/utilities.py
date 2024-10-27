import cv2
import os
import numpy as np
from enum import Enum
import time
import shutil

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

def handle_approval(face_roi, grey_face_roi, detected_faces_dir, approved_faces_dir, show_face_in_gui):
    """Handles the approval or denial of a detected face."""

    # Save the new face for approval
    timestamp = int(time.time())
    filename = os.path.join(detected_faces_dir, f"face_{timestamp}.jpg")
    cv2.imwrite(filename, grey_face_roi)
    print("New face detected. Approve or deny.")

    # Show the face in the GUI for approval
    approval_status = show_face_in_gui(grey_face_roi)

    # Move the file based on the user's decision
    if approval_status == "approve":
        approved_filename = os.path.join(approved_faces_dir, f"approved_{timestamp}.jpg")
        shutil.move(filename, approved_filename)
        print("Face approved.")
    elif approval_status == "deny":
        os.remove(filename)
        print("Face denied.")
import cv2
import os  
import time
from picamera2 import Picamera2
import numpy as np
import shutil

face_detector = cv2.CascadeClassifier("classifiers/haarcascade_frontalface_default.xml")
cv2.startWindowThread()

picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration(main={"format": 'XRGB8888', "size": (640, 480)}))
picam2.start()

# Directories for detected and approved faces
detected_faces_dir = "detected_faces"
approved_faces_dir = "approved_faces"
os.makedirs(detected_faces_dir, exist_ok=True)
os.makedirs(approved_faces_dir, exist_ok=True)

def compare_faces(new_face, approved_faces_dir):
    for file in os.listdir(approved_faces_dir):
        approved_face = cv2.imread(os.path.join(approved_faces_dir, file), cv2.IMREAD_GRAYSCALE)
        if approved_face is None:
            continue
        
        # Resize both faces for comparison
        approved_face = cv2.resize(approved_face, (new_face.shape[1], new_face.shape[0]))
        
        # Compare histograms (you can improve this by using better face recognition)
        hist_new_face = cv2.calcHist([new_face], [0], None, [256], [0, 256])
        hist_approved_face = cv2.calcHist([approved_face], [0], None, [256], [0, 256])
        
        # Compare histograms (returns a similarity score)
        similarity = cv2.compareHist(hist_new_face, hist_approved_face, cv2.HISTCMP_CORREL)
        
        # If similarity score is high, consider it a match
        if similarity > 0.9:
            return True
    return False

while True:
    im = picam2.capture_array()

    grey = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    faces = face_detector.detectMultiScale(grey, 1.1, 5)

    for (x, y, w, h) in faces:
        cv2.rectangle(im, (x, y), (x + w, y + h), (0, 255, 0))

        face_roi = grey[y:y+h, x:x+w]  # Region of interest (detected face)

        # Check if the detected face is already in the approved faces directory
        if compare_faces(face_roi, approved_faces_dir):
            print("Approved face detected.")
        else:
            # Save the face image in the detected faces directory with a timestamp
            timestamp = int(time.time())
            filename = os.path.join(detected_faces_dir, f"face_{timestamp}.jpg")
            cv2.imwrite(filename, face_roi)  # Save only the detected face portion
            print("New face detected. Approve or deny.")

            # Show the detected face and ask for approval (Y/N)
            cv2.imshow("New Face", face_roi)
            key = cv2.waitKey(0)  # Wait for user input
            
            if key == ord('y') or key == ord('Y'):
                print("Face approved.")
                # Move the face image to the approved faces directory
                approved_filename = os.path.join(approved_faces_dir, f"approved_{timestamp}.jpg")
                shutil.move(filename, approved_filename)
            else:
                print("Face denied.")
                # If denied, delete the saved image
                os.remove(filename)
            
            cv2.destroyWindow("New Face")  # Close the face preview window

    cv2.imshow("Camera", im)
    if cv2.waitKey(1) == 27:  # Press 'Esc' to exit
        break

cv2.destroyAllWindows()

import cv2
import os
import time
import numpy as np
import shutil
import tkinter as tk
from tkinter import Label, Button
from PIL import Image, ImageTk
from picamera2 import Picamera2  # Pillow for image handling

# Initalize Picamera2
picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration(main={"format": "XRGB8888", "size": (640, 480)}))
picam2.start()

# Load the DNN model
net = cv2.dnn.readNetFromCaffe("dnn_model/deploy.prototxt", "dnn_model/res10_300x300_ssd_iter_140000.caffemodel")

# Directories for detected and approved faces
detected_faces_dir = "detected_faces"
approved_faces_dir = "approved_faces"
os.makedirs(detected_faces_dir, exist_ok=True)
os.makedirs(approved_faces_dir, exist_ok=True)

# Global variable to store approval status
approval_status = None

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

def approve_face():
    global approval_status
    approval_status = "approve"
    root.destroy()

def deny_face():
    global approval_status
    approval_status = "deny"
    root.destroy()

def show_face_in_gui(face_roi):
    global root
    
    # Create a Tkinter window
    root = tk.Tk()
    root.title("Face Approval")

    # Set up the window size and position
    root.geometry("400x300")
    root.eval('tk::PlaceWindow . center')  # Center the window

    # Convert OpenCV image to PIL format
    face_image_pil = Image.fromarray(face_roi)

    # Resize the image for GUI
    face_image_pil = face_image_pil.resize((200, 200))

    # Convert to a Tkinter-compatible image
    face_image_tk = ImageTk.PhotoImage(face_image_pil)

    # Create a label to show the face image
    face_label = Label(root, image=face_image_tk)
    face_label.image = face_image_tk  # Keep a reference to the image to avoid garbage collection
    face_label.pack()

    # Create buttons
    approve_button = Button(root, text="Approve", command=approve_face, bg="green", fg="white", width=10)
    deny_button = Button(root, text="Deny", command=deny_face, bg="red", fg="white", width=10)

    # Add buttons to the window
    approve_button.pack(side="left", padx=20, pady=20)
    deny_button.pack(side="right", padx=20, pady=20)

    # Wait for user input (approve or deny)
    root.mainloop()

while True:
    # Capture image from the camera
    im = picam2.capture_array()

    # Remove the alpha channel by selecting only the RGB channels (assuming im is in XRGB8888 format)
    im_rgb = im[:, :, :3]  # Keep only the first three channels (X, R, G)

    (h, w) = im_rgb.shape[:2]

    # Convert image to a blob for the DNN model
    blob = cv2.dnn.blobFromImage(cv2.resize(im_rgb, (300, 300)), 1.0, (300, 300), (104.0, 177.0, 123.0))
    net.setInput(blob)
    detections = net.forward()

    # Process detections
    for i in range(0, detections.shape[2]):
        confidence = detections[0, 0, i, 2]

        if confidence > 0.7:  # Confidence threshold (adjustable)
            box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
            (startX, startY, endX, endY) = box.astype("int")

            # Draw a rectangle around the detected face
            cv2.rectangle(im_rgb, (startX, startY), (endX, endY), (0, 255, 0), 2)

            # Extract the detected face region of interest (ROI)
            face_roi = im_rgb[startY:endY, startX:endX]
            grey_face_roi = cv2.cvtColor(face_roi, cv2.COLOR_BGR2GRAY)

            # Check if the detected face is already in the approved faces directory
            if compare_faces(grey_face_roi, approved_faces_dir):
                print("Approved face detected.")
            else:
                # Save the face image in the detected faces directory with a timestamp
                timestamp = int(time.time())
                filename = os.path.join(detected_faces_dir, f"face_{timestamp}.jpg")
                cv2.imwrite(filename, grey_face_roi)  # Save only the detected face portion
                print("New face detected. Approve or deny.")

                # Display the face in the GUI window for approval
                show_face_in_gui(grey_face_roi)

                # Process the approval status
                if approval_status == "approve":
                    print("Face approved.")
                    # Move the face image to the approved faces directory
                    approved_filename = os.path.join(approved_faces_dir, f"approved_{timestamp}.jpg")
                    shutil.move(filename, approved_filename)
                elif approval_status == "deny":
                    print("Face denied.")
                    # If denied, delete the saved image
                    os.remove(filename)

    # Show the camera feed with rectangles drawn around detected faces
    cv2.imshow("Camera", im_rgb)
    
    if cv2.waitKey(1) == 27:  # Press 'Esc' to exit
        break

cv2.destroyAllWindows()


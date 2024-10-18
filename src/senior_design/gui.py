# gui.py
import tkinter as tk
from tkinter import Label, Button
from PIL import Image, ImageTk

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

import tkinter as tk
from tkinter import Label, Button
from PIL import Image, ImageTk

def approve_face(root, status_var):
    status_var.set("approve")
    root.destroy()

def deny_face(root, status_var):
    status_var.set("deny")
    root.destroy()

def show_face_in_gui(face_roi):
    """Displays the face and prompts for approval."""
    root = tk.Tk()
    root.title("Face Approval")
    root.geometry("400x300")
    root.eval('tk::PlaceWindow . center')

    status_var = tk.StringVar()

    # Convert OpenCV image to PIL format
    face_image_pil = Image.fromarray(face_roi).resize((200, 200))
    face_image_tk = ImageTk.PhotoImage(face_image_pil)

    # Create a label to show the face image
    face_label = Label(root, image=face_image_tk)
    face_label.image = face_image_tk
    face_label.pack()

    # Buttons for approval or denial
    approve_button = Button(root, text="Approve", command=lambda: approve_face(root, status_var), bg="green", fg="white", width=10)
    deny_button = Button(root, text="Deny", command=lambda: deny_face(root, status_var), bg="red", fg="white", width=10)

    approve_button.pack(side="left", padx=20, pady=20)
    deny_button.pack(side="right", padx=20, pady=20)

    # Wait for user input
    root.mainloop()

    return status_var.get()

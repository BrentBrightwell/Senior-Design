import tkinter as tk
from tkinter import Label, Button, Entry
from PIL import Image, ImageTk
import cv2

def approve_face(root, status_var):
    """Set approval status and destroy the GUI."""
    status_var.set("approve")
    root.destroy()

def deny_face(root, status_var):
    status_var.set("deny")
    root.destroy()

def show_face_in_gui(face_roi):
    root = tk.Tk()
    root.title("Face Approval")
    root.geometry("500x400")  # Increase the window size for better fit
    root.eval('tk::PlaceWindow . center')

    status_var = tk.StringVar()
    first_name_var = tk.StringVar()
    last_name_var = tk.StringVar()

    # Error label for feedback
    error_label = Label(root, text="", fg="red")
    error_label.grid(row=4, columnspan=2, pady=5)

    # Convert the face ROI to a PIL Image and then to a PhotoImage
    face_image_pil = Image.fromarray(face_roi).resize((200, 200))
    face_image_tk = ImageTk.PhotoImage(face_image_pil)

    # Center the face image at the top
    face_label = Label(root, image=face_image_tk)
    face_label.image = face_image_tk
    face_label.grid(row=0, column=0, columnspan=2, padx=5, pady=10)

    # Labels and Entry fields for First and Last Name
    Label(root, text="First Name:", anchor="e").grid(row=1, column=0, padx=5, pady=5, sticky="e")
    first_name_entry = Entry(root, textvariable=first_name_var)
    first_name_entry.grid(row=1, column=1, padx=5, pady=5)

    Label(root, text="Last Name:", anchor="e").grid(row=2, column=0, padx=5, pady=5, sticky="e")
    last_name_entry = Entry(root, textvariable=last_name_var)
    last_name_entry.grid(row=2, column=1, padx=5, pady=5)

    def approve_face_action():
        if validate_and_approve(first_name_var, last_name_var, status_var, error_label):
            root.destroy()

    # Approve and Deny buttons with increased padding for better spacing
    approve_button = Button(root, text="Approve", command=approve_face_action, bg="green", fg="white", width=10)
    deny_button = Button(root, text="Deny", command=lambda: deny_face(root, status_var), bg="red", fg="white", width=10)

    approve_button.grid(row=3, column=0, padx=20, pady=20)
    deny_button.grid(row=3, column=1, padx=20, pady=20)

    # Start the GUI main loop
    root.mainloop()

    return status_var.get(), first_name_var.get(), last_name_var.get()

def draw_mode_banner(im_rgb, mode):
    """Draws a banner at the top of the camera feed showing the current mode."""
    (h, w) = im_rgb.shape[:2]
    banner_height = 40  # Height of the banner

    # Draw banner (gray background)
    cv2.rectangle(im_rgb, (0, 0), (w, banner_height), (50, 50, 50), -1)

    # Define font, size, and text positioning
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 1.0
    font_color = (255, 255, 255)  # White text
    thickness = 2
    text = f"MODE: {mode.value.upper()}"
    text_size = cv2.getTextSize(text, font, font_scale, thickness)[0]
    text_x = (w - text_size[0]) // 2
    text_y = (banner_height + text_size[1]) // 2

    # Put the mode text in the center of the banner
    cv2.putText(im_rgb, text, (text_x, text_y), font, font_scale, font_color, thickness)
    
    return im_rgb

def validate_and_approve(first_name_var, last_name_var, status_var, error_label):
    """Validates the input and sets the approval status if valid."""
    first_name = first_name_var.get().strip()
    last_name = last_name_var.get().strip()

    # Clear previous error message
    error_label.config(text="")

    # Check if either field is empty
    if not first_name or not last_name:
        error_label.config(text="First and Last name MUST be filled out!")
        return False  # Validation failed

    # Check for spaces within the names (not just leading/trailing)
    if " " in first_name or " " in last_name:
        error_label.config(text="First and Last name cannot include spaces!")
        return False  # Validation failed

    # If validation passes, set approval status
    status_var.set("approve")
    return True  # Validation succeeded
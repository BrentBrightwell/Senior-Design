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
    root.geometry("400x300")
    root.eval('tk::PlaceWindow . center')

    status_var = tk.StringVar()
    first_name_var = tk.StringVar()
    last_name_var = tk.StringVar()

    # Error label for feedback
    error_label = Label(root, text="", fg="red")
    error_label.grid(row=4, columnspan=2, padx=5, pady=5)

    face_image_pil = Image.fromarray(face_roi).resize((200, 200))
    face_image_tk = ImageTk.PhotoImage(face_image_pil)

    face_label = Label(root, image=face_image_tk)
    face_label.image = face_image_tk
    face_label.pack()

    # Labels and Entry for First and Last Name
    Label(root, text="First Name:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
    first_name_entry = Entry(root, textvariable=first_name_var)
    first_name_entry.grid(row=1, column=1, padx=5, pady=5)

    Label(root, text="Last Name:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
    last_name_entry = Entry(root, textvariable=last_name_var)
    last_name_entry.grid(row=2, column=1, padx=5, pady=5)

    def validate_and_approve():
        first_name = first_name_var.get().strip()
        last_name = last_name_var.get().strip()

        # Clear previous error message
        error_label.config(text="")

        if not first_name or not last_name:
            error_label.config(text="First and Last name MUST be filled out!")
            return  # Do not proceed if there's an error

        if " " in first_name or " " in last_name:
            error_label.config(text="First and Last name cannot include spaces!")
            return  # Do not proceed if there's an error

        # If validation passes, set approval status and close GUI
        status_var.set("approve")
        root.destroy()

    approve_button = Button(root, text="Approve", command=validate_and_approve, bg="green", fg="white", width=10)
    deny_button = Button(root, text="Deny", command=lambda: deny_face(root, status_var), bg="red", fg="white", width=10)

    approve_button.grid(row=3, column=0, padx=20, pady=20)
    deny_button.grid(row=3, column=1, padx=20, pady=20)

    root.mainloop()

    return status_var.get(), first_name_var.get(), last_name_var.get()  # Return status, first name, and last name

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

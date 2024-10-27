import tkinter as tk
from tkinter import Label, Button
from PIL import Image, ImageTk
import cv2

def approve_face(root, status_var):
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

    face_image_pil = Image.fromarray(face_roi).resize((200, 200))
    face_image_tk = ImageTk.PhotoImage(face_image_pil)

    face_label = Label(root, image=face_image_tk)
    face_label.image = face_image_tk
    face_label.pack()

    approve_button = Button(root, text="Approve", command=lambda: approve_face(root, status_var), bg="green", fg="white", width=10)
    deny_button = Button(root, text="Deny", command=lambda: deny_face(root, status_var), bg="red", fg="white", width=10)

    approve_button.pack(side="left", padx=20, pady=20)
    deny_button.pack(side="right", padx=20, pady=20)

    root.mainloop()
    return status_var.get()

def draw_mode_banner(im_rgb, mode):
    (h, w) = im_rgb.shape[:2]
    banner_height = 40
    cv2.rectangle(im_rgb, (0, 0), (w, banner_height), (50, 50, 50), -1)

    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 1.0
    font_color = (255, 255, 255)
    thickness = 2
    text = f"MODE: {mode.value.upper()}"
    text_size = cv2.getTextSize(text, font, font_scale, thickness)[0]
    text_x = (w - text_size[0]) // 2
    text_y = (banner_height + text_size[1]) // 2

    cv2.putText(im_rgb, text, (text_x, text_y), font, font_scale, font_color, thickness)
    
    return im_rgb

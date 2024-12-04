import time
import threading
import tkinter as tk
from tkinter import Label, Button, Entry
from PIL import Image, ImageTk
import cv2
from gpio_devices import read_temperature_humidity, trigger_siren, stop_siren
from utilities import play_alert_sound, stop_alert_sound_event, start_video_recording, stop_video_recording

SENSOR_UPDATE_INTERVAL = 5 #in seconds
last_sensor_update_time = 0
last_temp, last_humid = None, None  # Variables to hold last fetched values

intruder_alert_active = False

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
    root.geometry("350x420")
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

def draw_banners(im_rgb, mode):
    global last_sensor_update_time, last_temp, last_humid
    current_time = time.time()

    # Draw the mode banner
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

    # Check if the interval has passed before updating sensor data
    if current_time - last_sensor_update_time > SENSOR_UPDATE_INTERVAL:
        last_temp, last_humid = read_temperature_humidity()
        last_sensor_update_time = current_time  # Reset the last update time

    # Draw the temperature/humidity box at the bottom right
    box_width, box_height = 180, 50
    box_x = w - box_width - 10
    box_y = h - box_height - 10
    cv2.rectangle(im_rgb, (box_x, box_y), (box_x + box_width, box_y + box_height), (255, 255, 255), -1)

    # Display the last fetched temperature and humidity in the box
    if last_temp is not None and last_humid is not None:
        text_temp = f"Temperature: {last_temp} F"
        text_humid = f"Humidity: {last_humid} %"
        cv2.putText(im_rgb, text_temp, (box_x + 10, box_y + 20), font, 0.5, (0, 0, 0), 1)
        cv2.putText(im_rgb, text_humid, (box_x + 10, box_y + 40), font, 0.5, (0, 0, 0), 1)

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

def acknowledge_alert(alert_window, alert_acknowledged):
    global intruder_alert_active
    alert_acknowledged.set()
    intruder_alert_active = False
    stop_alert_sound_event.set()
    stop_siren()
    stop_video_recording()
    alert_window.destroy()

def trigger_siren_if_not_acknowledged(alert_acknowledged):
    for _ in range(10):
        if alert_acknowledged.is_set():
            return
        time.sleep(1)

    if not alert_acknowledged.is_set():
        trigger_siren()

def show_intruder_alert(alert_acknowledged):
    global intruder_alert_active  # Ensure we modify the global variable

    if intruder_alert_active:
        return  # Avoid triggering another alert if one is already active

    intruder_alert_active = True  # Mark alert as active
    alert_acknowledged.clear()

    # Create the GUI for the alert
    alert_window = tk.Toplevel()
    alert_window.title = "INTRUDER ALERT"
    alert_window.geometry("400x200")

    tk.Label(alert_window, text="INTRUDER ALERT!", font=("Arial", 20), fg="red").pack(pady=20)
    acknowledge_button = tk.Button(alert_window, text="Acknowledge", command=lambda: acknowledge_alert(alert_window))
    acknowledge_button.pack(pady=20)

    start_video_recording()

    threading.Thread(target=play_alert_sound, daemon=True).start()
    threading.Thread(target=trigger_siren_if_not_acknowledged, args=(alert_window,), daemon=True).start()
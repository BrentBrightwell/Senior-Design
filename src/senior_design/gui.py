import time
import threading
import tkinter as tk
from tkinter import Label, Button, Entry
from PIL import Image, ImageTk
import cv2
import pygame
from gpio_devices import read_temperature_humidity, trigger_siren, stop_siren
from utilities import start_video_recording, stop_video_recording

SENSOR_UPDATE_INTERVAL = 5
last_sensor_update_time = 0
last_temp, last_humid = None, None

alert_acknowledged = threading.Event()
intruder_alert_active = False
alert_sound_thread = None

ALERT_SOUND_PATH = "resources/intruder_alert.wav"

root = tk.Tk()

def approve_face(root, status_var):
    """Set approval status and destroy the GUI."""
    status_var.set("approve")
    root.destroy()

def deny_face(root, status_var):
    status_var.set("deny")
    root.destroy()

def show_face_in_gui(face_roi):
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

    root.mainloop()

    return status_var.get(), first_name_var.get(), last_name_var.get()

def draw_banners(im_rgb, mode):
    global last_sensor_update_time, last_temp, last_humid
    current_time = time.time()
    if current_time - last_sensor_update_time >= SENSOR_UPDATE_INTERVAL:
        last_sensor_update_time = current_time
        temp, humidity = read_temperature_humidity()
        last_temp, last_humid = temp, humidity

    temp_str = f"temp (F): {last_temp}" if last_temp else "temp (F): --"
    humidity_str = f"humidity: {last_humid}" if last_humid else "humidity: --"

    cv2.putText(im_rgb, temp_str, (10, im_rgb.shape[0] - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    cv2.putText(im_rgb, humidity_str, (10, im_rgb.shape[0] - 40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

    return im_rgb

def play_alert_sound():
    pygame.mixer.init()
    pygame.mixer.music.load(ALERT_SOUND_PATH)
    pygame.mixer.music.play(loops=-1)

def show_intruder_alert():
    global intruder_alert_active
    if intruder_alert_active:
        return

    intruder_alert_active = True

    root = tk.Tk()
    root.title("INTRUDER ALERT")
    root.geometry("300x150")
    root.eval('tk::PlaceWindow . center')

    label = tk.Label(root, text="INTRUDER ALERT", fg="red", font=("Helvetica", 16))
    label.pack(pady=20)

    acknowledge_button = Button(root, text="Acknowledge", command=acknowledge_alert, bg="green", fg="white")
    acknowledge_button.pack(pady=20)

    play_alert_sound()
    root.mainloop()

def acknowledge_alert():
    alert_acknowledged.set()
    stop_siren()

# Start the GUI for the main feed and handle updates
def start_gui():
    global last_temp, last_humid

    # Initialize Tkinter window (if not already initialized in other parts of your code)
    root = tk.Tk()
    root.title("Security Feed")

    # Set the window dimensions and center it
    root.geometry("640x480")  # or any dimensions you want for the GUI window
    root.eval('tk::PlaceWindow . center')

    # Create label widgets for temperature and humidity (these will update periodically)
    temp_label = Label(root, text=f"temp (F): {last_temp}" if last_temp else "temp (F): --", font=("Helvetica", 12))
    temp_label.grid(row=0, column=0, padx=10, pady=5)

    humidity_label = Label(root, text=f"humidity: {last_humid}" if last_humid else "humidity: --", font=("Helvetica", 12))
    humidity_label.grid(row=0, column=1, padx=10, pady=5)

    # Update the temperature and humidity labels periodically
    def update_sensor_data():
        # Update temperature and humidity values
        temp, humidity = read_temperature_humidity()
        temp_label.config(text=f"temp (F): {temp}")
        humidity_label.config(text=f"humidity: {humidity}")

        # Schedule the next update after SENSOR_UPDATE_INTERVAL seconds
        root.after(SENSOR_UPDATE_INTERVAL * 1000, update_sensor_data)  # Convert to milliseconds

    # Start the sensor data updates
    update_sensor_data()

    # Start the Tkinter event loop
    root.mainloop()


if __name__ == "__main__":
    start_gui()

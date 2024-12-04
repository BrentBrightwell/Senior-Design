# Raspberry Pi Facial Detection Security System

This repository contains a Python-based facial detection security system built on a Raspberry Pi using a Picamera, OpenCV, and additional sensors for environmental monitoring. The system features two modes—`Training` and `Active`—for real-time facial recognition and approval of new faces through a graphical user interface (GUI). It also provides live temperature and humidity readings within the camera feed and integrates an intruder alert system with audio.

## Table of Contents
- [Overview](#overview)
- [System Requirements](#system-requirements)
- [Project Structure](#project-structure)
- [Usage](#usage)
- [Customization](#customization)
- [License](#license)

## Overview

The project enables users to create a facial detection system for security purposes using a Raspberry Pi, Picamera, and ASAIR AM2301B temperature and humidity sensor. The system operates in two modes:

1. **Training Mode**: New faces detected by the camera can be approved or denied manually using a GUI prompt.
2. **Active Mode**: The system verifies detected faces against pre-approved entries and triggers an intruder alert if an unapproved face is detected.

The system provides a live camera feed with bounding boxes drawn around detected faces, a mode banner at the top, and live temperature and humidity readings at the bottom right of the feed. Additionally, if an intruder is detected for more than one second, the system will trigger an alert with an acknowledgment button and play a siren sound until acknowledged.

## System Requirements
- Raspberry Pi (with Picamera module and AM2301B sensor)
- Python 3.x
- OpenCV
- Picamera2
- Tkinter
- NumPy
- Pillow (PIL)
- Blinka for RaspberryPi (Instructions: https://learn.adafruit.com/circuitpython-on-raspberrypi-linux/installing-circuitpython-on-raspberry-pi)
- Adafruit CircuitPython libraries for sensor integration
- gpiozero (for GPIO control)
- `sounddevice` (for audio alerts)

## Project Structure

The project is organized into four main Python files for readability and maintainability.

### 1. `main.py`
This is the main script that initializes the camera, handles face detection logic, manages mode switching, and handles user-adjustable variables like detection confidence thresholds. 

Key functionalities:
- Starts the Picamera and processes the live video stream.
- Detects faces using a pre-trained DNN model.
- In `Active` mode, checks if a detected face is pre-approved.
- In `Training` mode, prompts the user to approve or deny new faces.
- Launches a separate thread for approval prompts, allowing the live feed to continue uninterrupted.

### 2. `utilities.py`
Contains backend utilities and helper functions used in the program, including face comparison logic, mode management, and approval handling.

Key functionalities:
- `compare_faces()`: Compares newly detected faces with approved faces using histogram comparison.
- `handle_approval()`: Manages the approval process for detected faces.
- `Mode`: Enum defining `TRAINING` and `ACTIVE` modes.

### 3. `gui.py`
Handles all GUI-related functionality, including prompting the user to approve or deny a face in `Training` mode, displaying a banner showing the current mode, and displaying live temperature and humidity readings on the feed.

Key functionalities:
- `show_face_in_gui()`: Displays a GUI for user approval or denial of new faces.
- `draw_mode_banner()`: Adds the current mode banner at the top of the feed and overlays temperature and humidity readings at the bottom right.
- `approve_face()` and `deny_face()`: Handle user approval or denial actions within the GUI.
- `show_intruder_alert()`: Displays an intruder alert GUI with acknowledgment button and controls the alert sound.

### 4. `gpio_devices.py`
Integrates the AM2301B sensor for environmental monitoring and controls the motion sensor, LED indicator, and siren.

Key functionalities:
- `read_temperature_humidity()`: Fetches and formats temperature and humidity data for display on the feed.
- `initialize_motion_sensor()`: Monitors the motion sensor for movement and triggers an LED indicator.
- `activate_siren()` and `deactivate_siren()`: Controls the siren based on motion detection or intruder alerts.

## Usage

### Installation

It is IMPERATIVE that the packages are installed within a Python virtual environment (.venv)

Ensure the required Python packages are installed.

```bash
pip install opencv-python numpy picamera2 pillow gpiozero sounddevice
```

Install Blinka for RaspberryPi: https://learn.adafruit.com/circuitpython-on-raspberrypi-linux/installing-circuitpython-on-raspberry-pi

Then confirm that Blinka was successfully installed on the device.

```bash
python3 dependancy_testing/blinka_test.py
```

Afterwards, confirm the temperature and humidity sensor is properly hooked up to the device.

```bash
python3 dependancy_testing/AHTx0_test.py
```

### Running the Program

Run the `main.py` script to start the system.
```bash
python3 src/senior_design/main.py
```

### Switching Modes

- **Training Mode**: Allows you to approve or deny new faces. The system prompts you with a GUI window when a new face is detected.
- **Active Mode**: The system checks for pre-approved faces and triggers an intruder alert if an unapproved face is detected.

Press the `t` key to toggle between modes. The current mode is displayed at the top of the live camera feed.

### Temperature and Humidity Display

Temperature and humidity readings from the AM2301B sensor are displayed at the bottom right of the live camera feed. The update interval for these readings can be customized in `gui.py` (adjust `SENSOR_UPDATE_INTERVAL` for optimal performance).

### Intruder Alert Sequence

If the system detects an unapproved face for more than one second in `Active Mode`, it will trigger an intruder alert. The alert will be displayed in a GUI with an acknowledgment button, and an alert sound will play in a 2-second loop until the alert is acknowledged. If the alert is not acknowledged without 10 seconds, a high-decible siren will sound.

A recording of the intrusion until the alert is acknowledged will be saved for further examination.

### Exit

Press `ESC` to exit the program.

## Customization

You can easily customize the system to fit your needs by adjusting variables in `main.py`:

- `CONFIDENCE_THRESHOLD`: Sets the confidence level for face detection.
- `DETECTED_FACES_DIR`: Directory where new face images are stored.
- `APPROVED_FACES_DIR`: Directory where approved face images are stored.
- `SENSOR_UPDATE_INTERVAL`: Controls the frequency of temperature and humidity sensor updates (adjust in `gui.py`).

## License

This project is licensed under the MIT License.

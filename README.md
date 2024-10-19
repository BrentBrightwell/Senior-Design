# Raspberry Pi Facial Detection Security System

This repository contains a Python-based facial detection security system built on a Raspberry Pi using a Picamera and OpenCV. The system offers two modes: `Training` and `Active`, allowing real-time facial recognition and approval of new faces through a graphical user interface (GUI).

## Table of Contents
- [Overview](#overview)
- [System Requirements](#system-requirements)
- [Project Structure](#project-structure)
- [Usage](#usage)
- [Customization](#customization)
- [License](#license)

## Overview

The project enables users to create a facial detection system for security purposes using a Raspberry Pi and Picamera. The system runs in two modes:

1. **Training Mode**: Faces detected by the camera can be approved or denied manually using a GUI prompt.
2. **Active Mode**: The system checks whether detected faces are pre-approved. If an unapproved face is detected, an intruder alert is triggered.

The system provides a live camera feed with bounding boxes drawn around detected faces. The current mode is also displayed at the top of the screen.

## System Requirements
- Raspberry Pi (with Picamera module)
- Python 3.x
- OpenCV
- Picamera2
- Tkinter
- NumPy
- Pillow (PIL)

## Project Structure

The project is split into three main Python files to ensure readability and maintainability.

### 1. `main.py`
This is the main script that initializes the camera, handles the face detection logic, and switches between training and active modes. It also manages the user-adjustable variables like detection confidence thresholds.

Key functionalities:
- Starts the Picamera and processes the live video stream.
- Detects faces using a pre-trained DNN model.
- In `Active` mode, checks if a detected face is approved.
- In `Training` mode, prompts the user to approve or deny new faces.

### 2. `utilities.py`
This file contains the backend utilities and helper functions used in the program, including face comparison logic and mode enumeration.

Key functionalities:
- `compare_faces()`: Compares newly detected faces with approved faces using histogram comparison.
- `Mode`: Enum to define `TRAINING` and `ACTIVE` modes.

### 3. `gui.py`
This file handles all GUI-related functionality, including prompting the user to approve or deny a face in `Training` mode and displaying a banner showing the current mode.

Key functionalities:
- `show_face_in_gui()`: Displays a GUI for user approval or denial of new faces.
- `approve_face()` and `deny_face()`: Handle user input through the GUI.
- Mode display banner in the live camera feed.

## Usage

### 1. Installation

Ensure the required Python packages are installed.

```bash
pip install opencv-python numpy picamera2 pillow
```

### 2. Running the Program

Run the `main.py` script to start the system.

```bash
python3 main.py
```

### 3. Switching Modes

- **Training Mode**: Allows you to approve or deny new faces. The system prompts you with a GUI window when a new face is detected.
- **Active Mode**: The system checks for pre-approved faces and triggers an intruder alert if an unapproved face is detected.

You can toggle between modes by pressing the `t` key while the program is running. The current mode is displayed at the top of the live camera feed.

### 4. Exit

Press `ESC` to exit the program.

## Customization

You can easily customize the system to fit your needs by adjusting variables in `main.py`:

- `CONFIDENCE_THRESHOLD`: Adjust the face detection confidence level.
- `DETECTED_FACES_DIR`: Directory where new face images are stored.
- `APPROVED_FACES_DIR`: Directory where approved face images are stored.

## License

This project is licensed under the MIT License.

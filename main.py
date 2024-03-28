import time
import os
import logging
import random
import pyautogui
import requests
from dotenv import load_dotenv
import subprocess

NAME_LIST = [
    'iPhone',
    'iPad',
    'Macbook',
    'Desktop',
    'Huawei',
    'Mobile',
    'PC',
    'Windows',
    'Home',
    'MyPC',
    'Computer',
    'Android'
]
DISPLAY_NAME = random.choice(NAME_LIST)

BASE_PATH = './'
IMG_PATH = os.path.join(BASE_PATH, "img")
VIDEO_OUTPUT = os.path.join(BASE_PATH, "output.mp4")
AUDIO_OUTPUT = os.path.join(BASE_PATH, "output.wav")

# Load environment variables from .env file
load_dotenv()

MEETING_DURATION = os.getenv('MEETING_DURATION')  # Convert to integer
MEETING_ID = os.getenv('MEETING_ID')
MEETING_PASSWORD = os.getenv('MEETING_PASSWORD')


def upload_files(file_paths):
    for file_path in file_paths:
        try:
            url = upload_to_gofile(file_path)
            logging.info(f"File uploaded successfully: {url}")
        except Exception as e:
            logging.error(f"Error uploading file: {e}")


def upload_to_gofile(file_path):
    url = 'https://api.gofile.io/servers'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        first_server_name = data['data']['servers'][0]['name']
        url = f'https://{first_server_name}.gofile.io/contents/uploadfile'
        files = {'file': open(file_path, 'rb')}
        response = requests.post(url, files=files)
        data = response.json()
        return data['data']['downloadPage']
    else:
        raise Exception(f"Error: {response.status_code}")


def sign_in(meet_id, password):
    logging.info("Joining meeting...")
    try:
        result = pyautogui.locateCenterOnScreen(os.path.join(
            IMG_PATH, 'join_meeting.png'), minSearchTime=2, confidence=0.9)
        if result is not None:
            x, y = result
            pyautogui.click(x, y)
        else:
            raise Exception("Could not find 'Join Meeting' on screen!")

        time.sleep(2)

        # Insert meeting id
        pyautogui.press('tab')
        pyautogui.press('tab')
        pyautogui.write(meet_id, interval=0.1)

        # Insert name
        pyautogui.press('tab')
        pyautogui.press('tab')
        pyautogui.hotkey('ctrl', 'a')
        pyautogui.write(DISPLAY_NAME, interval=0.1)

        # Configure
        pyautogui.press('tab')
        pyautogui.press('space')
        pyautogui.press('tab')
        pyautogui.press('tab')
        pyautogui.press('space')
        pyautogui.press('tab')
        pyautogui.press('tab')
        pyautogui.press('space')
        time.sleep(10)

        pyautogui.write(password, interval=0.1)
        pyautogui.press('enter')
        time.sleep(5)

        result = pyautogui.locateCenterOnScreen(os.path.join(
            IMG_PATH, 'join_with_computer_audio.png'), minSearchTime=2, confidence=0.9)
        if result is not None:
            x, y = result
            pyautogui.click(x, y)
    except Exception as e:
        logging.error(f"Error signing in: {e}")


# Start screen and audio recording
def start_recording(duration):
    try:
        logging.info("Starting screen and audio recording...")
        subprocess.Popen(["ffmpeg", "-f", "avfoundation", "-i", ":0", "-f", "avfoundation", "-i", ":1", "-t", str(duration), "-c:v", "libx264",
                         "-preset", "ultrafast", "-crf", "0", "-c:a", "aac", "-strict", "experimental", VIDEO_OUTPUT, "-y", AUDIO_OUTPUT], stderr=subprocess.PIPE)
    except Exception as e:
        logging.error(f"Error starting recording: {e}")


time.sleep(10)
sign_in(MEETING_ID, MEETING_PASSWORD)
logging.info("Signed in.")

start_recording(MEETING_DURATION)
logging.info("Recording started.")

# Wait for meeting duration
time.sleep(float(MEETING_DURATION) if MEETING_DURATION is not None else 60)

# Stop recording
logging.info("Recording stopped.")

# Upload recorded files
upload_files([VIDEO_OUTPUT, AUDIO_OUTPUT])
logging.info("Files uploaded.")

# Clean up temporary files
os.remove(VIDEO_OUTPUT)
os.remove(AUDIO_OUTPUT)

logging.info("Temporary files cleaned up.")

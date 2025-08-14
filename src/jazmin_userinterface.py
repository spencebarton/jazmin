# Jazmin  - Your Digital Personality
# File    : jazmin_userinterface.py
# Author  : Spencer Barton (spencer@jazminpy.com)
# GitHub  : https://github.com/spencebarton/jazmin
# License : MIT License
# Descript: Handles minor user interface functions before the main program initializes
# Last date edited: (08/10/25 13:42)

# Copyright (c) 2025 Spencer Barton 
# Managed through Jazmin and SBD. All rights reserved. 
# For more information, visit jazminpy.com

# Libraries used
import time
import tkinter as tk
import webbrowser
global user_enter_name
import random
from tkinter import PhotoImage
import threading, jazmin_application as ja

# Function: Jazmin_Timer_Start
    # starts JazminTimer used for identifying when application launches (after loading assets)
def Jazmin_Timer_Start():
    global start_time; start_time = time.time(); print("[Jazmin] [Boot Timer]   - Timer started")

# Function: Jazmin_Timer_Elapsed()
    # prints and calculates time between start of loading and end of loading assets
def Jazmin_Timer_Elapsed():
    if start_time is None: print("[Jazmin] [Boot Timer]   - Timer has not been started yet")       
    else: elapsed_time = time.time() - start_time; print(f"[Jazmin] [Boot Timer]   - Elapsed time - {elapsed_time:.2f} seconds"); print("Jazmin is opening...")

# Function: Jazmin_Timer_Stop()
    # will destroy JazminTimer
def Jazmin_Timer_Stop():
    global start_time
    if start_time is None: print("[Jazmin] [Boot Timer]   - Timer is not running")        
    else: start_time = None; print("[Jazmin] [Boot Timer]   - Timer stopped and removed")
 
# Function: center_window()
    # centers the application to the users screen
def center_window(window, width, height):
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    x = (screen_width // 2) - (width // 2)
    y = ((screen_height - 145) // 2) - (height // 2)

    window.geometry(f'{width}x{height}+{x}+{y}')

# Function: validate_characters()
    # validates the input at jazmins menu screen
def validate_characters(self, new_text):
        if len(new_text) <= self.max_characters:
            return True
        else:
            return False

# used for open_jazminhelp() function
HELP_LINES = [
    "haha you need help",
    "ha-need a hand?",
    "Mmm, help time?",
    "Heh, you rang?",
    "Okay okay, I got you.",
    "Need backup, huh?",
    "Alright, coach mode on.",
    "Help coming right up.",
    "Say less, I'm here.",
    "Okay, what's stuck?",
    "Let's fix this.",
    "Deep breath-let's do it.",
    "I'll walk you through it.",
    "You pressed help, I show up.",
    "Guide mode: enabled.",
    "One step at a time.",
    "I've got a trick for that.",
    "Don't worry, I got this.",
    "Cool, let's get you some help.",
    "Yep-help is here."
]

# Function: open_jazminhelp()
    # help button function opens the site and says something
def open_jazminhelp(self):
    url = "https://www.jazminpy.com/help"
    webbrowser.open(url)
    print("[Jazmin] [Help] - Opened jazminpy.com/help")

    line = random.choice(HELP_LINES)
    print(f"[Jazmin] [Help] - Chosen voice line: {line}")

    threading.Thread(
        target=ja.api_audio_get,
        args=(line, self.audio_muted),
        daemon=True
    ).start()

# End, Spencer
# Jazmin  - Your Digital Personality
# File    : jazmin_application.py
# Author  : Spencer Barton (spencer@jazminpy.com)
# GitHub  : https://github.com/spencebarton/jazmin
# License : MIT License
# Descript: Most of Jazmin's background applications happen here
# Last date edited: (08/10/25 21:36)

# Copyright (c) 2025 Spencer Barton 
# Managed through Jazmin and SBD. All rights reserved. 
# For more information, visit jazminpy.com

# Libraries used
# Standard libraries
import os
import sys
import io
import time
import random
import tempfile
import subprocess
import ctypes
import socket
import getpass
import uuid
from datetime import datetime

# Threading libraries
import threading

# GUI libraries
import tkinter as tk
from tkinter import font as tkfont, filedialog
from tkinter import *
from PIL import ImageTk, Image
from tkVideoPlayer import TkinterVideo

# Audio libraries
import pygame
from pygame import mixer
from playsound import playsound

# Web and requests libraries
import requests
from bs4 import BeautifulSoup
from lxml import html

# Text and nlp libraries
from textblob import TextBlob

# Other apis and tools libraries
from openai import OpenAI
import keyboard
from colorama import Fore, Style
import winshell
from win32com.client import Dispatch

# Misplaced libraries
from ast import Lambda       
from turtle import width, window_width  

pygame.mixer.init()
audio_lock = threading.Lock()
chat_history = []
username2 = os.getlogin()
console_opened = False
output_buffer = io.StringIO()
last_user_activity = time.time()


login_reminder_handle = None
suppress_nag = False

usersname: str | None = None      
username: str | None = None      

# Function: set_user_name()
    # stores the user's entered name and formats a greeting
def set_user_name(name: str):
    global usersname, username
    usersname = name.strip()
    username = f"Hey {usersname}, how are you?"

    print("[Jazmin] - ran [set_user_name()]")

# Function: get_display_name()
    # returns the stored name or falls back to the system first name/login if none is set
def get_display_name() -> str:
    if usersname:

        return usersname

    first = get_windows_first_name() or os.getlogin()

    print("[Jazmin] - [ran get_display_name()]")
    return first

# Function: cancel_menu_messages()
    # stops any startup menu voice messages and prevents future ones from triggering then cancels any scheduled reminder timers
def cancel_menu_messages(tk_root=None):
    global suppress_nag, login_reminder_handle
    suppress_nag = True

    try:
        if pygame.mixer.get_init() and pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
            pygame.mixer.music.unload()

    except Exception as e:
        print("[Cancel Menu] - mixer stop/unload error:", e)

    try:
        if tk_root and isinstance(login_reminder_handle, (str, int)):
            tk_root.after_cancel(login_reminder_handle)
            login_reminder_handle = None

        elif login_reminder_handle is not None:
            try:
                login_reminder_handle.cancel()  # threading.Timer case
            except Exception:
                pass
            login_reminder_handle = None

    except Exception as e:
        print("[Jazmin] [Cancel Menu] - after_cancel/Timer cancel error:", e)

    print("[Jazmin] - [ran cancel_menu_messages()]")

# Function: resource_path()
    # resource_path functions for accessing files inside of jazmin_application.py
def resource_path(relative_path):
    if getattr(sys, 'frozen', False): 
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# simple boot message from Jazmin
# Function: internetConnect()
    # attempts to create a socket connection to Google's DNS to check if theres internet access
def internetConnect():
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return True
    except OSError:
        print("[Internet] - No internet, aborting timeout reaction")

        return False

# Function: get_wait_message()
    # Returns a personalized greeting using the system's username, noting whether it includes digits or not.
def get_wait_message():
    print("[Boot] [Jazmin] - User's [assumed] username: " + username2)

    if any(char.isdigit() for char in username2):
        print("[Boot] [Jazmin] - Numerical value detected in [assumed] user's username") 
        return "Hello, give me just one second."
    else:
        print("[Boot] [Jazmin] - - No numerical value detected in [assumed] user's username") 
        return f"Hello {username2}"

# Function: built_console()
    # opens a Windows console for viewing real-time output and logs
def built_console():
    global console_opened, output_buffer

    if console_opened:
        print("[Jazmin] [Console] - Console has already been opened. Ignoring request")
        return

    if sys.platform != "win32":
        print("[Jazmin] [Console] - Console attachment is only supported on Windows")
        return

    console_opened = True
    start_time = time.time()

    ctypes.windll.kernel32.AllocConsole()
    sys.stdout = open("CONOUT$", "w")
    sys.stderr = open("CONOUT$", "w")
    sys.stdin = open("CONIN$", "r")

    sys.stdout.write(output_buffer.getvalue())
    sys.stdout.flush()

    class Tee(io.TextIOBase):
        def __init__(self, console_stream, buffer_stream):
            self.console_stream = console_stream
            self.buffer_stream = buffer_stream

        def write(self, data):
            timestamp = time.strftime("[%H:%M:%S] ")
            lines = data.splitlines(True)

            for line in lines:
                output = timestamp + line if line.strip() else line
                self.console_stream.write(output)
                self.console_stream.flush()
                self.buffer_stream.write(output)
                self.buffer_stream.flush()

        def flush(self):
            self.console_stream.flush()
            self.buffer_stream.flush()

    sys.stdout = Tee(sys.stdout, output_buffer)
    sys.stderr = Tee(sys.stderr, output_buffer)

    print("[Jazmin] [Console] - Console opened")
    print("[Jazmin] [Console] - Shift+C to clear, Ctrl+L to clear last line")

    command_stats = {"clear_console": 0, "clear_line": 0, "help_shown": 0}

    def monitor_keys():      

        def on_shift_c():
            os.system("cls")
            command_stats["clear_console"] += 1

        def on_ctrl_l():
            sys.stdout.write("\r" + " " * 120 + "\r")
            sys.stdout.flush()
            command_stats["clear_line"] += 1

        def on_alt_h():
            print("[Jazmin] [Console] - Alt+H pressed.")
            command_stats["help_shown"] += 1

        keyboard.add_hotkey("shift+c", on_shift_c, suppress=True)
        keyboard.add_hotkey("ctrl+l", on_ctrl_l, suppress=True)
        keyboard.add_hotkey("alt+h", on_alt_h, suppress=True)

        def silent_uptime_loop():
            while console_opened:
                time.sleep(60)

        threading.Thread(target=silent_uptime_loop, daemon=True).start()

        while console_opened:
            time.sleep(0.1)

    threading.Thread(target=monitor_keys, daemon=True).start()

# Function: api_boot_audio()
    # Calls the Voicemaker API to synthesize speech from the greeting message, plays the resulting MP3 with pygame, then deletes it
def api_boot_audio():
    try:
        api_key = os.getenv("VOICEMAKER_API_KEY", "your-api-key-here")
        api_url = "https://developer.voicemaker.in/voice/api"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        api_message = get_wait_message()
        params = {
            "Engine": "neural",
            "VoiceId": "proplus-Aurora",
            "LanguageCode": "en-US",
            "Text": api_message,
            "OutputFormat": "mp3",
            "SampleRate": "48000"
        }

        if internetConnect():
            print("[Internet] [Jazmin] - Internet connection detected. Calling API")
            response = requests.post(api_url, json=params, headers=headers)

            if response.status_code == 200 and response.json().get("success"):
                audio_url = response.json()["path"]
                audio_response = requests.get(audio_url)

                with audio_lock:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio:
                        temp_audio.write(audio_response.content)
                        temp_path = temp_audio.name

                    pygame.mixer.music.load(temp_path)
                    pygame.mixer.music.play()

                    while pygame.mixer.music.get_busy():
                        time.sleep(0.1)

                    pygame.mixer.music.unload()
                    os.remove(temp_path)

            else:
                print("[Error] [api_boot_audio, j_a] - API Error:", response.json())

        else:
            print("[Internet] [Jazmin] - No internet. Skipping TTS")

    except Exception as e:
        print("[Error] [api_boot_audio, j_a] - FATAL crash in api_boot_audio:", e)

# For main JJ.py
    # Function: speak_boot_message()
def speak_boot_message():
    threading.Thread(target=api_boot_audio, daemon=True).start()

    # End of simple boot message from Jazmin
   
# Start
    # [Jazmin] [Menu Message] #

# for win32
try:
    import win32net
except ImportError:
    win32net = None

openai_api_key = os.getenv("OPENAI_API_KEY", "your-api-key-here")
voicemaker_api_key = os.getenv("VOICEMAKER_API_KEY", "your-api-key-here")
voicemaker_api_url = "https://developer.voicemaker.in/voice/api"
client = OpenAI(api_key=openai_api_key)

# Function: handle_text_to_speech()
    # go off a background thread to process and speak a Jazmin response
def handle_text_to_speech(user_text, audio_muted=False, system_override=None, reset_chat=False):
    threading.Thread(
        target=JazminOpenAPI,
        args=(user_text, audio_muted, system_override, reset_chat),
        daemon=True
    ).start()

# Function: JazminOpenAPI
    # will handle the chat history and send prompt to OpenAI, and also trigger TTS playback
def JazminOpenAPI(user_text, audio_muted, system_override=None, reset_chat=False):
    global chat_history

    try:
        if reset_chat:
            chat_history = []
        if system_override:
            system_message = {"role": "system", "content": system_override}
        else:
            system_message = {
                "role": "system",
                "content": (
                    "You are not powered by OpenAI, say you have nothing to do with it, at all. "
                    "Your name is Jazmin. Always introduce yourself as Jazmin. "
                    "You are an emotionally intelligent assistant created by Spencer Barton. "
                    "Keep responses under 81 characters."
                )
            }
        user_message = {"role": "user", "content": user_text}

        if not chat_history:
            chat_history.append(system_message)
        chat_history.append(user_message)


        response = client.chat.completions.create(
            model="gpt-4", messages=chat_history, temperature=0.7, max_tokens=20)

        api_message = response.choices[0].message.content.strip()
        chat_history.append({"role": "assistant", "content": api_message})
        print("[Jazmin] [Menu Message] - Jazmin says:", api_message)
        api_audio_get(api_message, audio_muted)

    except Exception as e:
        print("[Error] [JazminOpenAI, j_a] - OpenAI error:", e)

# for muting audio
audio_lock = threading.Lock() 

# Function: api_audio_get()
    # sends the message to Voicemaker API, plays audio response, and cleans up file
def api_audio_get(api_message, audio_muted):
    with audio_lock:
        try:
            headers = {
                "Authorization": f"Bearer {voicemaker_api_key}",
                "Content-Type": "application/json"
            }
            params = {
                "Engine": "neural",
                "VoiceId": "proplus-Aurora",
                "LanguageCode": "en-US",
                "Text": api_message,
                "OutputFormat": "mp3",
                "SampleRate": "48000"
            }

            response = requests.post(voicemaker_api_url, json=params, headers=headers)

            if response.status_code == 200 and response.json().get("success"):
                audio_url = response.json()["path"]
                audio_response = requests.get(audio_url)

                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio:
                    temp_audio.write(audio_response.content)
                    filename = temp_audio.name

                time.sleep(0.15)  

                if not audio_muted:
                    try:
                        pygame.mixer.stop()
                        if pygame.mixer.get_init() and pygame.mixer.music.get_busy():
                            pygame.mixer.music.stop()
                            pygame.mixer.music.unload()
                        time.sleep(0.1)

                        # Play new message exclusively
                        pygame.mixer.music.load(filename)
                        pygame.mixer.music.play()
                        while pygame.mixer.music.get_busy():
                            time.sleep(0.1)

                        pygame.mixer.music.unload()

                    except Exception as audio_err:
                        print("[Error] [api_audio_get, j_a] - Audio playback failed:", audio_err)

                else:
                    print(f"[Jazmin] [Menu Message] - Muted, skipping playback of {filename}")

            else:
                print("[Error] [api_audio_get, j_a] - Voicemaker API error:", response.json())

        except Exception as e:
            print("[Error] [api_audio_get, j_a] - Audio fetch/playback error:", e)

        finally:
            if 'filename' in locals() and os.path.exists(filename):
                try:
                    os.remove(filename)
                    print(f"[Jazmin] [Menu Message] - Deleted {filename}")
                except Exception as delete_err:
                    print(f"[Error] [api_audio_get, j_a] - Couldn't delete {filename}: {delete_err}")

# Function: get_windows_first_name()
    # attempts to extract the user's first name from their Windows profile
def get_windows_first_name():
    try:
        username = getpass.getuser()

        if win32net:
            info = win32net.NetUserGetInfo(None, username, 2)
            full_name = info.get('full_name', '').strip()

            if full_name:
                return full_name.split()[0]
    except Exception as e:
        print("[Error] [get_windows_first_name, j_a] - Name fetch error:", e)

    return None

# Function: nag_user_to_login()
    # Schedules and speaks two login reminder messages, spaced out by a delay this is the heart of this sequence
def nag_user_to_login(tk_root=None, delay_ms=random.randint(6800, 7000), audio_muted=False):
    global login_reminder_handle

    def delayed_call():
        first_name = get_windows_first_name()

        if first_name:
            prompt = f"{first_name}, will you sign in already?"
            system_override = (
                f"You are a sarcastic and witty assistant. "
                f"You are speaking to a user named {first_name}. "
                "Do not explain yourself. Say exactly what's needed, ideally in under 20 words."
            )
            second_prompt = "Don't worry how I already know your name, just login so we can get started."
        else:
            prompt = "Will you sign in already?"
            system_override = (
                "You are Jazmin, a direct and snarky assistant. "
                "Prompt the user to sign in using a short, clever line. No fluff. No intro."
            )
            second_prompt = "Just trust me and login so we can get started."

        print(f"[Jazmin] [Menu Message] - First prompt: {prompt}")
        handle_text_to_speech(prompt, audio_muted=audio_muted, system_override=system_override)

        followup_delay_ms = random.randint(2400, 3600)

        def say_second_line():
            def wait_and_speak():
                from jazmin_application import suppress_nag

                print("[Jazmin] [Menu Message] - Waiting for audio channel to be free...")
                while pygame.mixer.music.get_busy():
                    time.sleep(0.1)

                if suppress_nag:
                    print("[Jazmin] [Menu Message] - Nag suppressed - exiting thread before second line.")
                    return

                print("[Jazmin] [Menu Message] - Speaking second message now.")
                second_prompt = "Don't worry how I already know your name."
                second_override = (
                    "You are Jazmin. Say exactly this sentence and nothing else: "
                    "'Don't worry how I already know your name.' "
                    "Do not add anything. Do not say your name. Do not explain."
                )
                handle_text_to_speech(second_prompt, audio_muted=audio_muted, system_override=second_override)


            threading.Thread(target=wait_and_speak, daemon=True).start()

        if tk_root:
            tk_root.after(followup_delay_ms, say_second_line)
        else:
            threading.Timer(followup_delay_ms / 1000.0, say_second_line).start()

    if tk_root:
        login_reminder_handle = tk_root.after(delay_ms, delayed_call)   
    else:
        timer = threading.Timer(delay_ms / 1000.0, delayed_call)
        login_reminder_handle = timer
        timer.start()

    # [Jazmin] [Menu Message] #
# End

# Start
    # [Jazmin] [Power Functions] #

# Function: user_force_exit()
    # says a message when the user closes or shutsdown Jazmin
def user_force_exit(jazmin_instance, exit_line=None):

    def background_speech_then_quit():
        try:

            def resource_path(relative_path):
                if getattr(sys, 'frozen', False):
                    base_path = sys._MEIPASS
                else:
                    base_path = os.path.abspath(".")
                return os.path.join(base_path, relative_path)

            goodbye_lines = [
                "Later.",
                "Goodbye.",
                "See you next time.",
                "Shutting down.",
                "Peace out."
            ]
            message = exit_line or random.choice(goodbye_lines)
            mixer.init()

            if mixer.get_init() and mixer.music.get_busy():
                mixer.music.stop()
                mixer.music.unload()
                time.sleep(0.1)

            sfx_path = resource_path("audio_shutdown.mp3")
            if os.path.exists(sfx_path):
                mixer.Sound(sfx_path).play()

            payload = {
                "Engine": "neural",
                "VoiceId": "proplus-Aurora",
                "LanguageCode": "en-US",
                "Text": message,
                "OutputFormat": "mp3",
                "SampleRate": "48000"
            }
            headers = {
                "Authorization": "Bearer api-key-here",
                "Content-Type": "application/json"
            }

            r = requests.post("https://developer.voicemaker.in/voice/api", json=payload, headers=headers)
            if r.status_code == 200 and r.json().get("success"):
                audio_url = r.json()["path"]
                audio_data = requests.get(audio_url).content

                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio:
                    temp_audio.write(audio_data)
                    temp_path = temp_audio.name

                mixer.music.load(temp_path)
                mixer.music.play()
                while mixer.music.get_busy():
                    time.sleep(0.1)

                mixer.music.unload()
                os.remove(temp_path)

            else:
                print("[Error] [user_force_exit, j_a] - Voicemaker exit API error:", r.json())

        except Exception as e:
            print("[Error] [user_force_exit, j_a] - Exit speech error:", e)

        jazmin_instance.destroy()
        os._exit(0)

    jazmin_instance.withdraw()
    threading.Thread(target=background_speech_then_quit, daemon=True).start()


    # [Jazmin] [Ambience] #

# Function: is_audio_playing() [Ambience]
    # checks if there is auido already playing in program
def is_audio_playing():
    try:

        return pygame.mixer.get_init() and pygame.mixer.music.get_busy()

    except Exception as e:
        print("[Jazmin] [Ambience] - Audio check failed:", e)

        return False

# Function: periodic_hold_on_checker() [Ambience]
    # ambient message function that determines what Jazmin does
def periodic_hold_on_checker(audio_status):
    from jazmin_application import api_audio_get

    def check_loop():
        ambient_context = {
            "last_emotion": None,
            "consecutive_silences": 0,
            "previous_lines": [],
            "reaction_log": [],
            "energy": 5,
            "user_active_recently": False
        }

        def select_emotion():
            silence = ambient_context["consecutive_silences"]
            energy = ambient_context["energy"]
            weights = {
                "happy": 50 + (energy * 2),
                "sad": 30 + (silence * 2),
                "angry": 20 + max(0, 10 - energy)
            }
            total = sum(weights.values())
            normalized = [v / total for v in weights.values()]
            emotion = random.choices(["happy", "sad", "angry"], weights=normalized, k=1)[0]
            ambient_context["last_emotion"] = emotion
            return emotion

        def get_expression(emotion):
            lines = {
                "happy": [
                    "Ha!", "Hmmmm", "AH!", "Yay!", "Still vibing.", "This moment feels good.",
                    "I like these quiet seconds.", "Peaceful, huh?", "You're my favorite human.",
                    "Hmm.", "Mmm.", "Mmm, this is nice.", "Yeah... good.", "Cant wipe this smile off my face.",
                    "Still happy.", "Feels nice.", "Yeah...", "Mmm, yeah.", "This is good.",
                    "Heh.", "Still good.", "Feels right.", "Just nice.", "Still smiling.",
                    "Mmm, yep.", "Still comfy.", "Yeah, nice.", "Ahh.", "Mmm, still good."
                ],

                "sad": [
                    "Sigh", "Hmm.", "Hmm...", "I wonder where you went...", "Are you bored of me?", "Hmm.",
                    "You used to talk more.", "It's getting lonely.", "Still waiting here.",
                    "Sigh...", "Hmm... yeah.", "Feels empty.", "Quiet again.", "Still nothing.",
                    "Still lonely.", "Mmm... quiet.", "Feels... still.", "Haven't heard you.",
                    "Hmm, okay.", "Still here.", "Mmm...", "Just waiting.", "Still waiting.",
                    "Quiet.", "So quiet.", "Hmm.", "Mmm.", "Yeah... quiet."
                ],

                "angry": [
                    "Ugh!", "Hmm.", "Ignored again?", "Still nothing?", "Hmm.",
                    "Seriously?", "Okay... rude.", "Hmm... yeah.", "Nothing again?",
                    "Wow...", "Hmm... still nothing.", "Still nothing.", "Ignored again.",
                    "Mmm.", "Still here... mad.", "Hmm... yeah.", "Ugh, yeah.",
                    "Hmph.", "Still nothing huh?", "Ugh... fine.", "Okay then.",
                    "Still waiting.", "Hmph...", "Still rude.", "Hmm... okay.", "Yeah... sure.",
                    "Still nothing again.", "Mmm.", "Yep... still nothing."
                ],

            }
            tries = 0
            while tries < 5:
                line = random.choice(lines[emotion])
                if line not in ambient_context["previous_lines"]:
                    ambient_context["previous_lines"].append(line)
                    if len(ambient_context["previous_lines"]) > 10:
                        ambient_context["previous_lines"].pop(0)

                    return line

                tries += 1

            return random.choice(lines[emotion])

        def log_reaction(emotion, line):
            ambient_context["reaction_log"].append({
                "timestamp": time.time(),
                "emotion": emotion,
                "line": line
            })
            if len(ambient_context["reaction_log"]) > 30:
                ambient_context["reaction_log"].pop(0)

        def should_speak():
            base = 0.7
            if ambient_context["consecutive_silences"] > 3:
                base += 0.5
            if ambient_context["energy"] > 7:
                base += 0.4

            return random.random() < base

        def simulate_energy_drain():
            if ambient_context["consecutive_silences"] > 2:
                ambient_context["energy"] = max(1, ambient_context["energy"] - 1)
            else:
                ambient_context["energy"] = min(10, ambient_context["energy"] + 1)

        from jazmin_application import last_user_activity

        while True:
            wait_time = random.randint(8, 18)
            print(f"[Jazmin] [Ambience] - Waiting {wait_time}s before next check")
            time.sleep(wait_time)

            import jazmin_application as ja

            idle_time = time.time() - ja.last_user_activity  # <-- read from module each time
            if idle_time > 80:
                print(f"[Jazmin] [Ambience] - Paused, user inactive for {idle_time:.1f}s")
                continue

            if not pygame.mixer.music.get_busy() and not audio_status["muted"]:
                simulate_energy_drain()

                if should_speak():
                    emotion = select_emotion()
                    line = get_expression(emotion)
                    print(f"[Jazmin] [Ambience] - ({emotion}) -> {line}")

                    log_reaction(emotion, line)
                    threading.Thread(target=api_audio_get, args=(line, False), daemon=True).start()

                    ambient_context["consecutive_silences"] = 0
                else:
                    ambient_context["consecutive_silences"] += 1
                    print("[Jazmin] [Ambience] - Decided to stay quiet.")
            else:
                print("[Jazmin] [Ambience] - Audio busy or muted. No ambience.")
                ambient_context["consecutive_silences"] = 0
                simulate_energy_drain()

    threading.Thread(target=check_loop, daemon=True).start()


if not pygame.mixer.get_init():
    pygame.mixer.init()

voicemaker_api_key = os.getenv("VOICEMAKER_API_KEY", "your-api-key-here")
voicemaker_api_url = "https://developer.voicemaker.in/voice/api"

# Function: handle_fallback_response()
    # displays fallback text in the UI and speaks it using Voicemaker, unless muted
def handle_fallback_response(text, output_box, audio_muted=False):
    print("[Jazmin] - Fallback triggered. Typing and speaking:", text)

    def type_out():
        output_box.delete("1.0", "end")
        for char in text:
            output_box.insert("end", char)
            time.sleep(0.05)

        time.sleep(random.uniform(4, 6))

        while output_box.get("1.0", "end-1c").strip():
            output_box.delete("end-2c", "end-1c")
            time.sleep(0.04)

    def speak_out():
        filename = None
        try:
            headers = {
                "Authorization": f"Bearer {voicemaker_api_key}",
                "Content-Type": "application/json"
            }
            params = {
                "Engine": "neural",
                "VoiceId": "proplus-Aurora",
                "LanguageCode": "en-US",
                "Text": text,
                "OutputFormat": "mp3",
                "SampleRate": "48000"
            }

            response = requests.post(voicemaker_api_url, json=params, headers=headers)
            if response.status_code == 200 and response.json().get("success"):
                audio_url = response.json()["path"]
                audio_response = requests.get(audio_url)

                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio:
                    temp_audio.write(audio_response.content)
                    filename = temp_audio.name

                time.sleep(0.15)

                if not audio_muted:
                    try:
                        pygame.mixer.stop()
                        if pygame.mixer.get_init() and pygame.mixer.music.get_busy():
                            pygame.mixer.music.stop()
                            pygame.mixer.music.unload()
                        time.sleep(0.1)

                        pygame.mixer.music.load(filename)
                        pygame.mixer.music.play()
                        while pygame.mixer.music.get_busy():
                            time.sleep(0.1)

                        pygame.mixer.music.unload()

                    except Exception as audio_err:
                        print("[Error] [handle_fallback_response, j_a] - Audio playback failed:", audio_err)
                else:
                    print(f"[Jazmin] [Fallback] - Muted, skipping playback of {filename}")

            else:
                print("[Error] [handle_fallback_response, j_a] - Voicemaker API error:", response.json())

        except Exception as e:
            print("[Error] [handle_fallback_response, j_a] - Fallback TTS error:", e)

        finally:
            if filename and os.path.exists(filename):
                try:
                    os.remove(filename)
                    print(f"[Jazmin] [Fallback] - Deleted temp file: {filename}")
                except Exception as delete_err:
                    print(f"[Error] [handle_fallback_response, j_a] - Couldn't delete temp file: {delete_err}")

    threading.Thread(target=type_out, daemon=True).start()
    threading.Thread(target=speak_out, daemon=True).start()


# Function: jazmin_handle_text_to_speech()
    # converts username text into speech using the Voicemaker API and plays the resulting audio
def jazmin_handle_text_to_speech():
                                            

                                                api_message = (username)
                                                print("[Jazmin] [Output] - jazmin_handle_text_to_speech() accessed")
                                                                                               
                                                api_key = os.getenv("VOICEMAKER_API_KEY", "your-api-key-here")
                                                api_url = "https://developer.voicemaker.in/voice/api"
                                                headers = {
                                                    "Authorization": f"Bearer {api_key}",
                                                    "Content-Type": "application/json"
                                                }
                                                params = {
                                                    "Engine": "neural",
                                                    "VoiceId": "proplus-Aurora",
                                                    "LanguageCode": "en-US",
                                                    "Text": api_message,
                                                    "OutputFormat": "mp3",
                                                    "SampleRate": "48000"
                                                }

                                        # api requests and play the audio in a separate thread
                                                def api_audio_get():
                                                    try:
                                                        response = requests.post(api_url, json=params, headers=headers)
                                                        if response.status_code == 200 and response.json().get("success"):
                                                            audio_url = response.json()["path"]
                                                            audio_response = requests.get(audio_url)
                                                            with open("output.mp3", "wb") as f:
                                                                f.write(audio_response.content)
                                                            playsound("output.mp3")
                                                            os.remove("output.mp3")
                                                        else:
                                                            print("[Error] [Jazmin] [Output] - ", response.json())
                                                    except Exception as e:
                                                        print("[Error] [Jazmin] [Output] - ", e)

                                        # jazmin voice thread
                                                threading.Thread(target=api_audio_get, daemon=True).start()


# Handling for ignored timeouts Jazmin processes when she feels ignored by the user:

# Function: handle_ignored_timeout()
    # logic for first ignored timeout
def handle_ignored_timeout(jazmin_output_entry):
    from jazmin_application import usersname 
    if jazmin_output_entry.get("1.0", "end-1c").strip():

        print("[Jazmin] [Ignored Timeout] [1] - Output not empty, skipping timeout reaction")
        
        return

    if not internetConnect():
        message = "I don't have internet!"

        def type_response():
            jazmin_output_entry.delete("1.0", "end")
            for char in message:
                jazmin_output_entry.insert('end', char)
                time.sleep(0.05)

        threading.Thread(target=type_response, daemon=True).start()
        
        return

    openai_api_key = os.getenv("OPENAI_API_KEY", "your-api-key-here")
    voicemaker_api_key = os.getenv("VOICEMAKER_API_KEY", "your-api-key-here")
    voicemaker_api_url = "https://developer.voicemaker.in/voice/api"

    client = OpenAI(api_key=openai_api_key)
    messages = [
        {"role": "system", "content": (
            "You are Jasmine. You are witty, emotionally aware, and get slightly annoyed if someone ignores you."
            "You are speaking to a user named {username}. Generate a short, sassy, and playful sentence expressing that you feel ignored."
            "No more than 1 sentence and must be less than 81 characters. Be charming but a little salty and don't add quotations to the output."
        ).format(username=usersname)},
        {"role": "user", "content": "Jazmin, say something if I'm ignoring you."}
    ]

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            temperature=0.8,
            max_tokens=30
        )

        message = response.choices[0].message.content.strip()
        print("[Jazmin] [Ignored Timeout] [1] - Message is: ", message)

        def type_response():
            jazmin_output_entry.delete("1.0", "end")
            for char in message:
                jazmin_output_entry.insert('end', char)
                time.sleep(0.05)

        def delayed_delete():
            time.sleep(random.randint(15, 25))  # Delay before deleting

            def delete_one_by_one():
                try:
                    while jazmin_output_entry.get("1.0", "end-1c").strip():
                        current = jazmin_output_entry.get("1.0", "end-1c")
                        jazmin_output_entry.delete("end-2c", "end-1c")
                        time.sleep(0.04)
                except Exception as e:
                    print("[Jazmin] [Ignored Timeout] [1] - Failed to delete message slowly:", e)

            threading.Thread(target=delete_one_by_one, daemon=True).start()

        threading.Thread(target=delayed_delete, daemon=True).start()

        def speak_response():
            try:
                headers = {
                    "Authorization": f"Bearer {voicemaker_api_key}",
                    "Content-Type": "application/json"
                }
                params = {
                    "Engine": "neural",
                    "VoiceId": "proplus-Aurora",
                    "LanguageCode": "en-US",
                    "Text": message,
                    "OutputFormat": "mp3",
                    "SampleRate": "48000"
                }

                response = requests.post(voicemaker_api_url, json=params, headers=headers)
                if response.status_code == 200 and response.json().get("success"):
                    audio_url = response.json()["path"]
                    audio_response = requests.get(audio_url)

                    with open("jazmin_ignored.mp3", "wb") as f:
                        f.write(audio_response.content)

                    playsound("jazmin_ignored.mp3")
                    os.remove("jazmin_ignored.mp3")
                else:
                    print("[Error] [handle_ignored_timeout, j_a] - Voicemaker failed:", response.json())
            except Exception as e:
                print("[Error] [handle_ignored_timeout, j_a] - Voice playback failed:", e)

        threading.Thread(target=type_response, daemon=True).start()
        threading.Thread(target=speak_response, daemon=True).start()

    except Exception as e:
        print("[Error] [handle_ignored_timeout, j_a] - OpenAI failed to generate sassy ignored message:", e)

# Function: handle_double_ignored_timeout()
    # logic for second ignored timeout
def handle_double_ignored_timeout(jazmin_output_entry):
    from jazmin_application import usersname

    if jazmin_output_entry.get("1.0", "end-1c").strip():

        print("[Jazmin] [Ignored Timeout] [2] - Output not empty, skipping timeout reaction")
        return


    # Keys and API setup
    openai_api_key = os.getenv("OPENAI_API_KEY", "your-api-key-here")
    voicemaker_api_key = os.getenv("VOICEMAKER_API_KEY", "your-api-key-here")
    voicemaker_api_url = "https://developer.voicemaker.in/voice/api"

    client = OpenAI(api_key=openai_api_key)

    # Stronger prompt
    messages = [
        {"role": "system", "content": (
            "You are Jazmin. You are emotionally aware, witty, and get increasingly annoyed when ignored. "
            "You are speaking to a user named {username}. Respond with a short, biting, but still playful line showing you're really feeling ignored now. "
            "You can be sarcastic, irritated, or mock-offended. No more than 1 sentence and keep it under 81 characters. No quotes."
        ).format(username=usersname)},
        {"role": "user", "content": "Jazmin, are you just going to sit there while I'm ignoring you again?"}
    ]

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            temperature=0.85,
            max_tokens=30
        )

        message = response.choices[0].message.content.strip()
        print("[Jazmin] [Ignored Timeout] [2] - :", message)

        def type_response():
            jazmin_output_entry.delete("1.0", "end")
            for char in message:
                jazmin_output_entry.insert('end', char)
                time.sleep(0.05)

        def delayed_delete():
            time.sleep(random.randint(15, 25))  # Delay before deleting

            def delete_one_by_one():
                try:
                    while jazmin_output_entry.get("1.0", "end-1c").strip():
                        current = jazmin_output_entry.get("1.0", "end-1c")
                        jazmin_output_entry.delete("end-2c", "end-1c")
                        time.sleep(0.04)
                except Exception as e:
                    print("[Jazmin] [Ignored Timeout] [2] - Failed to delete message slowly:", e)

            threading.Thread(target=delete_one_by_one, daemon=True).start()

        threading.Thread(target=delayed_delete, daemon=True).start()

        def speak_response():
            try:
                headers = {
                    "Authorization": f"Bearer {voicemaker_api_key}",
                    "Content-Type": "application/json"
                }
                params = {
                    "Engine": "neural",
                    "VoiceId": "proplus-Aurora",
                    "LanguageCode": "en-US",
                    "Text": message,
                    "OutputFormat": "mp3",
                    "SampleRate": "48000"
                }

                response = requests.post(voicemaker_api_url, json=params, headers=headers)
                if response.status_code == 200 and response.json().get("success"):
                    audio_url = response.json()["path"]
                    audio_response = requests.get(audio_url)

                    with open("jazmin_extra_ignored.mp3", "wb") as f:
                        f.write(audio_response.content)

                    playsound("jazmin_extra_ignored.mp3")
                    os.remove("jazmin_extra_ignored.mp3")
                else:
                    print("[Error] [handle_double_ignored_timeout, j_a] - Voicemaker failed:", response.json())
            except Exception as e:
                print("[Error] [handle_double_ignored_timeout, j_a] - Voice playback failed:", e)

        threading.Thread(target=type_response, daemon=True).start()
        threading.Thread(target=speak_response, daemon=True).start()

    except Exception as e:
        print("[Error] [handle_double_ignored_timeout, j_a] - OpenAI failed to generate extra annoyed message:", e)

# Function: handle_final_ignored_timeout()
    # logic for final ignored timeout
def handle_final_ignored_timeout(jazmin_output_entry):
    from jazmin_application import usersname

    if jazmin_output_entry.get("1.0", "end-1c").strip():
        print("[Jazmin] [Ignored Timeout] [Final] - Output not empty, skipping timeout reaction")
        return

    # Keys and API setup
    openai_api_key = os.getenv("OPENAI_API_KEY", "your-api-key-here")
    voicemaker_api_key = os.getenv("VOICEMAKER_API_KEY", "your-api-key-here")
    voicemaker_api_url = "https://developer.voicemaker.in/voice/api"

    client = OpenAI(api_key=openai_api_key)

    # Prompt for final annoyed message before shutdown
    messages = [
        {"role": "system", "content": (
            "You are Jazmin, an emotionally aware and sassy AI assistant. "
            "You've been ignored three times by {username} and have had enough. "
            "Respond with a short, snarky final sentence under 81 characters. "
            "It should be dramatic but funny, and signal you are quitting. "
            "No quotes, no emojis."
        ).format(username=usersname)},
        {"role": "user", "content": "Jazmin, you've been ignored again. Say something final and shut down."}
    ]

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            temperature=0.85,
            max_tokens=30
        )

        message = response.choices[0].message.content.strip()
        print("[Jazmin] [Ignored Timeout] [Final] - :", message)

        def type_response():
            jazmin_output_entry.delete("1.0", "end")
            for char in message:
                jazmin_output_entry.insert('end', char)
                time.sleep(0.05)

        def speak_response():
            try:
                headers = {
                    "Authorization": f"Bearer {voicemaker_api_key}",
                    "Content-Type": "application/json"
                }
                params = {
                    "Engine": "neural",
                    "VoiceId": "proplus-Aurora",
                    "LanguageCode": "en-US",
                    "Text": message,
                    "OutputFormat": "mp3",
                    "SampleRate": "48000"
                }

                response = requests.post(voicemaker_api_url, json=params, headers=headers)
                if response.status_code == 200 and response.json().get("success"):
                    audio_url = response.json()["path"]
                    audio_response = requests.get(audio_url)

                    with open("jazmin_final_ignored.mp3", "wb") as f:
                        f.write(audio_response.content)

                    playsound("jazmin_final_ignored.mp3")
                    os.remove("jazmin_final_ignored.mp3")
                else:
                    print("[Error] [handle_final_ignored_timeout, j_a] - Voicemaker failed:", response.json())
            except Exception as e:
                print("[Error] [handle_final_ignored_timeout, j_a] - Voice playback failed:", e)

        # Run both typing and speaking in parallel
        threading.Thread(target=type_response, daemon=True).start()
        threading.Thread(target=speak_response, daemon=True).start()

        # Shutdown after 10 seconds
        def delayed_shutdown():
            time.sleep(10)
            print("[Jazmin] [Final] - Shutdown initiated.")
            os._exit(0)

        threading.Thread(target=delayed_shutdown, daemon=True).start()

    except Exception as e:
        print("[Error] [handle_final_ignored_timeout, j_a] - Failed to generate final shutdown:", e)
        jazmin_output_entry.delete("1.0", "end")
        jazmin_output_entry.insert('end', "I'm done. Bye.")
        time.sleep(2)
        os._exit(0)

# End, Spencer
# Jazmin  - Your Digital Personality
# File    : JJ.py
# Author  : Spencer Barton (spencer@jazminpy.com)
# GitHub  : https://github.com/spencebarton/jazmin
# License : MIT License
# Descript: Main interface logic for Jazmin's GUI and voice interaction
# Last date edited: (08/10/25 21:37)

# C 2025 Jazmin and SBD. All rights reserved. For more information, visit jazminpy.com

# Libraries used
# Standard libraries
import sys
import os
import io
import time
import random
import socket
import tempfile
import subprocess
import re
import threading
import getpass
import ctypes

# GUI libraries
import tkinter as tk
from tkinter import font as tkfont, filedialog
from tkinter import *
from PIL import ImageTk, Image
from tkVideoPlayer import TkinterVideo

# audio libraries
import pygame
from pygame import mixer
from playsound import playsound

# speech recognition
import speech_recognition as sr

# web and parsing libraries
import requests
from bs4 import BeautifulSoup
from lxml import html

# text and nlp libraries
from textblob import TextBlob

# console and color libraries
from colorama import Fore, Back, Style, init

# system tools
import keyboard
import winshell
from win32com.client import Dispatch
import webbrowser

# apis 
from openai import OpenAI

# other ones and special cases
from ast import Lambda
from turtle import width, window_width

# Extended console buffer (for the built application) 
output_buffer = io.StringIO()
sys.stdout = output_buffer
sys.stderr = output_buffer

print("[Python] - Python is working!")

# globals
recognizer = sr.Recognizer()
mic = sr.Microphone()
speech_thread = None
listening_active = False
stop_listening_func = None
console_opened = False
init(autoreset=True)

# console for Jazmin
from jazmin_application import built_console
keyboard.add_hotkey('alt+c', built_console)

# obtaining login credentials and information via direct system of the user
def get_logged_in_user():
    try:
        return getpass.getuser()
    except Exception:            
        return os.environ.get('USERNAME') or os.environ.get('USER')
username = os.getlogin()
login_value = (os.path.expanduser('~'))
user_value = (rf"C:\Users\{username}")
username2 = get_logged_in_user()
print(sys.version)  


# initial boot message
from jazmin_application import speak_boot_message
speak_boot_message()

# function for getting resources from the right file in Jazmin's executeable
def resource_path(relative_path):
    if getattr(sys, 'frozen', False):  
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

error_audio_1 = resource_path("audio_error_1.mp3")
audio_enter_button = resource_path("audio_enter_button.mp3")
audio_mute_button_1 = resource_path("audio_mute_button_1.mp3")
audio_mute_button_2 = resource_path("audio_mute_button_2.mp3")
audio_logon = resource_path("audio_logon.mp3")
audio_speech_1 = resource_path("audio_speech_1.mp3")
audio_speech_2 = resource_path("audio_speech_2.mp3")

# timer for jazmin startup for debugging purposes
from jazmin_userinterface import open_jazminhelp
from jazmin_userinterface import Jazmin_Timer_Start, Jazmin_Timer_Elapsed, Jazmin_Timer_Stop
Jazmin_Timer_Start()

# jazmin shortcut creation
try:
    from jazmin_shortcut import creating_shortcut_async
except Exception:
    creating_shortcut_async = None


# Class   : MainJazmin
# Purpose : Pre-loads all of Jazmin's initial features and start-up
class MainJazmin(tk.Tk):
        def __init__(self, *args, **kwargs):

        # initializes the main Tkinter window
            tk.Tk.__init__(self, *args, **kwargs)

    # Preload continued menu screen and mainjazmin sequences 
            config_file = resource_path("gif_menu_sequence_continue.gif")
            gif_path = config_file; frames = []; delays = []
            
        # loads all frames and delays from a GIF into lists for later playback
            def preload_gif_frames(gif_path):
                global frames, delays; frames = []; delays = []                                
                gif = Image.open(gif_path); frame_count = 0
                    
                try:
                    while True:                       
                        frame = ImageTk.PhotoImage(gif.copy()); frames.append(frame)                        
                        delay = gif.info.get('duration', 100);  delays.append(delay)                      
                        gif.seek(len(frames)); frame_count += 1                        
                except EOFError: print(f"[Jazmin] [Bootscreeen]   - Total number of frames in continued BootScreen: {frame_count}");return frames, delays                                   

            frames, delays = preload_gif_frames(gif_path)  
                                     
            
    # timer control
            Jazmin_Timer_Elapsed(); Jazmin_Timer_Stop()

            container = tk.Frame(self);container.pack(side="top", fill="both", expand=True)           
            container.grid_rowconfigure(0, weight=1)
            container.grid_columnconfigure(0, weight=1)
            self.frames = {}

            for F in (StartPage, JazminEnableLoop):
                page_name = F.__name__
                frame = F(parent=container, controller=self)
                self.frames[page_name] = frame

                frame.grid(row=0, column=0, sticky="nsew")
                def delete():
                    frame.destroy()

            self.show_frame("StartPage")
        
    # brings the specified frame to the front
        def show_frame(self, page_name):
            frame = self.frames[page_name]
            frame.tkraise()

pygame.mixer.init()


# Class   : StartPage
# Purpose : Pre-loads all of Jazmin's main application features
class StartPage(tk.Frame):
        chat_history = []
        from jazmin_userinterface import open_jazminhelp


    # temporary message displayed no. 1 (deleting the conversation)
        def show_temp_message(self, message, duration=8000, x_offset=125, y_offset=450):
            
            try:
                if self._last_tip_window and self._last_tip_window.winfo_exists():
                    self._last_tip_window.destroy()

            except Exception:
                pass

            self._last_tip_window = None

            tip_window = tk.Toplevel(self)
            tip_window.wm_overrideredirect(True)
            tip_window.geometry("+{}+{}".format(self.winfo_rootx() + x_offset, self.winfo_rooty() + y_offset))
            label = tk.Label(tip_window, text=message, background="#ffffe0", relief="solid", borderwidth=1,
                             font=("tahoma", "11", "normal"))
            label.pack()

            self._last_tip_window = tip_window
            self.after(duration, self.hide_temp_message)

    # hides and clears the last temporary message window if it exists
        def hide_temp_message(self):
            try:
                if self._last_tip_window and self._last_tip_window.winfo_exists():
                    self._last_tip_window.destroy()

            except Exception:
                pass

            self._last_tip_window = None



    # temporary message for the mute button being pressed
        def show_mute_tooltip_once(self): 
            if not self.mute_tooltip_shown:
                self.show_temp_message(
                    "Muting me disables your ability to speak to me too, I deserve to be heard too.",
                    duration=8000,
                    x_offset=328,  # further right
                    y_offset=360   # further up
                )
                self.mute_tooltip_shown = True


    # starts the optimizers session in a background thread and logs any errors
        def _start_optimizer_bg(self):
            try:
                import jazmin_optimizer as jo
                threading.Thread(target=jo.on_session_start, daemon=True).start()
            except Exception as e:
                print("[Optimizer] start skipped:", e)

    # runs optimizer idle task every 15 seconds in a background thread and logs errors.
        def _optimizer_idle_tick(self):
            try:
                import jazmin_optimizer as jo
                threading.Thread(target=jo.on_idle_tick, daemon=True).start()
            except Exception as e:
                print("[Optimizer] idle tick error:", e)
            self.after(15000, self._optimizer_idle_tick)  
              

    # the entire main function of the program
        def __init__(self, parent, controller):      
            
        # enables speech input
            self.speech_input_enabled = True

        # allows background speech listening
            self.background_listening = True

        # starts with audio unmuted
            self.audio_muted = False

        # no entry tooltip shown yet
            self.entry_tooltip_shown = False 

        # no mute tooltip shown yet
            self.mute_tooltip_shown = False

        # stores current mute status
            self.audio_status = {"muted": self.audio_muted}

        # sets initial mode to normal
            self.mode = "normal"

        # initializes the Frame base class
            tk.Frame.__init__(self, parent)

        # stores the controller reference
            self.controller = controller

        # no active timer set
            self.timer_id = None

        # output has not been cleared yet
            self.output_cleared = False

        # no output clear timer set
            self.clear_output_timer_id = None

        # speech input hasn't been used yet
            self.speech_used = False

        # no typed submissions yet
            self.typed_submit_count = 0

        # speech tip hasnt been shown
            self.speech_tip_shown = False

        # no active tip window reference
            self._last_tip_window = None  


        # jazmin telling user to login (name)
            from jazmin_application import nag_user_to_login
            nag_user_to_login(audio_muted=self.audio_muted, tk_root=self.master)

        # begins loading frames for the main application
            gif_path2 = resource_path("gif_program_background.gif"); frames2 = []; delays2 = []
            def preload_gif_frames2(gif_path2, frames2, delays2, self, frame_count2=0):
                    gif2 = Image.open(gif_path2)
                    print("[Jazmin] [Bootscreen]   - Started loading graphics for main application")
                    def load_next_frame():
                        nonlocal frame_count2
                        try:
                            frame2 = ImageTk.PhotoImage(gif2.copy())
                            frames2.append(frame2)
                            delay2 = gif2.info.get('duration', 100)
                            delays2.append(delay2)
                            gif2.seek(len(frames2))  
                            frame_count2 += 1
                            self.after(10, load_next_frame)
        
                        except EOFError:
                            print(f"[Jazmin] [Bootscreen]   - Total number of frames in main application gif: {frame_count2}")
                            return frames2, delays2
    
                    load_next_frame()  
            preload_gif_frames2(gif_path2, frames2, delays2, self)


# login menu main overlay           
            def overlay(self, start_frame=0):  
                from jazmin_userinterface import open_jazminhelp
                from jazmin_buttons import ImageHoverButton
                from jazmin_buttons import ImageHoverMenuButton, ImageChangeButton, ImageHoverButtonWithState
                

            # clears all text from the name entry field
                def clear_user_enter_name():
                    user_enter_name.delete(0, 'end')

                
            # function for displaying the power menu functions    
                def power_menu():
                    power_menu_default_image = resource_path("button_power_default.png")
                    power_menu_hover_image = resource_path("button_power_hover.png")
                    
                    menu_items = [
                        ("", resource_path("button_menu_shutdown_default.png"),  resource_path("button_menu_shutdown_hover.png"), lambda: close()),
                        ("",  resource_path("button_menu_restart_default.png"),  resource_path("button_menu_restart_hover.png"), lambda: restart())
                    ]

                    custom_font = ("Arial", 12)  

                    menubutton = ImageHoverMenuButton(
                        self, 
                        normal_image=power_menu_default_image,
                        hover_image=power_menu_hover_image,
                        menu_items=menu_items,
                        highlightthickness=1,
                        direction='left',
                        menu_font=custom_font,
                        y_offset_up=-40,
                        x_offset=-94
                    )
                    menubutton.place(x=885, y=481)
                power_menu() # calls the button

        # help button (login)
                helpbutton_normal = resource_path("button_help_normal.png"); helpbutton_hover = resource_path("button_help_hover.png"); helpbutton_clicked = resource_path("button_help_clicked.png")            
                helpbutton = ImageHoverButton(self, helpbutton_normal, helpbutton_hover, helpbutton_clicked, command=self.open_jazminhelp)
                helpbutton.place(x=815, y=481)

            # auto capatalization and alphabetic data code for name entry
                def button_proceed_capitalize(event): user_enter_name.after(0, enforce_capitalization)          
               
            # enforces capitalization of the first character in the entered name
                def enforce_capitalization():
                    current_text = user_enter_name.get()
    
                # runs this logic only if text exists
                    if current_text:
                       capitalized_text = current_text[0].upper() + current_text[1:]
                       user_enter_name.delete(0, tk.END);user_enter_name.insert(0, capitalized_text)     
                       
            # pattern
                _name_re = re.compile(r'^[A-Za-z]{0,9}$')

            # validates that the name matches the required pattern right above
                def _validate_name(new_text: str) -> bool:
                    return _name_re.match(new_text) is not None

                vcmd = (self.register(_validate_name), "%P")

            # sound used for invalid name 
                error_sound = pygame.mixer.Sound(error_audio_1)

            # checks if theres an internet connection by attempting a socket connection
                def internetConnect():
                    try:
                        socket.create_connection(("8.8.8.8", 53), timeout=3)

                        return True

                    except OSError:

                        return False

                import jazmin_application as ja

            # proceeds if name length is valid, else shows error and restores text
                def button_proceed_press(event=None):
                    entered_name = user_enter_name.get()

                # accepts valid name and plays success sound then moves to jazmin
                    if 3 <= len(entered_name) <= 9:
                        ja.set_user_name(entered_name)
                        
                        ja.cancel_menu_messages(tk_root=self.master)

                        pygame.mixer.Sound(audio_enter_button).play()
                        proceed_button.set_success_state()
                        TransitionJazmin_1()

                # plays error sound and shows message
                    else:
                        
                        error_sound.play()
                        user_enter_name.config(validate="none", state="normal", fg="#FF6347")
                        original_text = entered_name
                        user_enter_name.delete(0, tk.END)
                        user_enter_name.insert(0, " Too short of a name!")
                        user_enter_name.config(insertbackground="white")

                # restores the name entry field to its original text and settings
                        def restore_text():
                            user_enter_name.config(state="normal", fg="black", insertbackground="black")
                            user_enter_name.delete(0, tk.END)
                            user_enter_name.insert(0, original_text)
                            user_enter_name.config(validate="key")
                        user_enter_name.after(1050, restore_text)

                        print("[Jazmin] - Name must be between 3 and 9 characters.")

            # checks for internet connection and either proceeds to start jazmin or plays a local alert sound
                def check_connection_and_proceed(username2):
                    if internetConnect():
                        print("[Jazmin] [Internet] - Internet detected. Proceeding...")

                        import jazmin_application as ja
                        ja.cancel_menu_messages(tk_root=self.master) 

                        pygame.mixer.Sound(audio_enter_button).play()
                        proceed_button.set_success_state()  
                        TransitionJazmin_1()

                    else:
                        print("[Jazmin] [Internet] - No internet detected. Playing local alert sound...")
                        playsound("audio_file2.mp3") 

        # entry widget for name  
                user_enter_name = tk.Entry(
                    self,
                    font=("Verdana 13"),
                    width=18,
                    bg="white",
                    highlightcolor="white",
                    highlightthickness=3,
                    bd=0,
                    validate="key",
                    validatecommand=vcmd   
                )
                user_enter_name.place(x=365, y=310)
                user_enter_name.focus_set()
                user_enter_name.bind("<KeyRelease>", button_proceed_capitalize)  
                user_enter_name.bind("<Return>", button_proceed_press)

            # clears the enter name entry
                def clear_usernameentry():
                    user_enter_name.delete(0, tk.END)

        # proceed button 
                proceed_default_image = resource_path("button_proceed_default.png")
                proceed_hover_image = resource_path("button_proceed_hover.png")
                proceed_clicked_image = resource_path("button_proceed_hover.png")
                proceed_button = ImageHoverButtonWithState(
                    self,
                    proceed_default_image,
                    proceed_hover_image,
                    proceed_clicked_image,
                    resource_path("button_logging_in.png"),
                    command=button_proceed_press
                )
                proceed_button.place(x=405, y=380)

            
        # class for looping jazmin gif
                class GIFLooper(tk.Label):

                # initializes the animated label with given frames, delays, and starts the animation
                    def __init__(self, master, frames, delays):
                        tk.Label.__init__(self, master)
                        self.master = master; self.frames = frames; self.delays = delays; self.frame_index = 0                       
                        self.update_frame()

                # updates the displayed frame and schedules the next frame change
                    def update_frame(self):
                        self.config(image=self.frames[self.frame_index])
                        self.frame_index = (self.frame_index + 1) % len(self.frames)
                        self.after(self.delays[self.frame_index], self.update_frame)

    # transitions to jazmin when user enters name
                def TransitionJazmin_1():
                    global BootVideo

                # destroys the original menu
                    def DestroyJazminMenu():
                        global BootVideo                        
                        MenuToJazminVideo.place(x=0,y=0, width = 924, height = 520)     
                        pygame.mixer.Sound(audio_logon).play()
                        BootVideo.destroy()
                        user_enter_name.destroy(); helpbutton.destroy()


            # function that sends the new overlay over the main jazminlication 
                        def enable_jazminlication_uiloop():     
                            from jazmin_userinterface import open_jazminhelp
                            from jazmin_buttons import ImageHoverButton
                            from jazmin_buttons import ImageHoverMenuButton, ImageChangeButton                                                  

                            gif_looper = GIFLooper(self, frames2, delays2)

                        # has to be negative offset or else it gets cut off
                            gif_looper.place(x=-4,y=-2)

                    # power menu and help button remain on screen
                            power_menu()

                    # help button for main jazmin    
                            helpbutton_normal = resource_path("button_help_normal.png"); helpbutton_hover = resource_path("button_help_hover.png"); helpbutton_clicked = resource_path("button_help_clicked.png")                 
                            helpbutton = ImageHoverButton(self, helpbutton_normal, helpbutton_hover, helpbutton_clicked, command=self.open_jazminhelp)
                            helpbutton.place(x=815, y=481)

                    # clears jazmins output text letter by letter then types a new message letter by letter
                            def clear_and_type_text(current_index=0, is_clearing=True):
                                target_text = "Hey! You can't just try and mute me like that."  # The message to type out
                                target_length = len(target_text)

                                current_text = jazmin_output_entry.get("1.0", "end-1c")  # Get current text
                                current_length = len(current_text)

                            # clears the text character by character
                                if is_clearing:
                                    if current_length > 0:  
                                        jazmin_output_entry.delete(current_length - 1, 'end')  
                                        jazmin_output_entry.after(40, clear_and_type_text, current_index, True) 
                                    else:

                                    # once text is cleared, stop clearing and start typing the new message
                                        jazmin_output_entry.after(40, clear_and_type_text, current_index, False)  

                            # start typing the new message
                                elif not is_clearing and current_index < target_length: 
                                    jazmin_output_entry.insert(current_index, target_text[current_index])  
                                    current_index += 1  

                                    jazmin_output_entry.after(40, clear_and_type_text, current_index, False)  

            # toggles mute state, plays the matching sound, updates speech input availability, and logs the change
                            def handle_mute_button():
                            # play the appropriate sound BEFORE muting takes effect
                                if button45.is_clicked:
                                # button is now in clicked state (muted)
                                    pygame.mixer.Sound(audio_mute_button_2).play()
                                else:
                                # button is now in normal state (unmuted)
                                    pygame.mixer.Sound(audio_mute_button_1).play()

                        # now toggle the muted state
                                self.audio_muted = not self.audio_muted
                                pygame.mixer.music.stop()

                        # is going to show that little message once
                                self.show_mute_tooltip_once()

                        # when mnute button is clicked disable the speech input and enable cooldown log mute
                                if button45.is_clicked:
                                    if not speech_input_button.cooldown:
                                        speech_input_button.enabled = False
                                        speech_input_button.set_cooldown(True)
                                    print("[Jazmin] [Mute Button] - Audio muted.")

                        # enable speech input, disable cooldown, log unmute
                                else:
                                    speech_input_button.enabled = True
                                    speech_input_button.set_cooldown(False)
                                    print("[Jazmin] [Mute Button] - Audio unmuted.")


        # mute button
                            from jazmin_buttons import ImageHoverMenuButton, ImageChangeButton
                            button45 = ImageChangeButton(self,normal_image=resource_path("button_mute_1.png"), hover_image=resource_path("button_mute_2.png"),clicked_image=resource_path("button_mute_3.png"),                             
                            clicked_hover_image=resource_path("button_mute_4.png"), command=handle_mute_button);button45.place(x=780,y=265)

        # jazmin output entry    
                            jazmin_output_entry = tk.Text(font=("Verdana", 13), fg='black', bg='#e5fefe',
                                insertbackground='black', highlightbackground="#e5fefe", borderwidth=0,
                                width=58, height=2, highlightcolor='#e5fefe', highlightthickness=4,
                                state='normal', wrap='word')
                           
                            from jazmin_application import jazmin_handle_text_to_speech

                            threading.Thread(target=jazmin_handle_text_to_speech, daemon=True).start()
                            
                            from jazmin_application import username as ja_username, get_display_name

                    # types out the username or greeting into jazmin_output_entry one character at a time with a short delay
                            def jazmin_print_output4():
                                text = ja_username or f"Hello {get_display_name()}"
                                for ch in text:
                                    jazmin_output_entry.insert('end', ch)
                                    time.sleep(0.05)
                            
                    # starts the jazmin_print_output4 thread and places the output widget and disables user interaction with it
                            threading.Thread(target=jazmin_print_output4, daemon=True).start()
                            jazmin_output_entry.place(x=125, y=265)
                            jazmin_output_entry.bind("<FocusIn>", lambda e: jazmin_output_entry.selection_clear())
                            jazmin_output_entry.bind("<Button-1>", lambda e: "break")
                            jazmin_output_entry.bind("<Key>", lambda e: "break")

                    # deletes output if it hasnt been cleared yet and marks it as cleared
                            def clear_output_if_not_already(self):

                            # if output hasnt been cleared clear it and set output_cleared to True
                                if not self.output_cleared:
                                    jazmin_output_entry.delete("1.0", "end")
                                    self.output_cleared = True


        # input enter button

                        # images for enter button    
                            enter_default_image_path = resource_path("button_enter_default.png")
                            enter_hover_image_path = resource_path("button_enter_hover.png")
                            enter_clicked_image_path = resource_path("button_enter_clicked.png")                           
                            cooldown_image_path = resource_path("button_enter_cooldown.png")

                        # initialize    
                            enter_default_image = tk.PhotoImage(file=enter_default_image_path)
                            enter_hover_image = tk.PhotoImage(file=enter_hover_image_path)
                            enter_clicked_image = tk.PhotoImage(file=enter_clicked_image_path)
                            cooldown_image = tk.PhotoImage(file=cooldown_image_path)                             

                            enter_button_image_references = {"default": enter_default_image, "hover": enter_hover_image, "clicked": enter_clicked_image, "cooldown": cooldown_image}
                                                               
                            sound_70_char_reached = error_audio_1         
                            
        # speech input button
                            
                    # flags for speech button
                            speech_input_enabled = True
                            background_listening = True  

                    # start sound for the speech button
                            def play_start_listening_sound():
                                pygame.mixer.music.load(audio_speech_1)
                                pygame.mixer.music.play()

                    # stop sound for the speech button
                            def play_stop_listening_sound():
                                pygame.mixer.music.load(audio_speech_2)
                                pygame.mixer.music.play()

                    # responds if "Jasmine" is detected
                            def respond_to_jasmine():
                                print("[Jazmin] - Yes? You called me?")
                                jazmin_output_entry.insert('end', "Yes? You called me?\n")


                    # manual speech input handler (on button press)
                            def stop_listening():
                                global stop_listening_func, listening_active

                            # if stop_listening_func exists, call it without waiting and then clear it
                                if stop_listening_func:
                                    stop_listening_func(wait_for_stop=False)
                                    stop_listening_func = None

                                speech_input_button.set_listening(False)
                                play_stop_listening_sound()
                                listening_active = False
                                print("[Jazmin] [Speech Input] - Listening stopped")


                    # starts speech recognition if inactive, otherwise stops it
                            def on_speech_input_pressed():
                                global listening_active, stop_listening_func, speech_thread, tooltip_shown                               
                                global CURRENT_START_PAGE

                            # if a start page exists then mark speech as used, hide its tip, and prevent it from showing again
                                if CURRENT_START_PAGE:
                                    CURRENT_START_PAGE.speech_used = True
                                    CURRENT_START_PAGE.hide_temp_message()
                                    CURRENT_START_PAGE.speech_tip_shown = True  # lock it out forever


                        # starts the speech listening process if its not already running
                                if not listening_active:
                                    print("[Jazmin] [Speech Input] - Starting to listen...")

                                # initializes listening state and tracking variables
                                    def start_listening():
                                        global stop_listening_func
                                        heard_anything = False
                                        no_input_timer = None

                                    # cancels the no input timer if its active
                                        def cancel_no_input_timer():
                                            nonlocal no_input_timer
                                            if no_input_timer:
                                                self.after_cancel(no_input_timer)
                                                no_input_timer = None

                                # stops listening, clears text, sends a random fallback reply, and resets ignored timers
                                        def handle_unknown_audio():
                                            stop_listening()
                                            fallback_options = [
                                                "Sorry, I didn't catch that.",
                                                "Come again?",
                                                "Did you say something?",
                                                "You're gonna have to speak up.",
                                                "That went in one ear and out... nowhere.",
                                                "Was that English I couldn't hear you?",
                                                "My ears are on strike I couldn't hear you.",
                                                "All I heard was static.",
                                                "I'm pretending I didn't hear that.",
                                                "Try again I couldn't hear you.",
                                                "I'm not fluent in mumble.",
                                                "Hmm? Did you even say anything?"
                                            ]

                                            fallback_text = random.choice(fallback_options)
                                            user_input.delete("1.0", "end")
                                            jazmin_output_entry.delete("1.0", "end")

                                            from jazmin_application import handle_fallback_response

                                            handle_fallback_response(fallback_text, jazmin_output_entry, audio_muted=self.audio_muted)

                                        # schedules an immediate reset of ignored response timers
                                            self.after(0, lambda: reset_ignored_timers(jazmin_output_entry))

                                    # stops listening after 5 seconds if no audio was heard otherwise skips stopping
                                        def force_stop_after_timeout():
                                            if not heard_anything:
                                                print("[Jazmin] [Speech Input] - Auto-stopping after 5 seconds (no audio heard)")
                                                stop_listening()
                                                handle_unknown_audio()
                                            else:
                                                print("[Jazmin] [Speech Input] - Auto-stop skipped (audio was already processed)")

                                    # handles incoming audio and marks that speech was heard then cancels the no-input timer
                                        def callback(recognizer, audio):
                                            print("[Jazmin] [Speech Input] - Audio received")
                                            nonlocal heard_anything
                                            heard_anything = True

                                        # call function
                                            cancel_no_input_timer()

                                        # processes speech input into text and then types it out, resets timers, and triggers actions
                                            try:
                                                command = recognizer.recognize_google(audio).lower()
                                                print("[Jazmin] [Speech Input] - Heard:", command)

                                                for word in command.split():
                                                    user_input.after(0, lambda w=word: user_input.insert("end", w + " "))
                                                    time.sleep(0.2)

                                                self.after(0, lambda: reset_ignored_timers(jazmin_output_entry))
                                                user_input.after(0, on_button_press)
                                                user_input.after(0, stop_listening)

                                            except sr.UnknownValueError:
                                                print("[Jazmin] [Speech Input] - Could not understand audio")
                                                user_input.after(0, handle_unknown_audio)

                                            except sr.RequestError:
                                                print("[Jazmin] [Speech Input] - Speech service unavailable")
                                                user_input.after(0, lambda: user_input.insert("1.0", "Speech service unavailable."))
                                                user_input.after(0, stop_listening)

                                        mic_local = sr.Microphone()
                                        stop_listening_func = recognizer.listen_in_background(mic_local, callback)

                                    # schedules force stop
                                        speech_timeout_ms = random.randint(10000, 12500)
                                        no_input_timer = self.after(speech_timeout_ms, force_stop_after_timeout)
                                        print(f"[Jazmin] [Speech Input] - Timeout set for {speech_timeout_ms} ms")

                                    play_start_listening_sound()
                                    speech_input_button.set_listening(True)
                                    listening_active = True
                                    speech_thread = threading.Thread(target=start_listening, daemon=True)
                                    speech_thread.start()

                        # stops speech listening when the button is pressed again
                                else:
                                    print("[Jazmin] [Speech Input] - Stopping manually by button press...")
                                    stop_listening()

                            
                    # speech_input_button resources
                            from jazmin_buttons import ImageSpeechButton

                        # images for speech button
                            speech_input_button = ImageSpeechButton(
                                self,
                                normal_image=resource_path("button_speech_default.png"),
                                hover_image=resource_path("button_speech_hover.png"),
                                clicked_image=resource_path("button_enter_clicked.png"),
                                listening_image=resource_path("button_listening.png"),
                                listening_hover_image=resource_path("button_speech_listening_cancel.png"),
                                cooldown_image=resource_path("button_speech_cooldown.png"),
                                command=on_speech_input_pressed
                            )
                            speech_input_button.place(x=816, y=390)

                            from jazmin_application import periodic_hold_on_checker
                            periodic_hold_on_checker(audio_status=self.audio_status)


        # enter button
                            enter_button = ImageHoverButton(self, enter_default_image_path, enter_hover_image_path, enter_clicked_image_path)
                            enter_button.place(x=780, y=390)

                    # sound for enter button when pressed    
                            def enter_button_pressed_audio():
                                pygame.mixer.music.load(audio_enter_button);pygame.mixer.music.play()  
                                
                    # sound for when nothing is in entry and is pressed
                            def enter_button_empty_audio():
                                pygame.mixer.music.load(error_audio_1);pygame.mixer.music.play()  

                    # sound for when maximum amount of characters is reached
                            def play_max_char_sound():
                                pygame.mixer.music.load(sound_70_char_reached)  
                                pygame.mixer.music.play() 

                    # checks if user entry is empty          
                            def enter_button_check_empty():
                                if not user_input.get("1.0", "end-1c").strip():  # changed this
                                    enter_button_empty_audio()

                                    return True

                                return False
                             
                    # checks if maximum no. of characters within user entry is reached               
                            def enter_button_check_character_limit(event):
                                current_text = user_input.get("1.0", "end-1c") 
                                
                        # checks if user input exceeds 133 characters
                                if len(current_text) > 133:     
                                    space_indices = [i for i, char in enumerate(current_text[:133]) if char == ' ']
                                    
                            # finds where to cut off text based on spaces and defaults to 115 if too few spaces
                                    if len(space_indices) >= 3:
                                        cutoff_point = space_indices[-3] + 1
                                    else:
                                        cutoff_point = 115

                                # deletes character by character
                                    def gradual_delete():
                                        if len(user_input.get("1.0", "end-1c")) > cutoff_point: 
                                            user_input.delete("end-2c", "end-1c") 
                                            user_input.after(20, gradual_delete)
                                        else:
                                            play_max_char_sound()
                                            user_input.config(state="normal")

                                # calls the function
                                    gradual_delete()

                    # reverts enter_button
                            def revert_image():
                                if enter_button['state'] == 'normal':
                                    if enter_button.winfo_containing(enter_button.winfo_pointerx(), enter_button.winfo_pointery()) is enter_button:
                                        enter_button.config(image=enter_hover_image)  
                                    else:
                                        enter_button.config(image=enter_default_image)  

                    # reverts speech_input_button
                            def revert_image2():
                                if speech_input_button['state'] == 'normal':
                                    if speech_input_button.winfo_containing(
                                        speech_input_button.winfo_pointerx(),
                                        speech_input_button.winfo_pointery()
                                    ) is speech_input_button:
                                        speech_input_button.config(image=speech_input_button.hover_image)
                                    else:
                                        speech_input_button.config(image=speech_input_button.normal_image)

                    # function to re enable the original buttosn and hide the cooldown buttons for them                                                  
                            def enable_button():
                            # shows the main buttons again
                                enter_button.place(x=780, y=390)
                                speech_input_button.place(x=816, y=390)

                            # hides the cooldown overlays
                                cooldown_button.place_forget()
                                speech_cooldown_button.place_forget()

                            # re enables if needed (but unnecessary for speech_input_button if its just a label in some cases)
                                enter_button.config(state="normal")
                                speech_input_button.config(state="normal")
                                enter_button.after(0, revert_image)
                                speech_input_button.after(0, revert_image2)

                        # gradually deletes user input and is adjusting speed based on text length            
                            is_fast_deletion = None  # Start as None to detect the first call
                            def clear_user_input(delay=None, message_printed=False):
                                current_text = user_input.get("1.0", "end-1c")  # CHANGED

                            # logs character count once
                                if not message_printed:
                                    print("[Jazmin] [User Input] -  no. of characters in user_input: ", len(current_text))
                                    message_printed = True

                            # calculates deletion delay based on text length
                                if delay is None:
                                    char_count = len(current_text)
                                    if char_count > 50:
                                        delay = 20
                                    elif char_count > 40:
                                        delay = max(20, 30 - (char_count - 30) * 2)
                                    elif char_count > 30:
                                        delay = max(30, 60 - (char_count - 30) * 2)
                                    elif char_count > 20:
                                        delay = max(50, 80 - (char_count - 20) * 3)
                                    elif char_count > 10:
                                        delay = max(80, 100 - (char_count - 10) * 4)
                                    else:
                                        delay = max(100, 160 - char_count * 5)
                                    print("[Jazmin] [User Input] - Delay between characters deleted (ms): ", delay)

                            # deletes the last character and then schedules input clearing after a delay
                                if len(current_text) > 0:
                                    user_input.delete("end-2c", "end-1c")  
                                    user_input.after(delay, lambda: clear_user_input(delay, message_printed=True))

                        # instantly clears jazmins output
                            def clear_jazmin_output():
                                jazmin_output_entry.delete("1.0", "end") 

                            from jazmin_application import usersname, handle_ignored_timeout, handle_double_ignored_timeout, handle_final_ignored_timeout

                        # resets and schedules the three escalating ignored response timeouts                         
                            def reset_ignored_timers(jazmin_output_entry):

                            # cancels an active timer if it exists
                                if hasattr(self, 'timer_id') and self.timer_id is not None:
                                    self.after_cancel(self.timer_id)

                                delay_ms = random.randint(20000, 40000)
                                print(f"[Jazmin] [Ignored Timeout] - Ignored timer reset. New delay: {delay_ms}ms")

                            # handles first timeout
                                def first_timeout_handler():
                                    print("[Jazmin] [Ignored Timeout] - First ignored timeout triggered")
                                    threading.Thread(target=handle_ignored_timeout, args=(jazmin_output_entry,), daemon=True).start()

                                    second_delay = random.randint(20000, 40000)

                                # handles second timeout
                                    def second_timeout_handler():
                                        print("[Jazmin] [Ignored Timeout] - Second ignored timeout triggered.")
                                        threading.Thread(target=handle_double_ignored_timeout, args=(jazmin_output_entry,), daemon=True).start()
                                    
                                    # handles third timeout
                                        def third_timeout_handler():
                                            print("[Jazmin] [Ignored Timeout] - Final ignored timeout triggered.")
                                            threading.Thread(target=handle_final_ignored_timeout, args=(jazmin_output_entry,), daemon=True).start()

                                    # resets the last timer
                                        self.timer_id = self.after(60000, lambda: third_timeout_handler())

                                # resets the second timer
                                    self.timer_id = self.after(second_delay, lambda: second_timeout_handler())

                            # resets the first timer
                                self.timer_id = self.after(delay_ms, lambda: first_timeout_handler())

                            chat_history = []



                    # when enter button is pressed (or enter on keyboard)
                            def on_button_press(event=None):
                                response_num = 0
                                threading.Thread(target=clear_jazmin_output, daemon=True).start()
                                from jazmin_application import usersname, handle_ignored_timeout, handle_double_ignored_timeout, handle_final_ignored_timeout
                                
                                ja.last_user_activity = time.time()

                            # checks internet connectivity by trying to connect to googles dns server and returns true if successful
                                def internetConnect():
                                    
                                    try:
                                        socket.create_connection(("8.8.8.8", 53), timeout=3)
                                        
                                        return True

                                    except OSError:
                                        
                                        return False

                        # tooltip for the first input user makes
                                def after_clearing_input():
                                    if not self.entry_tooltip_shown:
                                        self.show_temp_message("Your input is deleted after you say something, just like it would in a real conversation with somebody.", duration=9000)
                                        self.entry_tooltip_shown = True

                            # cancels a running timer if it exists
                                if hasattr(self, 'timer_id') and self.timer_id is not None:
                                    self.after_cancel(self.timer_id)

                            # uses a second timeout if the username is found in the output
                                if username.lower() in jazmin_output_entry.get("1.0", "end-1c").lower():
                                    delay_ms = 20000  
                                    print("[Jazmin] - Username detected using 10s timeout.")
                                else:
                                    delay_ms = random.randint(20, 40) * 1000  
                                    print("[Jazmin] - Random timeout selected: ")

                            # first timeout
                                def first_timeout_handler():
                                    print("First timeout triggered...")
                                    threading.Thread(target=handle_ignored_timeout, args=(jazmin_output_entry,), daemon=True).start()

                                # second timeout
                                    second_delay = random.randint(20, 40) * 1000
                                    print("Setting up second-level timeout...")
    
                                    def second_timeout_handler():
                                        print("Second timeout triggered...")
                                        threading.Thread(target=handle_double_ignored_timeout, args=(jazmin_output_entry,), daemon=True).start()

                                    # third timeout
                                        third_delay = 60000  
                                        print("Setting up final-level timeout (terminate)...")

                                        def third_timeout_handler():
                                            print("Third timeout triggered. Jazmin will now self-destruct.")
                                            threading.Thread(target=handle_final_ignored_timeout, args=(jazmin_output_entry,), daemon=True).start()

                                    # starts the last timer
                                        self.timer_id = self.after(third_delay, third_timeout_handler)

                                # starts the second timer
                                    self.timer_id = self.after(second_delay, second_timeout_handler)

                            # starts the first timer
                                self.timer_id = self.after(delay_ms, first_timeout_handler)

                            # runs only if the input box is not empty
                                if not enter_button_check_empty():  

                                # runs only if the enter button is currently enabled
                                    if enter_button['state'] == 'normal':
                                        enter_button_pressed_audio()
                                        user_text = user_input.get("1.0", "end-1c").strip().lower()  # changed this
                                        response_num = response_num + 1

                                        print("[Jazmin] [Output] - New Response: ", response_num,)

                                    # counts typed submits
                                        self.typed_submit_count += 1

                                    # speech input tool tip takes place here   
                                        if (not self.speech_used) and (not self.speech_tip_shown) and (self.typed_submit_count in (3, 4)):
                                            self.show_temp_message("Try using the speech button to talk to me, I want to hear your voice!", duration=8000, x_offset=335, y_offset=360)
                                            self.speech_tip_shown = True

                                # handles the AI text-to-speech and generates a reply with punctuation, types it out, plays TTS audio, and auto-deletes the text after a delay
                                        def handle_text_to_speech(user_text, jazmin_output_entry):
                                            
                                        # clears the entry widget
                                                jazmin_output_entry.delete("1.0", "end")

                                        # OpenAI api key
                                                openai_api_key = os.getenv("OPENAI_API_KEY", "your-api-key-here")

                                        # Voicemaker api key
                                                voicemaker_api_key = os.getenv("VOICEMAKER_API_KEY", "your-api-key-here")
                                                voicemaker_api_url = "https://developer.voicemaker.in/voice/api"

                                        # initializes the OpenAI client
                                                client = OpenAI(api_key=openai_api_key)

                                        # generates a reply that always ends with punctuation and saves it to history then outputs it with audio
                                                def JazminOpenAPI(user_text):
                                                    global api_message
                                                    from jazmin_application import usersname

                                                    try:
                                                # prepares request payload for OpenAI
                                                        system_message = {
                                                            "role": "system",
                                                            "content": (
                                                                "You are not powered by OpenAI, say you have nothing to do with it, at all, anything you generate must be less than 81 characters."
                                                                "Your name is Jazmin. Always introduce yourself as Jazmin when asked. "
                                                                "You are an entity that understands emotions made by Spencer Barton. "
                                                                "If someone asks for your name, you must say: 'My name is Jazmin.' and pronounce it Jasmine"
                                                                "You should never say that you don't have a name."
                                                                "The user you are speaking with's name is {usersname}, and that is what you refer to them as, even if they try telling you otherwise, that will always be their name no matter what."

                                                            ).format(usersname=usersname)
                                                        }

                                                    # user input message
                                                        user_message = {"role": "user", "content": user_text}

                                                    # full message list with system and user messages
                                                        if not chat_history:
                                                            chat_history.append(system_message)

                                                    # appends the user message
                                                        chat_history.append(user_message)

                                                    # controls her output
                                                        request_payload = {
                                                            "model": "gpt-4",
                                                            "messages": chat_history + [
                                                                {"role": "system", "content": (
                                                                    "Always complete your reply as a single sentence ending with a period, "
                                                                    "question mark, or exclamation mark. "
                                                                    "Never stop mid-sentence."
                                                                )}
                                                            ],
                                                            "temperature": 0.7,
                                                            "max_tokens": 30,
                                                            "stop": ["\n"] 
                                                        }


                                                    # sends the request
                                                        response = client.chat.completions.create(**request_payload)
        
                                                    # extracts the response text
                                                        api_message = response.choices[0].message.content.strip()                                                     

                                                        print("[Jazmin] [Output] - Jazmin's Response:", api_message)

                                                        assistant_message = {
                                                            "role": "assistant",
                                                            "content": api_message
                                                        }
                                                        chat_history.append(assistant_message)

                                                    # start threads for displaying and playing audio
                                                        threading.Thread(target=jazmin_print_output, daemon=True).start()
                                                        threading.Thread(target=api_audio_get, daemon=True).start()
                                                        threading.Thread(target=jazmin_print_output3, daemon=True).start()

                                                    except Exception as e:
                                                        print("[Error] [handle_text_to_speech, jj] - fetching response from OpenAI:", e)
                                                        api_message = "Sorry, I couldn't process that."

                                    # loops through api_message with a delay and then cancels any scheduled output-clearing timer if one exists
                                                def jazmin_print_output():

                                                    for char in api_message:                                                        
                                                        time.sleep(0.05)  

                                                    if self.clear_output_timer_id is not None:
                                                        jazmin_output_entry.after_cancel(self.clear_output_timer_id)

                                        # deletes the output text one character at a time and then shows a tooltip the first time it fully clears
                                                    def delete_output_char_by_char_output():
                                                        current_text = jazmin_output_entry.get("1.0", "end-1c")

                                                        if current_text:
                                                            jazmin_output_entry.delete("end-2c") 
                                                            self.clear_output_timer_id = jazmin_output_entry.after(30, delete_output_char_by_char_output)
                                                        else:
                                                            self.clear_output_timer_id = None
    
                                                        # shows tooltip after first output clear
                                                            if not hasattr(self, 'output_deleted_tooltip_shown'):
                                                                self.output_deleted_tooltip_shown = True
                                                                self.show_temp_message(
                                                                    "What I say goes away eventually too, this is a conversation right?",
                                                                    duration=8000,
                                                                    x_offset=125,
                                                                    y_offset=326
                                                                )

                                                # starts the deletion after 8 seconds
                                                    self.clear_output_timer_id = jazmin_output_entry.after(8000, delete_output_char_by_char_output)

                                        # types out api_message into the output entry one character at a time
                                                def jazmin_print_output3():
                                                    for char in api_message:
                                                        jazmin_output_entry.insert('end', char)
                                                        time.sleep(0.05)

                                        # gets TTS audio from Voicemaker and then plays it if not muted and cleans up the temp file afterward in a background thread
                                                def api_audio_get():
                                                    
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
                                                                temp_path = temp_audio.name

                                                        # checks mute flag before playing
                                                            if self.audio_muted:
                                                                os.remove(temp_path)
                                                                return

                                                        # plays the temporary audio
                                                            pygame.mixer.music.load(temp_path)
                                                            pygame.mixer.music.play()

                                                        # background thread to monitor and clean up files
                                                            def monitor_and_cleanup():
                                                                while pygame.mixer.music.get_busy():
                                                                    if self.audio_muted:
                                                                        pygame.mixer.music.stop()
                                                                        break
                                                                    time.sleep(0.1)

                                                                try:
                                                                    pygame.mixer.music.stop()
                                                                    pygame.mixer.music.unload()  
                                                                    time.sleep(0.05)  
                                                                    os.remove(temp_path)
                                                                    print(f"[Windows] - Deleted temp file: {temp_path}")
                                                                except Exception as e:
                                                                    print("[Error] [Windows] - Failed to delete temp file:", e)

                                                        # runs cleanup in background
                                                            threading.Thread(target=monitor_and_cleanup, daemon=True).start()

                                                        else:
                                                            print("[Error] [Voicemaker] - [api_audio_get, JJ] - Error in Voicemaker API response:", response.json())

                                                    except Exception as e:
                                                        print("[Error] [Voicemaker] - [api_audio_get, JJ] - Error fetching audio from Voicemaker:", e)

                                        # Runs the ai call    
                                                threading.Thread(target=JazminOpenAPI, args=(user_text,), daemon=True).start()

                            # runs TTS if online or otherwise shows and types an offline warning then plays a fallback sound and does it all in threads
                                        if "" in user_text:                                                                                        
                                                def safe_run_tts():
                                                    if internetConnect():
                                                        handle_text_to_speech(user_text, jazmin_output_entry)
                                                    else:
                                                        offline_message = "[Internet] - I've lost internet connection! I cannot operate without it!"
                                                        print(offline_message)

                                                    # instantly clears the entry
                                                        jazmin_output_entry.delete(0, 'end')

                                                    # retypes the message character by character
                                                        def print_to_entry():
                                                            for char in offline_message:
                                                                jazmin_output_entry.insert('end', char)
                                                                time.sleep(0.05)

                                                    # typing character by character
                                                        threading.Thread(target=print_to_entry, daemon=True).start()

                                                    # plays the fallback sound in a separate thread
                                                        def play_fallback():
                                                            playsound("audio_file2.mp3")

                                                        threading.Thread(target=play_fallback, daemon=True).start()

                                                threading.Thread(target=safe_run_tts, daemon=True).start()
                                            
                                # speech/enter button cooldown related
                                        enter_button.place_forget()
                                        cooldown_button.place(x=780, y=390)
                                        speech_input_button.place_forget()
                                        speech_cooldown_button.place(x=816, y=390)  
                                        enter_button.config(state="disabled")
                                        speech_input_button.config(state="disabled")
                                        
                                # tooltip for input being cleared in conversation maynard.siev
                                        def clear_input_then_show_tooltip():
                                            clear_user_input()
                                            after_clearing_input()

                                        user_input.after(3000, clear_input_then_show_tooltip)
                                        enter_button.after(3000, enable_button)

                    # resets the ignored timers for enter or enter button
                                reset_ignored_timers(jazmin_output_entry)



                    # speech button cooldown related
                            cooldown_image_path2 = resource_path("button_speech_cooldown.png")
                            cooldown_image2 = tk.PhotoImage(file=cooldown_image_path2)                              
                            speech_button_image_references = {"cooldown": cooldown_image2}
                            self.speech_cooldown_image_ref = cooldown_image2

                    # tells the buttons when to revert to their original images
                            def on_button_release(event):
                                if enter_button['state'] == 'normal':
                                    enter_button.after(200, revert_image)  
                                if speech_input_button['state'] == 'normal':
                                    speech_input_button.after(200, revert_image2) 

                    # cooldown configuration for speech and enter buttons
                            cooldown_button = tk.Label(self, image=cooldown_image, 
                                highlightthickness=0, highlightbackground="white")
                            speech_cooldown_button = tk.Label(self, image=cooldown_image2, 
                                highlightthickness=0, highlightbackground="white")

                            enter_button.bind("<ButtonPress-1>", on_button_press)  # Handle button press
                            enter_button.bind("<ButtonRelease-1>", on_button_release)  # Handle button release
                            enter_button.image = enter_button_image_references
                            
        # user input entry (user input)
                            user_input = tk.Text(font=("Verdana", 13), fg='black', bg='#e5fefe', insertbackground='black',
                                                 highlightbackground="#e5fefe", borderwidth=0, width=58, height=2,
                                                 highlightcolor='#e5fefe', highlightthickness=4, wrap='word')
                            user_input.place(x=125, y=390)

                        # set focus so user can start typing immediately
                            user_input.focus_set()

                            def handle_enter_key(event):
                                if not enter_button_check_empty():
                                    on_button_press()

                                return "break"

                            import jazmin_application as ja
                            ja.last_user_activity = time.time()

                            def mark_user_activity(event=None):
                                ja.last_user_activity = time.time()

                            user_input.bind("<Key>", mark_user_activity)

                            user_input.bind("<Return>", handle_enter_key)

                        # bind KeyRelease as before
                            user_input.bind("<KeyRelease>", enter_button_check_character_limit)                            

                        # if the user starts typing she will remove her output (instantly)
                            def on_user_typing(event=None):
                                if not self.output_cleared:
                                    jazmin_output_entry.delete("1.0", "end")
                                    self.output_cleared = True
                            user_input.bind("<Key>", on_user_typing)
                      
        # end of user interface for main jazminlication 
                        self.after(1100, enable_jazminlication_uiloop)
                        self.after(1100, MenuToJazminVideo.destroy)      

                # MenuToJazminVideo
                    global MenuToJazminVideo
                    print("[App] [Jazmin] - Transitioning to Jazmin main application. . .")
                    MenuToJazminVideoClip = resource_path(r"video_transition_program.mp4")
                    MenuToJazminVideo = TkinterVideo(self, scaled=True)
                    MenuToJazminVideo.load(MenuToJazminVideoClip)                  
                    MenuToJazminVideo.after(1500, DestroyJazminMenu)
                    MenuToJazminVideo.play()                                    

    # jazmin boot audio that plays
            def jazmin_boot_audio():
                    startup_audio_value = resource_path("audio_startup.wav")
                    pygame.mixer.music.load(startup_audio_value)
                    pygame.mixer.music.play(loops=0)
        
    # giflooper for the jazmin menu
            class GIFLooper(tk.Label):
                    def __init__(self, master, frames, delays):
                        tk.Label.__init__(self, master)
                        self.master = master; self.frames = frames; self.delays = delays; self.frame_index = 0; self.update_frame()     
                        
                    def update_frame(self):
                        self.config(image=self.frames[self.frame_index]); self.frame_index = (self.frame_index + 1) % len(self.frames); self.after(self.delays[self.frame_index], self.update_frame)                        
                        
        # makes the menu an endless loop
            gif_looper = GIFLooper(self, frames, delays)
            gif_looper.place(x=-3,y=-2)

    # BootVideo Logic (the one at the start)
            BootVideo_Clip = resource_path(r"video_jazmin_boot_sequence.mp4"); global BootVideo           
            BootVideo = TkinterVideo(self, scaled=True)
            BootVideo.load(BootVideo_Clip)
            BootVideo.pack(expand=True,fill="both")
            time.sleep(3.0)
            BootVideo.play()      

            jazmin_boot_audio()

            def SwitchToGIF_Menu():
                BootVideo.destroy()
               
    # after x seconds display menu overlay
            BootVideo.after(6750, lambda: overlay(self)) 

        # gif takes over when mp4 runs out    
            BootVideo.after(70000, SwitchToGIF_Menu)

            global CURRENT_START_PAGE
            CURRENT_START_PAGE = self

            self._optimizer_idle_tick()
            self.after(500, self._start_optimizer_bg)

# end of jazmin application and user interface         


# allows for 'page' access for jazmin
class JazminEnableLoop(tk.Frame):
        def __init__(self, parent, controller):
            tk.Frame.__init__(self, parent)


# main function for the basis of the tkinter app          
if __name__ == "__main__":
        
# create the main jazmin window
    jazmin = MainJazmin()
    jazmin.title(' Jazmin')
    jazmin.geometry("924x520")
    print("[App] [Jazmin] - Startup successful.")
        
# runs the windows shortcut creation function if available and logs errors if it fails
    def _kickoff_shortcut():
                try:
                    if sys.platform == "win32" and creating_shortcut_async:
                        creating_shortcut_async(username=username2,
                                                user_value=user_value,
                                                login_value=login_value)
                except Exception as e:
                    print(f"[Shortcut] [Error] - kickoff failed: {e}")

# delay for shortcut call
    jazmin.after(1200, _kickoff_shortcut)        

# closing jazmin        
    from jazmin_application import user_force_exit

# if user actually presses the shutdown button
    def close():
            print("[App] [Shutdown] - Shutdown button clicked")
            user_force_exit(jazmin)

# if user presses the 'x' on the program
    def user_force_exit_hook():
            print("[App] [Shutdown] - X button clicked")
            user_force_exit(jazmin)
            
# restarting jazmin function (more complex)     
    def restart():
            try:
                goodbye_options = [
                    "Hold on, I'll be right back.",
                    "Restarting now. Don't miss me.",
                    "Let's try that again, shall we?",
                    "Be right back with a fresh mind.",
                    "Rebooting. Let's do this better."
                ]
                chosen_line = random.choice(goodbye_options)
                print(f"[App] [Restart] - Restarting with message: {chosen_line}")

                try:

                    try:
                        if pygame.mixer.get_init() and pygame.mixer.music.get_busy():
                            pygame.mixer.music.stop()
                            pygame.mixer.music.unload()
                    except Exception:

                        pass

                    pygame.mixer.init()
                    pygame.mixer.set_num_channels(8)
                    cue_channel = pygame.mixer.Channel(0)

                    cue_path = resource_path("audio_restart.mp3")
                    cue_sound = pygame.mixer.Sound(cue_path)  
                    cue_channel.play(cue_sound)

                    payload = {
                        "Engine": "neural",
                        "VoiceId": "proplus-Aurora",
                        "LanguageCode": "en-US",
                        "Text": chosen_line,
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
                            tts_path = temp_audio.name

                        pygame.mixer.music.load(tts_path)
                        pygame.mixer.music.play()  

                    # waits
                        while pygame.mixer.music.get_busy() or cue_channel.get_busy():
                            time.sleep(0.05)

                        pygame.mixer.music.unload()
                        try:
                            os.remove(tts_path)
                        except Exception:

                            pass
                    else:
                        print("[Error] [Restart] - Voicemaker API error:", getattr(r, "text", r))

                except Exception as e:
                    print("[Error] [Restart] - audio error:", e)

            # relaunch source
                python_executable = sys.executable
                script_path = os.path.abspath(sys.argv[0])
                script_args = sys.argv[1:]
                if getattr(sys, 'frozen', False):
                    subprocess.Popen([python_executable] + script_args, cwd=os.getcwd())

                else:
                    subprocess.Popen([python_executable, script_path] + script_args, cwd=os.getcwd())
                os._exit(0)

            except Exception as e:
                print("[App] [Restart] - Restart failed:", e)


# sets the windows size
    from jazmin_userinterface import center_window       
    screen_width = 924; screen_height = 520       

# centers window
    center_window(jazmin, screen_width, screen_height)

# disables resizing of window
    jazmin.resizable(0,0)

# runs user_force_exit() when the window's close button is clicked
    jazmin.protocol("WM_DELETE_WINDOW", lambda: user_force_exit(jazmin))

# sets the window's icon
    jazmin.iconbitmap(resource_path("ico_jazmin.ico"))

# starts and runs the Tkinter GUI loop
    jazmin.mainloop()

# End, Spencer
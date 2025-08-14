# Jazmin  - Your Digital Personality
# File    : jazmin_buttons.py
# Author  : Spencer Barton (spencer@jazminpy.com)
# GitHub  : https://github.com/spencebarton/jazmin
# License : MIT License
# Descript: Buttons used throughout Jazmin's program are affected by the classes in this file
# Last date edited: (08/02/25 09:31)

# Copyright (c) 2025 Spencer Barton 
# Managed through Jazmin and SBD. All rights reserved. 
# For more information, visit jazminpy.com

# Libraries used
import tkinter as tk
from PIL import Image, ImageTk
from tkinter import Menu
import sys
import os

# Class: ImageSpeechButton 
    # a label-based button that switches between normal, hover, clicked, listening, and cooldown statesused for voice input control
    # buttons that use ImageSpeechButton: speech_input_button

class ImageSpeechButton(tk.Label):
    def __init__(self, master, normal_image, hover_image, clicked_image, listening_image, listening_hover_image, cooldown_image, command=None, **kwargs):
        super().__init__(master, **kwargs)
        self.enabled = True

        self.normal_image = ImageTk.PhotoImage(Image.open(normal_image))
        self.hover_image = ImageTk.PhotoImage(Image.open(hover_image))
        self.clicked_image = ImageTk.PhotoImage(Image.open(clicked_image))
        self.listening_image = ImageTk.PhotoImage(Image.open(listening_image))
        self.listening_hover_image = ImageTk.PhotoImage(Image.open(listening_hover_image))
        self.cooldown_image = ImageTk.PhotoImage(Image.open(cooldown_image))

        self.config(image=self.normal_image)
        self.command = command

        self.listening = False
        self.cooldown = False

        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.bind("<Button-1>", self.on_click)
        self.bind("<ButtonRelease-1>", self.on_release)

    def _is_hovered(self):
        return self.winfo_containing(self.winfo_pointerx(), self.winfo_pointery()) is self

    def set_listening(self, active):
        self.listening = active
        self.cooldown = False
        self._update_image()

    def set_cooldown(self, active):
        self.cooldown = active
        self.listening = False
        self._update_image()

    def _update_image(self):
        if self.cooldown:
            self.config(image=self.cooldown_image)
        elif self.listening:
            if self._is_hovered():
                self.config(image=self.listening_hover_image)
            else:
                self.config(image=self.listening_image)
        elif self._is_hovered():
            self.config(image=self.hover_image)
        else:
            self.config(image=self.normal_image)

    def on_enter(self, event):
        if self.cooldown:
            return
        if self.listening:
            self.config(image=self.listening_hover_image)
        else:
            self.config(image=self.hover_image)

    def on_leave(self, event):
        if self.cooldown:
            return
        if self.listening:
            self.config(image=self.listening_image)
        else:
            self.config(image=self.normal_image)

    def on_click(self, event):
        if not self.enabled:
            return
        if not self.cooldown and not self.listening:
            self.config(image=self.clicked_image)
        if self.command and not self.cooldown:
            self.command()

    def on_release(self, event):
        if not self.enabled:
            return
        if self.cooldown:
            return
        if self.listening:
            self.config(image=self.listening_hover_image if self._is_hovered() else self.listening_image)
        else:
            self.config(image=self.hover_image if self._is_hovered() else self.normal_image)

# Class: ImageHoverButtonWithState
    # a label button that changes images on hover and click, and locks into the sucess image once triggered
    # buttons that use ImageHoverButtonWithState: proceed_button

class ImageHoverButtonWithState(tk.Label):
    def __init__(self, master, normal_image, hover_image, clicked_image, success_image, command=None, **kwargs):
        super().__init__(master, **kwargs)
        
        self.normal_image = ImageTk.PhotoImage(Image.open(normal_image))
        self.hover_image = ImageTk.PhotoImage(Image.open(hover_image))
        self.clicked_image = ImageTk.PhotoImage(Image.open(clicked_image))
        self.success_image = ImageTk.PhotoImage(Image.open(success_image))
        self.config(image=self.normal_image)
        self.command = command

        self.success_mode = False  

        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.bind("<Button-1>", self.on_click)
        self.bind("<ButtonRelease-1>", self.on_release)

    def on_enter(self, event):
        if not self.success_mode:
            self.config(image=self.hover_image)

    def on_leave(self, event):
        if not self.success_mode:
            self.config(image=self.normal_image)

    def on_click(self, event):
        if not self.success_mode:
            self.config(image=self.clicked_image)
        if self.command:
            self.command()

    def on_release(self, event):
        if not self.success_mode:
            if event.widget == self:
                self.config(image=self.hover_image)
            else:
                self.config(image=self.normal_image)

    def set_success_state(self):
        self.config(image=self.success_image)
        self.success_mode = True 

# Class: ImageHoverButton 
    # a simple label button that visually changes when hovered or clicked-ideal for standard UI actions
    # buttons that use ImageHoverButton: helpbutton, enter_button

class ImageHoverButton(tk.Label):
    def __init__(self, master, normal_image, hover_image, clicked_image, command=None, **kwargs):
        super().__init__(master, **kwargs)
        
        self.normal_image = ImageTk.PhotoImage(Image.open(normal_image))
        self.hover_image = ImageTk.PhotoImage(Image.open(hover_image))
        self.clicked_image = ImageTk.PhotoImage(Image.open(clicked_image))
        self.config(image=self.normal_image)
        self.command = command

        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.bind("<Button-1>", self.on_click)
        self.bind("<ButtonRelease-1>", self.on_release)

    def on_enter(self, event):
        self.config(image=self.hover_image)

    def on_leave(self, event):
        self.config(image=self.normal_image)

    def on_click(self, event):
        self.config(image=self.clicked_image)
        if self.command:
            self.command()

    def on_release(self, event):
        if event.widget == self: 
            self.config(image=self.hover_image)
        else:
            self.config(image=self.normal_image)

# Class: ImageHoverMenuButton 
    # a menu button that shows a custom dropdown menu with image-based items on click, and handles hover effects
    # buttons that use ImageHoverMenuButton: menubutton

class ImageHoverMenuButton(tk.Menubutton):
    def __init__(self, master, normal_image, hover_image, menu_items, menu_bg="#0042A2", menu_hover_bg="#4588D9", menu_font=("Arial", 10), x_offset=0, y_offset_up=0, border_thickness=2, **kwargs):
        super().__init__(master, **kwargs)

        self.normal_image = ImageTk.PhotoImage(Image.open(normal_image))
        self.hover_image = ImageTk.PhotoImage(Image.open(hover_image))
        self.config(image=self.normal_image)

        self.menu_items = menu_items
        self.menu_bg = menu_bg
        self.menu_hover_bg = menu_hover_bg
        self.menu_font = menu_font
        self.border_thickness = border_thickness

        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.bind("<Button-1>", self.show_menu)

        self.x_offset = x_offset
        self.y_offset_up = y_offset_up

        self.menu_window = None

    def on_enter(self, event):
        self.config(image=self.hover_image)

    def on_leave(self, event):
        self.config(image=self.normal_image)

    def show_menu(self, event):
        if self.menu_window:
            self.menu_window.destroy()

        self.menu_window = tk.Toplevel(self)
        self.menu_window.wm_overrideredirect(True)
        self.menu_window.configure(bg="white")  

        x_offset = self.winfo_rootx() + self.x_offset
        y_offset = self.winfo_rooty() + self.winfo_height() + self.y_offset_up
        self.menu_window.geometry(f"+{x_offset}+{y_offset}")

        inner_frame = tk.Frame(self.menu_window, bg=self.menu_bg, bd=0)
        inner_frame.pack(padx=self.border_thickness, pady=self.border_thickness)

        self.menu_window.bind("<FocusOut>", lambda e: self._close_menu_on_click_outside())

        for index, (label, item_normal_image, item_hover_image, command) in enumerate(self.menu_items):
            normal_img = ImageTk.PhotoImage(Image.open(item_normal_image))
            hover_img = ImageTk.PhotoImage(Image.open(item_hover_image))

            menu_button = tk.Button(
                inner_frame,
                image=normal_img,
                command=lambda cmd=command: self._menu_command(cmd),
                bg=self.menu_bg,
                relief=tk.FLAT,        
                bd=0,                   
                font=self.menu_font,
                compound=tk.LEFT
            )
            menu_button.image_normal = normal_img  
            menu_button.image_hover = hover_img
            menu_button.bind("<Enter>", lambda e, btn=menu_button, img=hover_img: self._on_button_hover(btn, img))
            menu_button.bind("<Leave>", lambda e, btn=menu_button, img=normal_img: self._on_button_leave(btn, img))

            menu_button.pack(fill=tk.X)

        self.menu_window.focus_set()

    def _menu_command(self, command):
        if self.menu_window:
            self.menu_window.destroy()
        command()

    def _on_button_hover(self, button, hover_img):
        button.config(image=hover_img, bg=self.menu_hover_bg)

    def _on_button_leave(self, button, normal_img):
        button.config(image=normal_img, bg=self.menu_bg)

    def _close_menu_on_click_outside(self):
        if self.menu_window:
            self.menu_window.destroy()

# Class: ImageChangeButton 
    # a toggle-style label button that switches between normal and clicked states, each with their own hover behaviorused for things like mute toggles
    # buttons that use ImageChangeButton: button45 (mute button)

class ImageChangeButton(tk.Label):
    def __init__(self, master, normal_image, hover_image, clicked_image, clicked_hover_image, command=None, **kwargs):
        super().__init__(master, **kwargs)

        self.normal_image = ImageTk.PhotoImage(Image.open(normal_image))
        self.hover_image = ImageTk.PhotoImage(Image.open(hover_image))
        self.clicked_image = ImageTk.PhotoImage(Image.open(clicked_image))
        self.clicked_hover_image = ImageTk.PhotoImage(Image.open(clicked_hover_image))

        self.config(image=self.normal_image)
        self.command = command

        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.bind("<Button-1>", self.on_click)
        self.is_clicked = False

    def on_enter(self, event):
        if self.is_clicked: 
            self.config(image=self.clicked_hover_image)         
        else: 
            self.config(image=self.hover_image)            

    def on_leave(self, event): 
        if self.is_clicked: 
            self.config(image=self.clicked_image)            
        else: 
            self.config(image=self.normal_image)            

    def on_click(self, event):
        if self.is_clicked: 
            self.config(image=self.normal_image)             
        else: 
            self.config(image=self.clicked_image)            
        self.is_clicked = not self.is_clicked   
        if self.command:
            self.command()

# End, Spencer
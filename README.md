# Jazmin — A Digital Personality Assistant

Jazmin is a Windows desktop **emotional assistant** I built in Python with a custom GUI, real-time TTS, and strict audio-playback control (no overlapping lines).  
**Download the app:** https://jazminpy.com  
This repo showcases the source.

![Jazmin UI](docs/screenshots/main_ui.png)

## Features
- Custom Tkinter GUI with image-based controls
- OpenAI-powered dialogue (configurable)
- Voicemaker TTS with **exclusive** playback (queued / overlap-free)
- Idle timeouts, personality lines, and login prompts
- Clean shutdown logic with sound effects

## Tech Stack
Python, Tkinter, Pillow, pygame, playsound, requests, BeautifulSoup4, lxml,  
TextBlob, OpenAI SDK, keyboard, colorama, winshell / pywin32, tkVideoPlayer

---

## Project Structure
├─ src/ # source code
│ ├─ JJ.py # entry point
│ ├─ jazmin_application.py
│ ├─ jazmin_userinterface.py
│ ├─ jazmin_buttons.py
│ ├─ jazmin_optimizer.py
│ └─ jazmin_shortcut.py
├─ assets/ # runtime assets (images/sounds/fonts)
├─ docs/
│ └─ screenshots/ # images used in this README
├─ .env.example # placeholder env vars (no real keys)
├─ LICENSE (MIT)
└─ README.md

## Run Locally (optional)
> The packaged installer is on the website. If you’d like to run from source:

```bash
# 1) Create & activate a venv (Windows)
python -m venv .venv
.venv\Scripts\activate

# 2) Install deps
pip install -r requirements.txt

# 3) Configure environment variables
copy .env.example .env   # then add your own keys

# 4) Launch
python src/JJ.py

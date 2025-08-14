# Jazmin — A Digital Personality Assistant

Jazmin is a Windows desktop emotional assistant I built in Python with a custom GUI, real-time TTS,
and strict audio-playback control (no overlapping lines). You can download the app from
**https://jazminpy.com** — this repo showcases the source.

![Jazmin UI](docs/screenshots/main_ui.png)

## Features
- Custom Tkinter GUI with image-based controls
- OpenAI-powered dialogue (configurable)
- Voicemaker TTS with exclusive playback (queued/overlap-free)
- Idle timeouts, personality lines, and login prompts
- Clean shutdown logic with sound effects

## Tech Stack
Python, Tkinter, Pillow, pygame, playsound, requests, BeautifulSoup4, lxml,
TextBlob, OpenAI SDK, keyboard, colorama, winshell/pywin32, tkVideoPlayer.

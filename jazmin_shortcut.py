# Jazmin  - Your Digital Personality
# File    : jazmin_shortcut.py
# Author  : Spencer Barton (spencer@jazminpy.com)
# GitHub  : https://github.com/spencebarton/jazmin
# License : MIT License
# Descript: Creates a desktop shortcut for Jazmin with robust path + error handling
# Last date edited: (08/10/25 16:01)

# Copyright (c) 2025 Spencer Barton 
# Managed through Jazmin and SBD. All rights reserved. 
# For more information, visit jazminpy.com

# Standard Libraries used
import os
import sys
import threading
from pathlib import Path

# tries to import dispatch from win32com.client and saves the error if it fails
try:
    from win32com.client import Dispatch
except Exception as e:
    Dispatch = None
    _import_err = e

# tries to import winshell and saves the error if it fails
try:
    import winshell
except Exception as e:
    winshell = None
    _winshell_err = e

# Function: _log()
    # prints a formatted shortcut log message with a subcategory and text
def _log(subcat: str, msg: str) -> None:
    print(f"[Shortcut] [{subcat}] - {msg}")

# Function: _candidate_targets()
    # builds and returns a list of possible Jazmin.exe file paths in priority order, removing duplicates
def _candidate_targets(username: str | None) -> list[Path]:
    cands: list[Path] = []

    if getattr(sys, "frozen", False):
        cands.append(Path(sys.executable))

    here = Path(__file__).resolve()
    cands.append(here.parent / "dist" / "Jazmin" / "Jazmin.exe")

    cands.append(here.parent.parent / "dist" / "Jazmin" / "Jazmin.exe")

    if username:
        cands.append(Path(rf"C:\Users\{username}\Desktop\JJ - Copy\JJ\dist\Jazmin\Jazmin.exe"))
        cands.append(Path(rf"C:\Users\{username}\OneDrive\Desktop\JJ - Copy\JJ\dist\Jazmin\Jazmin.exe"))

    seen = set()
    out = []
    for p in cands:
        if p not in seen:
            out.append(p)
            seen.add(p)

    return out

# Function: _pick_target()
    # returns the first existing file path from _candidate_targets or None if none exist
def _pick_target(username: str | None) -> Path | None:
    for p in _candidate_targets(username):
        if p.exists():
            return p

    return None

# Function: _guess_icon_for()
    # finds the most likely icon file for Jazmin.exe
def _guess_icon_for(target: Path) -> Path | None:
    cand1 = target.with_suffix(".ico")  # Jazmin.ico beside Jazmin.exe
    if cand1.exists():

        return cand1

    cand2 = target.parent.parent / "ico_jazmin.ico"
    if cand2.exists():

        return cand2

    return None

# Function: creating_shortcut()
    # creates a desktop shortcut for Jazmin if it doesn't already exist
def creating_shortcut(username: str | None, user_value: str | None, login_value: str | None) -> bool:
    _log("Init", "Starting shortcut creation process")

    if user_value is not None and login_value is not None and user_value != login_value:
        _log("Auth", "User identity different")
        _log("Error", "Shortcut generation aborted. Error 9x001")

        return False

    if winshell is None:
        _log("Error", f"winshell not available: {_winshell_err}")

        return False

    if Dispatch is None:
        _log("Error", f"win32com not available: {_import_err}")

        return False

# will resolve desktop to handle OneDrive redirection automatically
    try:
        desktop = Path(winshell.desktop())
    except Exception as e:
        _log("Error", f"Failed to resolve Desktop path: {e}")

        return False

    lnk_path = desktop / "Jazmin.lnk"
    _log("Check", f"Shortcut path: {lnk_path}")

    if lnk_path.exists():
        _log("Exists", "Shortcut already exists")

        return True

# find target .exe file
    target = _pick_target(username)
    if not target:
        _log("Error", "Could not locate Jazmin.exe in any known path")

        return False

    _log("Path", f"Using target: {target}")
    workdir = target.parent
    _log("Path", f"Working dir: {workdir}")

# ensures icon is optional
    icon_path = _guess_icon_for(target)
    if icon_path:
        _log("Check", f"Icon found: {icon_path}")
    else:
        _log("Warn", "Icon not found; shortcut will use default")

# create the shortcut on desktop
    try:
        shell = Dispatch("WScript.Shell")
        sc = shell.CreateShortCut(str(lnk_path))
        sc.Targetpath = str(target)
        sc.WorkingDirectory = str(workdir)
        if icon_path:
            sc.IconLocation = f"{icon_path},0"
        sc.save()

        _log("Success", "Shortcut created successfully")

        return True

    except Exception as e:
        _log("Error", f"Failed to create shortcut: {e}")

        return False

# Function: creating_shortcut_async()
    # runs the shortcut creation in a background thread to avoid blocking main ui
def creating_shortcut_async(username: str | None, user_value: str | None, login_value: str | None) -> None:
    
    t = threading.Thread(target=creating_shortcut, args=(username, user_value, login_value), daemon=True)
    t.start()

# End, Spencer
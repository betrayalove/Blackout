"""
Build script for Blackout executable using PyInstaller
"""

import os
import sys
import shutil
import subprocess

APP_NAME = "Blackout"
ICON = "icon.ico"
MAIN_SCRIPT = "main.py"
DIST_DIR = "dist"


def clean():
    """Clean previous build artifacts"""
    for folder in ["build", "dist"]:
        if os.path.exists(folder):
            shutil.rmtree(folder)
    for file in os.listdir():
        if file.endswith(".spec"):
            os.remove(file)


def build():
    """Build the executable using PyInstaller"""
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--windowed",
        f"--icon={ICON}",
        f"--name={APP_NAME}",
        f"--add-data={ICON};.",
        MAIN_SCRIPT
    ]
    print("Running:", " ".join(cmd))
    subprocess.check_call(cmd)


def create_autostart_script():
    """Creates a script to add Blackout to Windows autostart (in dist/)"""
    script_content = '''@echo off
REM Add Blackout to Windows autostart

echo Adding Blackout to autostart...
set "EXE_PATH=%~dp0Blackout.exe"
reg add "HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Run" /v "Blackout" /t REG_SZ /d "%EXE_PATH%" /f
if %ERRORLEVEL% EQU 0 (
    echo Blackout added to autostart!
) else (
    echo Error adding to autostart. Try running as administrator.
)
pause
'''
    os.makedirs("dist", exist_ok=True)
    with open(os.path.join("dist", "add_to_autostart.bat"), "w", encoding="cp866") as f:
        f.write(script_content)
    print("Created dist/add_to_autostart.bat")


def create_remove_autostart_script():
    """Creates a script to remove Blackout from Windows autostart (in dist/)"""
    script_content = '''@echo off
REM Remove Blackout from Windows autostart

echo Removing Blackout from autostart...
reg delete "HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Run" /v "Blackout" /f
if %ERRORLEVEL% EQU 0 (
    echo Blackout removed from autostart!
) else (
    echo Error removing from autostart. Maybe it was not added.
)
pause
'''
    os.makedirs("dist", exist_ok=True)
    with open(os.path.join("dist", "remove_from_autostart.bat"), "w", encoding="cp866") as f:
        f.write(script_content)
    print("Created dist/remove_from_autostart.bat")


def main():
    print("=== Blackout Build ===")
    print("Cleaning previous builds...")
    clean()
    print("Building executable...")
    build()
    print(f"Build finished. The EXE is in the '{DIST_DIR}' folder as '{APP_NAME}.exe'.")
    
    # Create autostart scripts
    create_autostart_script()
    create_remove_autostart_script()
    
    print("\n=== Instructions ===")
    print("1. Executable: dist/Blackout.exe")
    print("2. To add to autostart: run add_to_autostart.bat as administrator")
    print("3. To remove from autostart: run remove_from_autostart.bat as administrator")
    print("4. To run manually: double-click Blackout.exe")
    print("5. Settings are saved in Windows registry (HKEY_CURRENT_USER\\Software\\Blackout)")


if __name__ == "__main__":
    main() 
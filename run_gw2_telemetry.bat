@echo off
REM GW2 UDP Telemetry Launcher for Windows
REM This script creates a virtual environment and runs the telemetry client

set SCRIPT_DIR=%~dp0
set VENV_DIR=%SCRIPT_DIR%venv

REM Check if Python is available
where python >nul 2>&1
if errorlevel 1 (
    echo Error: Python not found in PATH
    echo Please install Python 3.x and add it to your PATH
    pause
    exit /b 1
)

REM Create virtual environment if it doesn't exist
if not exist "%VENV_DIR%" (
    echo Creating virtual environment...
    python -m venv "%VENV_DIR%"
    if errorlevel 1 (
        echo Error: Failed to create virtual environment
        pause
        exit /b 1
    )
) else (
    echo Virtual environment already exists.
)

REM Activate virtual environment
echo Activating virtual environment...
call "%VENV_DIR%\Scripts\activate.bat"
if errorlevel 1 (
    echo Error: Failed to activate virtual environment
    pause
    exit /b 1
)

REM Install/upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

REM Run the telemetry script (no additional packages needed - uses built-in socket)
echo Starting GW2 UDP Telemetry Client...
echo.
python "%SCRIPT_DIR%gw2_udp_telemetry.py"
set ERROR_CODE=%errorlevel%

REM Deactivate virtual environment
call deactivate

echo.
echo Telemetry client has exited with code %ERROR_CODE%
pause
exit /b %ERROR_CODE%

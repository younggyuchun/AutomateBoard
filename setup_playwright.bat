@echo off
chcp 65001 >nul
echo ================================================
echo Hansomang Automation Tool - Playwright Setup
echo ================================================
echo.
echo Installing Playwright browser...
echo This only needs to be run once.
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed or not found in PATH.
    echo.
    echo Please install Python first:
    echo 1. Visit: https://www.python.org/downloads/
    echo 2. Download and install Python 3.13 or later
    echo 3. Make sure to check "Add Python to PATH" during installation
    echo.
    echo Alternative: Open Microsoft Store and search for "Python"
    echo.
    pause
    exit /b 1
)

echo Python found. Checking Playwright package...
echo.

REM Check if Playwright package is installed
python -c "import playwright" >nul 2>&1
if %errorlevel% neq 0 (
    echo Playwright package not found. Installing...
    echo This may take a few minutes...
    echo.
    python -m pip install playwright
    if %errorlevel% neq 0 (
        echo.
        echo ================================================
        echo Failed to install Playwright package.
        echo Please check your internet connection and try again.
        echo ================================================
        echo.
        pause
        exit /b 1
    )
    echo.
    echo Playwright package installed successfully!
    echo.
)

echo Installing Playwright browser (Chromium)...
echo This may take a few minutes...
echo.

REM Install playwright browser using Python module
python -m playwright install chromium

if %errorlevel% equ 0 (
    echo.
    echo ================================================
    echo Installation completed successfully!
    echo You can now run HansomangAutomation.exe
    echo ================================================
) else (
    echo.
    echo ================================================
    echo An error occurred.
    echo Please check your internet connection and try again.
    echo ================================================
)

echo.
pause


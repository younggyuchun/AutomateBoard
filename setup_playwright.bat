@echo off
chcp 65001 >nul
echo ================================================
echo Hansomang Automation Tool - Playwright Setup
echo ================================================
echo.
echo Installing Playwright browser...
echo This only needs to be run once.
echo.

REM Install playwright using Python module
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


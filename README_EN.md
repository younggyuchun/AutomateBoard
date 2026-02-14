# Hansomang Automation Tool

This program is a GUI application that automates the registration of Sunday sermons and popup/notice modifications on the hansomang.ca website.

## Installation

### Running with Python
1. Install required packages:
```bash
pip install playwright customtkinter
playwright install chromium
```

### Using Windows EXE File (Recommended)
1. Download `HansomangAutomation.exe`
2. First time only: Run `setup_playwright.bat` (one time setup)
3. Run `HansomangAutomation.exe`

For detailed instructions, see `USER_MANUAL_EN.txt`.

## How to Run

### Run with Python
```bash
python gui_app.py
```

### Run Windows EXE
Double-click `HansomangAutomation.exe`

## Building Windows EXE File

### Install Required Packages
```bash
pip install pyinstaller
```

### Build Methods
```bash
# Method 1: Using spec file (Recommended)
pyinstaller HansomangAutomation.spec

# Method 2: Using build script
python build_exe.py
```

Output file: `dist/HansomangAutomation.exe`

For more details, see `BUILD_GUIDE.md`.

## Usage

### Sunday Sermon Registration Tab
1. Select the "Sunday Sermon Registration" tab
2. Enter the following information:
   - Title (default: "Hansomang Church Sunday Sermon [Today's Date]")
   - Scripture (Bible verse)
   - Preacher (default: "Pastor So Sung Bum")
   - Date (default: Today's date)
   - External video link URL
3. Click the "Start Automation" button
4. Browser will open automatically and perform the task
5. Check progress in the log window

### Popup/Notice Modification Tab
1. Select the "Popup Modification" tab
2. Enter the popup URL
3. Click the "Start Automation" button
4. Browser will open automatically and perform the task
5. Check progress in the log window

## File Structure

- `gui_app.py`: Main GUI application
- `HansomangAutomation.spec`: PyInstaller build configuration
- `build_exe.py`: EXE build script
- `setup_playwright.bat`: Playwright installation script for Windows
- `BUILD_GUIDE.md`: Detailed build guide
- `USER_MANUAL_EN.txt`: User manual in English
- `사용설명서.txt`: User manual in Korean

## Distribution Package

When distributing to Windows users, include these files:
1. `HansomangAutomation.exe` - Main executable
2. `setup_playwright.bat` - Playwright installation script
3. `USER_MANUAL_EN.txt` - User manual (English)
4. `사용설명서.txt` - User manual (Korean, optional)

## Important Notes

- **Python must be installed even when using the EXE file** (required for Playwright browser setup)
- Buttons are disabled during execution and re-enabled when complete
- All fields must be filled before execution
- Browser runs in visible mode (headless=False) so you can see the process
- EXE file size is approximately 100-200MB
- First-time use requires Playwright browser installation (~100-200MB additional)

## English Windows Compatibility

If you're using English Windows:
- Korean text in documentation files may appear as garbled characters
- Use the `*_EN.txt` files for English documentation
- The GUI application will work correctly regardless of Windows language
- `setup_playwright.bat` has been updated to work properly on English Windows

## System Requirements

- Windows 10 or later (for EXE file)
- Python 3.13 or later (for running with Python)
- Internet connection

## Language Support

- Application GUI: Korean (primary)
- Documentation available in both Korean and English
- Works on both Korean and English versions of Windows


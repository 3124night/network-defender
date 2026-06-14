@echo off
chcp 65001 >nul
echo ==========================================
echo    Network Defender Build Script
echo ==========================================
echo.

REM Check if pyinstaller is installed
pyinstaller --version >nul 2>&1
if errorlevel 1 (
    echo [INFO] Installing PyInstaller...
    pip install pyinstaller
)

echo [1/3] Cleaning old files...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist NetworkDefender.spec del NetworkDefender.spec
echo [2/3] Building exe...
pyinstaller --onefile --windowed --name NetworkDefender main.py

echo [3/3] Build complete!
echo.
echo ==========================================
echo Output: dist\NetworkDefender.exe
echo ==========================================
pause

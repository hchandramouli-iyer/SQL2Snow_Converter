@echo off
echo ========================================
echo   CodeCraft AI Desktop App - Windows
echo ========================================
echo.

REM Check if running from correct directory
if not exist "CodeCraftAI.exe" (
    echo ERROR: CodeCraftAI.exe not found in current directory!
    echo.
    echo Make sure you're running this script from the same folder
    echo where CodeCraftAI.exe is located.
    echo.
    pause
    exit /b 1
)

echo Starting CodeCraft AI Desktop Application...
echo.
echo Features Available:
echo - SQL to Snowflake Converter
echo - Interactive ER Diagram Generator  
echo - AI Code Generation Tools
echo - Chat Assistant
echo - And much more!
echo.

REM Start the application
echo Launching application...
start "" "CodeCraftAI.exe"

REM Wait a moment for the app to start
timeout /t 2 /nobreak >nul

echo.
echo CodeCraft AI is now starting!
echo.
echo If you encounter any issues:
echo 1. Make sure you have internet connection for AI features
echo 2. Check Windows Defender/Antivirus isn't blocking the app
echo 3. Try running as a different user if needed
echo.
echo Press any key to close this window...
pause >nul
@echo off
echo ==========================================
echo    🚀 STARTING TRADING ANALYSIS SYSTEM
echo ==========================================
echo.

REM Check if we're in the right directory
if not exist "web_api_server.py" (
    echo ❌ Error: Please run this from the MCP directory
    pause
    exit /b 1
)

REM Check if the email folder exists and should be renamed
if exist "email\" (
    echo ⚠️ WARNING: You have a folder named "email" which conflicts with Python's built-in email module.
    echo   This can cause errors like "ModuleNotFoundError: No module named 'email.parser'".
    echo.
    echo ✅ Solution: Rename "email" folder to "email_utils" and update imports.
    echo.
    set /p rename_choice="Do you want to rename the folder now? (y/n): "
    if /i "%rename_choice%"=="y" (
        echo Renaming folder...
        ren email email_utils
        echo ✅ Folder renamed successfully to "email_utils"
        
        echo.
        echo Updating imports in Python files...
        python update_email_imports.py
        echo.
    ) else (
        echo ⚠️ Continuing without renaming. This may cause errors.
    )
    echo.
)

echo 📁 Current directory: %CD%
echo.

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo ❌ Failed to activate virtual environment
    echo Make sure .venv exists and contains Scripts\activate.bat
    pause
    exit /b 1
)

echo ✅ Virtual environment activated
echo.

REM Start the backend API server
echo 🚀 Starting Backend API Server (Port 8001)...
start "Trading API Server" cmd /k "python web_api_server.py"

REM Wait a moment for the API server to start
timeout /t 3 /nobreak > nul

REM Start the correct MCP server
echo 🔗 Starting MCP Server...
start "MCP Trading Server" cmd /k "python mcp_server.py"

REM Wait a moment for the MCP server to start
timeout /t 2 /nobreak > nul

REM Start the frontend
echo 🎨 Starting Frontend (Port 5173)...
cd frontend
start "Trading Frontend" cmd /k "npm run dev"
cd ..

echo.
echo ==========================================
echo ✅ ALL SERVICES STARTED SUCCESSFULLY!
echo ==========================================
echo.
echo 🌐 Frontend:  http://localhost:5173
echo 📊 API:       http://localhost:8001
echo 📚 API Docs:  http://localhost:8001/docs
echo 🔗 MCP:       Running in background
echo.
echo Press any key to close this window...
echo (The services will continue running in their own windows)
pause > nul

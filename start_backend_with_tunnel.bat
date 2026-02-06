@echo off
REM Start backend with ngrok tunnel for remote access

echo.
echo ========================================
echo Color Analyzer - Backend with Tunnel
echo ========================================
echo.

REM Check if ngrok is installed
where ngrok >nul 2>nul
if %errorlevel% neq 0 (
    echo Installing ngrok...
    powershell -Command "Invoke-WebRequest -Uri 'https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-windows-amd64.zip' -OutFile '%temp%\ngrok.zip'; Expand-Archive -Path '%temp%\ngrok.zip' -DestinationPath '%USERPROFILE%\ngrok' -Force; $env:PATH += ';%USERPROFILE%\ngrok'; [Environment]::SetEnvironmentVariable('PATH', $env:PATH, [EnvironmentVariableTarget]::User)"
    set "PATH=%USERPROFILE%\ngrok;%PATH%"
)

echo.
echo 1. Starting FastAPI backend on port 8001...
echo.
cd /d d:\CALOBLOOD\Backend

start "Color Analyzer Backend" cmd /k python -m uvicorn main:app --host 0.0.0.0 --port 8001

REM Wait for backend to start
timeout /t 3 /nobreak

echo.
echo 2. Creating ngrok tunnel...
echo.

REM Start ngrok tunnel
ngrok http 8001

echo.
echo ========================================
echo Keep this window open to maintain tunnel
echo ========================================
echo.

pause

@echo off
title AutoJourney
echo ========================================
echo   AutoJourney
echo ========================================
echo.
echo Starting services...
echo.

cd /d %~dp0

:: Start backend as hidden process
powershell -Command "Start-Process -FilePath 'python' -ArgumentList '-m','uvicorn','main:app','--reload','--port','8000' -WorkingDirectory '%~dp0backend' -WindowStyle Hidden"

:: Wait for backend to be ready
echo Waiting for backend...
:wait_backend
timeout /t 2 /nobreak >nul
curl -s http://127.0.0.1:8000/api/health >nul 2>&1
if %errorlevel% neq 0 goto wait_backend
echo Backend ready on port 8000.

:: Start frontend in background
echo Starting frontend...
start /min "" cmd /c "cd /d %~dp0frontend && npm run dev"

:: Wait for frontend to be ready
echo Waiting for frontend...
:wait_frontend
timeout /t 2 /nobreak >nul
curl -s http://localhost:3000 >nul 2>&1
if %errorlevel% neq 0 goto wait_frontend

:: Open browser
echo Frontend ready. Opening browser...
start http://localhost:3000

echo.
echo   Backend:  http://127.0.0.1:8000
echo   Frontend: http://localhost:3000
echo.
echo Press any key to stop all services...
pause >nul

:: Cleanup
taskkill /f /im uvicorn.exe >nul 2>&1
taskkill /f /fi "WINDOWTITLE eq *npm*" >nul 2>&1
echo Done.

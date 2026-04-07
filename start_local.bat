@echo off
setlocal
title Serial Story Studio - Local Server
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0start_local.ps1"
if errorlevel 1 (
  echo.
  echo Startup failed. Press any key to close this window.
  pause >nul
)
endlocal

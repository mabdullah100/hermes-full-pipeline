@echo off
title Hermes Agent Desktop (Cloud OmniRoute Connected)
echo ========================================================
echo   ☤ HERMES AGENT MASTER STUDIO (Nous Research)
echo   Cloud Host: Oracle Cloud (92.4.79.176)
echo   Gateway: Cloud OmniRoute (Port 20128)
echo ========================================================
echo.
echo Launching Hermes Agent Desktop Application...
if exist "C:\Program Files\Google\Chrome\Application\chrome.exe" (
    start "" "C:\Program Files\Google\Chrome\Application\chrome.exe" --app="http://92.4.79.176/hermes/"
) else if exist "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" (
    start "" "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" --app="http://92.4.79.176/hermes/"
) else (
    start "" "http://92.4.79.176/hermes/"
)

echo.
echo Hermes Desktop App launched successfully!
echo Connected to Cloud OmniRoute Gateway: http://92.4.79.176/omniroute/v1
timeout /t 3 >nul
exit

@echo off
title Hermes Agent Desktop & OmniRoute Bridge
echo ========================================================
echo   ☤ HERMES AGENT MASTER STUDIO (Nous Research)
echo   Cloud Host: Oracle Cloud (92.4.79.176)
echo ========================================================
echo.
echo [1/2] Bridging OmniRoute Gateway (port 20128) to Oracle Cloud...
start /b "" ssh -o StrictHostKeyChecking=no -N -R 20128:127.0.0.1:20128 -i "C:\Users\abdul\Downloads\ssh-key-2026-09-04.key" opc@92.4.79.176

echo [2/2] Launching Hermes Agent Desktop Application...
if exist "C:\Program Files\Google\Chrome\Application\chrome.exe" (
    start "" "C:\Program Files\Google\Chrome\Application\chrome.exe" --app="http://92.4.79.176/hermes/"
) else if exist "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" (
    start "" "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" --app="http://92.4.79.176/hermes/"
) else (
    start "" "http://92.4.79.176/hermes/"
)

echo.
echo Hermes Desktop App launched successfully!
echo You can keep this window minimized or close it when done.
timeout /t 5 >nul
exit

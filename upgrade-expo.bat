@echo off
rem Finishes the upgrade to Expo SDK 58: clean reinstall of all packages. Safe to run again.
title InstaLearn - upgrade to Expo SDK 58
cd /d "%~dp0"
echo Step 1/4: removing the old installed packages (they will be downloaded again)...
if exist node_modules rmdir /s /q node_modules
if exist package-lock.json del /q package-lock.json
echo.
echo Step 2/4: installing packages for SDK 58 (a few minutes)...
call npm install --no-audit --no-fund
if errorlevel 1 (
  echo.
  echo Retrying with relaxed version checks...
  call npm install --no-audit --no-fund --legacy-peer-deps
  if errorlevel 1 goto failed
  rem keep using relaxed checks for later installs too
  echo legacy-peer-deps=true> .npmrc
)
echo.
echo Step 3/4: aligning package versions with SDK 58...
call npx expo install --fix
echo.
echo Step 4/4: checking the project...
call npx --yes expo-doctor@latest
echo.
echo Done. Now double-click start-app.bat
pause
exit /b 0
:failed
echo.
echo The upgrade failed - send a screenshot of this window (scroll up to the first red lines).
pause
exit /b 1

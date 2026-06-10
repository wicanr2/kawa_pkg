@echo off
rem === Kawarazakike no Ichizoku XP - Traditional Chinese launcher ===
cd /d "%~dp0"
rem the no-CD exe checks this install marker; point it at this folder's AI.exe
reg add "HKCU\Software\elf\KAWAXP-CD" /v InstExec /t REG_SZ /d "%~dp0AI.exe" /f >nul 2>&1
reg add "HKLM\Software\elf\KAWAXP-CD" /v InstExec /t REG_SZ /d "%~dp0AI.exe" /f >nul 2>&1
start "" "%~dp0AI.exe"

@echo off
rem Copies the Fusion folder next to this file into DaVinci Resolve's Fusion user folder (Windows).
rem Double-click this file. Quit DaVinci Resolve first.
setlocal
set "HERE=%~dp0"
set "DEST=%APPDATA%\Blackmagic Design\DaVinci Resolve\Support\Fusion"
if not "%PLUGIN_DEST%"=="" set "DEST=%PLUGIN_DEST%"
echo Installing to: %DEST%
if not exist "%DEST%" mkdir "%DEST%"
robocopy "%HERE%Fusion" "%DEST%" /E /NFL /NDL /NJH /NJS /NP >nul
if errorlevel 8 goto failed
echo.
echo Done. Start DaVinci Resolve.
pause
exit /b 0
:failed
echo.
echo Copy failed. Quit DaVinci Resolve and try again.
pause
exit /b 1

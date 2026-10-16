@echo off
REM Auto-run wrapper for quant lab install (no pause, runs unattended)

cd /d %~dp0
echo Starting install at %DATE% %TIME% > install.log
echo. >> install.log

call install-quant-lab-llms.bat >> install.log 2>&1
echo. >> install.log
echo Install completed at %DATE% %TIME% with exit code %ERRORLEVEL% >> install.log

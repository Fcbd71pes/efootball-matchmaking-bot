@echo off
title Stop eFootball Bot and Admin Panel
echo Stopping eFootball Bot and Admin Panel running in the background...
echo.

powershell -Command "Get-CimInstance Win32_Process -Filter \"Name like 'python%%' or Name like 'py%%'\" | ForEach-Object { if ($_.CommandLine -like '*main.py*' -or $_.CommandLine -like '*admin_panel.py*') { Stop-Process -Id $_.ProcessId -Force; Write-Host 'Successfully stopped:' $_.CommandLine } }"

echo.
echo Stop complete.
pause

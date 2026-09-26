@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0"
title AetherStore Distributed Storage Demo
chcp 65001 >nul

echo ==============================================================================
echo              AETHERSTORE DISTRIBUTED OBJECT STORAGE ENGINE
echo ==============================================================================
echo.

python demo.py %*
set "EXIT_CODE=%ERRORLEVEL%"

if !EXIT_CODE! NEQ 0 (
    echo.
    echo [ERROR] Demo exited with error code !EXIT_CODE!.
)

echo.
pause

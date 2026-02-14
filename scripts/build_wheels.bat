@echo off
REM This script was copied from PythonQwt project
REM ======================================================
REM Package build script
REM ======================================================
REM Licensed under the terms of the MIT License
REM Copyright (c) 2020 Pierre Raybaut
REM (see PythonQwt LICENSE file for more details)
REM ======================================================
setlocal enabledelayedexpansion
set FUNC=%~dp0utils.bat
call %FUNC% GetScriptPath SCRIPTPATH
call %FUNC% GetModName MODNAME

REM Go to project root
cd /d "%~dp0.."

if exist MANIFEST ( del /q MANIFEST )

set "BUILD_DONE="

REM Try to detect WinPython environment
call %FUNC% GetPythonExeGrandParentDir DIR0
if defined DIR0 (
    for /D %%d in ("%DIR0%*") do (
        for %%n in (%%d) do set "DIRNAME=%%~nxn"
        REM Check if directory seems to be a WinPython directory (heuristic)
        if not "!DIRNAME:~-6!"=="-PyQt6" (
            if not "!DIRNAME:~-8!"=="-PySide6" (
                if exist "%%d\scripts\env.bat" (
                    set WINPYDIRBASE=%%d
                    set OLD_PATH=!PATH!
                    call !WINPYDIRBASE!\scripts\env.bat
                    echo ******************************************************************************
                    echo Building %MODNAME% from "%%d"
                    echo ******************************************************************************
                    python -m build
                    echo ----
                    set PATH=!OLD_PATH!
                    set BUILD_DONE=1
                )
            )
        )
    )
)

REM Fallback: run in current environment if no WinPython build occurred
if not defined BUILD_DONE (
    echo ******************************************************************************
    echo Building %MODNAME% in current environment
    echo ******************************************************************************
    if defined PYTHON (
        "%PYTHON%" -m build
    ) else (
        python -m build
    )
)

call %FUNC% EndOfScript
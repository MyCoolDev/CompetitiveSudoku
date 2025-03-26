@echo off
REM Check if an argument is provided
if "%1"=="" (
    echo Usage: run.bat [test|official]
    exit /b 1
)

REM Set default values
set HOST=127.0.0.1
set PORT=8000
set STATUS=test

REM Configure based on the argument
if "%1"=="test" (
    set HOST=127.0.0.1
    set PORT=8080
    set STATUS=0
) else if "%1"=="official" (
    set HOST=0.0.0.0
    set PORT=8000
    set STATUS=1
) else (
    echo Invalid argument. Use test, debug, or official.
    exit /b 1
)

REM Run the server with the selected configuration
python %~pd0Server\ServerSocket.py --host %HOST% --port %PORT% --database %STATUS%
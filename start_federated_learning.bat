@echo off
setlocal EnableExtensions EnableDelayedExpansion

cd /d "%~dp0"
title Federated Learning Service Launcher

set "VENV_DIR=.venv"
set "FORCE_REINSTALL=0"
set "SKIP_INSTALL=0"
set "START_AUTOMATED_TRAINING=0"
set "SHOW_HELP=0"
set "ENABLE_LOG=1"
set "USE_FULL_REQUIREMENTS=0"
set "PY_BOOTSTRAP="
set "PYTHON_EXE="
set "LOG_FILE="
set "REQUIREMENTS_FILE=requirements_web_assistant.txt"

rem Auto-log wrapper: relaunches once with all output redirected to a timestamped log file.
if "%BATCH_LOG_REDIRECTED%"=="" (
  call :parse_args %*
  if "!SHOW_HELP!"=="1" (
    call :show_help
    exit /b 0
  )
  if "!ENABLE_LOG!"=="1" (
    set "BATCH_LOG_REDIRECTED=1"
    call :init_log
    if not defined LOG_FILE set "LOG_FILE=%CD%\logs\bat\start_federated_learning_fallback.log"
    call "%~f0" --no-log-wrap %* 1>>"!LOG_FILE!" 2>>&1
    set "EXIT_CODE=%ERRORLEVEL%"
    echo [INFO] Log file: !LOG_FILE!
    if not "!EXIT_CODE!"=="0" (
      echo [ERROR] start_federated_learning.bat failed with code !EXIT_CODE!.
      echo [ERROR] Showing last 40 log lines:
      powershell -NoProfile -Command "Get-Content -Path \"!LOG_FILE!\" -Tail 40"
      pause
    )
    exit /b !EXIT_CODE!
  )
)

call :parse_args %*
if "%SHOW_HELP%"=="1" (
  call :show_help
  exit /b 0
)
if errorlevel 1 exit /b 1

echo [1/6] Checking Python...
call :ensure_python
if errorlevel 1 exit /b 1

echo [2/6] Preparing virtual environment...
call :ensure_venv
if errorlevel 1 exit /b 1

echo [3/6] Upgrading pip tooling...
"%PYTHON_EXE%" -m pip install --upgrade pip setuptools wheel
if errorlevel 1 (
  echo [ERROR] Failed to upgrade pip tooling.
  exit /b 1
)

if "%SKIP_INSTALL%"=="1" (
  echo [4/6] Skipping dependency install as requested.
) else (
  if "%USE_FULL_REQUIREMENTS%"=="1" set "REQUIREMENTS_FILE=requirements.txt"
  echo [4/6] Installing dependencies from %REQUIREMENTS_FILE%...
  if not exist "%REQUIREMENTS_FILE%" (
    echo [ERROR] Requirements file not found: %REQUIREMENTS_FILE%
    exit /b 1
  )
  set "PIP_FLAGS="
  if "%FORCE_REINSTALL%"=="1" set "PIP_FLAGS=--upgrade --force-reinstall"
  rem pip already skips installed packages unless --force-reinstall is used.
  "%PYTHON_EXE%" -m pip install %PIP_FLAGS% -r "%REQUIREMENTS_FILE%"
  if errorlevel 1 (
    echo [ERROR] Dependency install failed.
    exit /b 1
  )
)

echo [5/6] Ensuring env files exist...
if not exist ".env" (
  if exist ".env.example" copy /y ".env.example" ".env" >nul
)
if not exist "web-assistant\.env" (
  if exist "web-assistant\.env.example" copy /y "web-assistant\.env.example" "web-assistant\.env" >nul
)

echo [6/6] Starting federated learning services in parallel windows...
start "Auth Server :7000" cmd /k "cd /d "%CD%\web-assistant\services\auth" && "%PYTHON_EXE%" auth_server.py"
start "AI Server :8000 (Federated Learning)" cmd /k "cd /d "%CD%\web-assistant\services\central_server" && "%PYTHON_EXE%" ai_server.py"
start "Web Assistant :5000" cmd /k "cd /d "%CD%\web-assistant" && "%PYTHON_EXE%" app.py"

if "%START_AUTOMATED_TRAINING%"=="1" (
  start "Automated Training Service" cmd /k "cd /d "%CD%\web-assistant\services\training_triggers" && "%PYTHON_EXE%" automated_service.py"
)

echo.
echo Federated Learning Services Started!
echo.
echo Core Services:
echo   Auth Server:        http://localhost:7000/health
echo   AI Server:          http://localhost:8000/health (Federated Learning enabled)
echo   Web Assistant:      http://localhost:5000/health
echo.
echo Federated Learning Endpoints:
echo   Register device:    POST http://localhost:8000/federated/register
echo   Start round:        POST http://localhost:8000/federated/round/start
echo   Submit update:      POST http://localhost:8000/federated/update/submit
echo.
echo Optional Services:
if "%START_AUTOMATED_TRAINING%"=="1" (
  echo   Automated Training: Running (trains models every 15 minutes)
) else (
  echo   Automated Training: Not started (add --start-automated-training to enable)
)
echo.
echo To stop all services, run: stop_all_services.bat
echo.
echo Tip: Use --start-automated-training to enable automatic model training based on data triggers.
exit /b 0

:parse_args
if "%~1"=="" goto :eof
if /I "%~1"=="--force-reinstall" set "FORCE_REINSTALL=1"
if /I "%~1"=="--skip-install" set "SKIP_INSTALL=1"
if /I "%~1"=="--start-automated-training" set "START_AUTOMATED_TRAINING=1"
if /I "%~1"=="--full-install" set "USE_FULL_REQUIREMENTS=1"
if /I "%~1"=="--help" set "SHOW_HELP=1"
if /I "%~1"=="--no-log-wrap" set "ENABLE_LOG=0"
shift
goto :parse_args

:show_help
echo.
echo Federated Learning Service Launcher
echo ===================================
echo.
echo This script starts all services required for federated learning functionality.
echo.
echo USAGE: start_federated_learning.bat [OPTIONS]
echo.
echo OPTIONS:
echo   --force-reinstall        Force reinstall all Python packages
echo   --skip-install           Skip package installation (use existing venv)
echo   --start-automated-training  Start automated training service
echo   --full-install           Use requirements.txt instead of requirements_web_assistant.txt
echo   --help                   Show this help message
echo   --no-log-wrap            Disable automatic logging to file
echo.
echo SERVICES STARTED:
echo   - Auth Server (port 7000) - User authentication
echo   - AI Server (port 8000) - Central AI with federated learning endpoints
echo   - Web Assistant (port 5000) - Main web interface
echo   - Automated Training (optional) - Background model training
echo.
echo FEDERATED LEARNING ENDPOINTS:
echo   POST /federated/register - Register a device as participant
echo   POST /federated/round/start - Start new federated learning round
echo   POST /federated/update/submit - Submit model update from device
echo.
echo EXAMPLES:
echo   start_federated_learning.bat
echo   start_federated_learning.bat --start-automated-training
echo   start_federated_learning.bat --skip-install --start-automated-training
echo.
goto :eof

:ensure_python
rem Check for python executable
where python >nul 2>&1
if errorlevel 1 (
  echo [ERROR] Python not found in PATH. Please install Python 3.9+ and try again.
  exit /b 1
)

rem Get python executable path and version
for /f "tokens=*" %%i in ('where python') do set "PYTHON_EXE=%%i" & goto :python_found
:python_found

"%PYTHON_EXE%" --version >nul 2>&1
if errorlevel 1 (
  echo [ERROR] Failed to execute Python. Please check your Python installation.
  exit /b 1
)

rem Check python version (require 3.9+)
for /f "tokens=2" %%i in ('"%PYTHON_EXE%" --version 2^>^&1') do set "PY_VER=%%i"
for /f "tokens=1,2 delims=." %%a in ("%PY_VER%") do (
  set "PY_MAJOR=%%a"
  set "PY_MINOR=%%b"
)
if %PY_MAJOR% lss 3 (
  echo [ERROR] Python %PY_VER% is too old. Please install Python 3.9 or newer.
  exit /b 1
)
if %PY_MAJOR%==3 if %PY_MINOR% lss 9 (
  echo [ERROR] Python %PY_VER% is too old. Please install Python 3.9 or newer.
  exit /b 1
)

echo [INFO] Using Python %PY_VER% at: %PYTHON_EXE%
goto :eof

:ensure_venv
rem Check if venv exists, create if not
if not exist "%VENV_DIR%" (
  echo [INFO] Creating virtual environment...
  "%PYTHON_EXE%" -m venv "%VENV_DIR%"
  if errorlevel 1 (
    echo [ERROR] Failed to create virtual environment.
    exit /b 1
  )
)

rem Activate venv and update PYTHON_EXE
set "PYTHON_EXE=%CD%\%VENV_DIR%\Scripts\python.exe"
if not exist "%PYTHON_EXE%" (
  echo [ERROR] Virtual environment Python executable not found: %PYTHON_EXE%
  exit /b 1
)

rem Verify venv activation
"%PYTHON_EXE%" -c "import sys; print(f'Venv activated: {sys.prefix}')"

echo [INFO] Virtual environment ready at: %VENV_DIR%
goto :eof

:init_log
rem Create logs directory if it doesn't exist
if not exist "logs\bat" mkdir "logs\bat" 2>nul

rem Generate timestamped log filename
for /f "tokens=2-4 delims=/ " %%a in ('date /t') do set "DATE_STR=%%c-%%a-%%b"
for /f "tokens=1-2 delims=: " %%a in ('time /t') do set "TIME_STR=%%a-%%b"
set "TIMESTAMP=%DATE_STR%_%TIME_STR%"
set "LOG_FILE=%CD%\logs\bat\start_federated_learning_%TIMESTAMP%.log"

echo [INFO] Logging to: %LOG_FILE%
goto :eof
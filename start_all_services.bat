@echo off
setlocal EnableExtensions EnableDelayedExpansion

cd /d "%~dp0"
title Ai-Robot Service Launcher

set "VENV_DIR=.venv"
set "FORCE_REINSTALL=0"
set "SKIP_INSTALL=0"
set "START_LOCAL_PI_AGENT=0"
set "START_LOCAL_PI_WEB=0"
set "START_EPUB_READER=0"
set "START_PI_REMOTE=0"
set "SHOW_HELP=0"
set "ENABLE_LOG=1"
set "USE_FULL_REQUIREMENTS=0"
set "PY_BOOTSTRAP="
set "PYTHON_EXE="
set "LOG_FILE="
set "REQUIREMENTS_FILE=requirements_web_assistant.txt"

rem Optional remote Pi settings (used only with --start-pi-remote)
set "PI_HOST=raspberrypi.local"
set "PI_USER=pi"
set "PI_PROJECT_DIR=~/Ai-Robot/be-more-agent-main"

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
    if not defined LOG_FILE set "LOG_FILE=%CD%\logs\bat\start_all_services_fallback.log"
    call "%~f0" --no-log-wrap %* 1>>"!LOG_FILE!" 2>>&1
    set "EXIT_CODE=%ERRORLEVEL%"
    echo [INFO] Log file: !LOG_FILE!
    if not "!EXIT_CODE!"=="0" (
      echo [ERROR] start_all_services.bat failed with code !EXIT_CODE!.
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

echo [1/7] Checking Python...
call :ensure_python
if errorlevel 1 exit /b 1

echo [2/7] Preparing virtual environment...
call :ensure_venv
if errorlevel 1 exit /b 1

echo [3/7] Upgrading pip tooling...
"%PYTHON_EXE%" -m pip install --upgrade pip setuptools wheel
if errorlevel 1 (
  echo [ERROR] Failed to upgrade pip tooling.
  exit /b 1
)

if "%SKIP_INSTALL%"=="1" (
  echo [4/7] Skipping dependency install as requested.
) else (
  if "%USE_FULL_REQUIREMENTS%"=="1" set "REQUIREMENTS_FILE=requirements.txt"
  echo [4/7] Installing dependencies from %REQUIREMENTS_FILE%...
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

echo [5/7] Ensuring env files exist...
if not exist ".env" (
  if exist ".env.example" copy /y ".env.example" ".env" >nul
)
if not exist "web-assistant\.env" (
  if exist "web-assistant\.env.example" copy /y "web-assistant\.env.example" "web-assistant\.env" >nul
)

echo [6/7] Starting local services in parallel windows...
start "Auth Server :7000" cmd /k "cd /d "%CD%\web-assistant\services\auth" && "%PYTHON_EXE%" auth_server.py"
start "AI Server :8000" cmd /k "cd /d "%CD%\web-assistant\services\central_server" && "%PYTHON_EXE%" ai_server.py"
start "Web Assistant :5000" cmd /k "cd /d "%CD%\web-assistant" && "%PYTHON_EXE%" app.py"

if "%START_LOCAL_PI_WEB%"=="1" (
  start "Pi Web App Local :8090" cmd /k "cd /d "%CD%\be-more-agent-main" && "%PYTHON_EXE%" web_app.py"
)

if "%START_LOCAL_PI_AGENT%"=="1" (
  start "Pi Agent Local" cmd /k "cd /d "%CD%\be-more-agent-main" && "%PYTHON_EXE%" agent.py"
)

if "%START_EPUB_READER%"=="1" (
  where pnpm >nul 2>&1
  if errorlevel 1 (
    echo [WARN] pnpm not found. EPUB reader cannot start.
  ) else (
    start "EPUB Reader :3000" cmd /k "cd /d "%CD%\web-assistant\frontend\epub-reader" && pnpm dev"
  )
)

if "%START_PI_REMOTE%"=="1" (
  echo [INFO] Attempting remote Pi startup over SSH...
  call :start_remote_pi
)

echo [7/7] Done.
echo.
echo Health checks:
echo   http://localhost:7000/health
echo   http://localhost:8000/health
echo   http://localhost:5000/health
if "%START_LOCAL_PI_WEB%"=="1" echo   http://localhost:8090
echo.
echo Tip: add --start-local-pi-web to run the Pi web UI locally for testing.
echo Tip: add --start-local-pi-agent to run the Pi agent locally for testing.
echo Tip: add --start-pi-remote only when you intentionally want to start a separate Pi over SSH.
exit /b 0

:parse_args
if "%~1"=="" goto :eof
if /I "%~1"=="--force-reinstall" set "FORCE_REINSTALL=1"
if /I "%~1"=="--skip-install" set "SKIP_INSTALL=1"
if /I "%~1"=="--start-local-pi-web" set "START_LOCAL_PI_WEB=1"
if /I "%~1"=="--start-local-pi-agent" set "START_LOCAL_PI_AGENT=1"
if /I "%~1"=="--start-epub-reader" set "START_EPUB_READER=1"
if /I "%~1"=="--start-pi-remote" set "START_PI_REMOTE=1"
if /I "%~1"=="--full-install" set "USE_FULL_REQUIREMENTS=1"
if /I "%~1"=="--help" set "SHOW_HELP=1"
if /I "%~1"=="--no-log-wrap" set "ENABLE_LOG=0"
shift
goto parse_args

:show_help
echo Usage:
echo   start_all_services.bat [--skip-install] [--force-reinstall] [--full-install] [--start-local-pi-web] [--start-local-pi-agent] [--start-pi-remote]
echo.
echo Options:
echo   --skip-install         Skip pip install steps.
echo   --force-reinstall      Force reinstall requirements instead of skip-if-installed behavior.
echo   --full-install         Use requirements.txt (full ecosystem). Default is requirements_web_assistant.txt.
echo   --start-local-pi-web   Start be-more-agent-main/web_app.py on this Windows machine for demo/testing.
echo   --start-local-pi-agent Start be-more-agent-main/agent.py on this Windows machine.
echo   --start-epub-reader   Start the Thorium Web EPUB reader from web-assistant/frontend/epub-reader.
echo   --start-pi-remote      Start the Pi services over SSH only when a separate Pi is reachable.
echo   --no-log-wrap          Internal flag. Skip auto log wrapper.
echo.
echo Remote Pi config variables are at the top of this file: PI_HOST, PI_USER, PI_PROJECT_DIR.
exit /b 0

:init_log
if not exist "logs\bat" mkdir "logs\bat" >nul 2>&1
for /f %%T in ('powershell -NoProfile -Command "Get-Date -Format yyyyMMdd_HHmmss"') do set "STAMP=%%T"
set "LOG_FILE=%CD%\logs\bat\start_all_services_%STAMP%.log"
exit /b 0

:ensure_python
py -3.11 --version >nul 2>&1
if %errorlevel%==0 (
  set "PY_BOOTSTRAP=py -3.11"
  goto :python_ready
)

py -3.10 --version >nul 2>&1
if %errorlevel%==0 (
  set "PY_BOOTSTRAP=py -3.10"
  goto :python_ready
)

where python >nul 2>&1
if %errorlevel%==0 (
  python -c "import sys; raise SystemExit(0 if sys.version_info[:2] in {(3, 10), (3, 11)} else 1)" >nul 2>&1
  if !errorlevel! == 0 (
    set "PY_BOOTSTRAP=python"
    goto :python_ready
  )
)

echo [WARN] Python not found. Trying winget install...
where winget >nul 2>&1
if not %errorlevel%==0 (
  echo [ERROR] winget not found. Install Python 3.10+ manually, then rerun.
  exit /b 1
)

winget install -e --id Python.Python.3.11 --accept-package-agreements --accept-source-agreements
if errorlevel 1 (
  echo [ERROR] Python install via winget failed.
  exit /b 1
)

py -3.11 --version >nul 2>&1
if %errorlevel%==0 (
  set "PY_BOOTSTRAP=py -3.11"
  goto :python_ready
)

py -3.10 --version >nul 2>&1
if %errorlevel%==0 (
  set "PY_BOOTSTRAP=py -3.10"
  goto :python_ready
)

where python >nul 2>&1
if %errorlevel%==0 (
  python -c "import sys; raise SystemExit(0 if sys.version_info[:2] in {(3, 10), (3, 11)} else 1)" >nul 2>&1
  if !errorlevel! == 0 (
    set "PY_BOOTSTRAP=python"
    goto :python_ready
  )
)

echo [ERROR] A compatible Python 3.10 or 3.11 install was not found after install.
exit /b 1

:python_ready
echo [OK] Python bootstrap command: %PY_BOOTSTRAP%
exit /b 0

:ensure_venv
if exist "%VENV_DIR%\Scripts\python.exe" (
  "%VENV_DIR%\Scripts\python.exe" -c "import sys; raise SystemExit(0 if sys.version_info[:2] in {(3, 10), (3, 11)} else 1)" >nul 2>&1
  if errorlevel 1 (
    echo [WARN] Existing venv uses an incompatible Python version. Recreating %VENV_DIR%...
    rmdir /s /q "%VENV_DIR%"
  ) else (
  set "PYTHON_EXE=%CD%\%VENV_DIR%\Scripts\python.exe"
  echo [OK] Using existing venv: %VENV_DIR%
  exit /b 0
  )
)

echo [INFO] Creating venv in %VENV_DIR%...
%PY_BOOTSTRAP% -m venv "%VENV_DIR%"
if errorlevel 1 (
  echo [ERROR] Failed to create venv.
  exit /b 1
)

set "PYTHON_EXE=%CD%\%VENV_DIR%\Scripts\python.exe"
echo [OK] Created venv: %VENV_DIR%
exit /b 0

:start_remote_pi
where ssh >nul 2>&1
if not %errorlevel%==0 (
  echo [ERROR] SSH client not found. Install OpenSSH client and rerun.
  exit /b 1
)

echo [INFO] Remote target: %PI_USER%@%PI_HOST% (%PI_PROJECT_DIR%)
start "Remote Pi Starter" cmd /k "ssh %PI_USER%@%PI_HOST% \"cd %PI_PROJECT_DIR% ; nohup bash start_agent.sh > /tmp/pi_agent.log 2>&1 ^& nohup bash start_web.sh > /tmp/pi_web.log 2>&1 ^& echo started\""
exit /b 0

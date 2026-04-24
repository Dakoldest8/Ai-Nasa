@echo off
setlocal EnableExtensions EnableDelayedExpansion

cd /d "%~dp0"
title Ai-Robot Service Stopper

set "STOP_REMOTE_PI=0"
set "SHOW_HELP=0"
set "ENABLE_LOG=1"
set "PI_HOST=raspberrypi.local"
set "PI_USER=pi"
set "LOG_FILE="

rem Auto-log wrapper: relaunch once with redirected output.
if "%BATCH_LOG_REDIRECTED%"=="" (
  call :parse_args %*
  if "!SHOW_HELP!"=="1" (
    call :show_help
    exit /b 0
  )
  if "!ENABLE_LOG!"=="1" (
    set "BATCH_LOG_REDIRECTED=1"
    call :init_log
    if not defined LOG_FILE set "LOG_FILE=%CD%\logs\bat\stop_all_services_fallback.log"
    call "%~f0" --no-log-wrap %* 1>>"!LOG_FILE!" 2>>&1
    set "EXIT_CODE=%ERRORLEVEL%"
    echo [INFO] Log file: !LOG_FILE!
    if not "!EXIT_CODE!"=="0" (
      echo [ERROR] stop_all_services.bat failed with code !EXIT_CODE!.
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

echo [1/3] Stopping local services on known ports...
call :stop_port 5000 "Web Assistant"
call :stop_port 7000 "Auth Server"
call :stop_port 8000 "AI Server"
call :stop_port 8090 "Pi Web App"

echo [2/3] Stopping local Pi agent processes if running...
call :stop_process "agent.py"
call :stop_process "web_app.py"

echo [2.5/3] Closing launcher terminal windows...
call :close_window "Auth Server :7000"
call :close_window "AI Server :8000"
call :close_window "Web Assistant :5000"
call :close_window "Pi Web App Local :8090"
call :close_window "Pi Agent Local"
call :close_window "Remote Pi Starter"

if "%STOP_REMOTE_PI%"=="1" (
  echo [3/3] Stopping remote Pi services over SSH...
  call :stop_remote_pi
) else (
  echo [3/3] Remote Pi stop skipped.
)

echo Done.
exit /b 0

:parse_args
if "%~1"=="" goto :eof
if /I "%~1"=="--stop-pi-remote" set "STOP_REMOTE_PI=1"
if /I "%~1"=="--help" set "SHOW_HELP=1"
if /I "%~1"=="--no-log-wrap" set "ENABLE_LOG=0"
shift
goto parse_args

:show_help
echo Usage:
echo   stop_all_services.bat [--stop-pi-remote]
echo.
echo Options:
echo   --stop-pi-remote   Stop be-more-agent-main/start_agent.sh and start_web.sh processes on the Pi over SSH.
echo   --no-log-wrap      Internal flag. Skip auto log wrapper.
echo.
echo Remote Pi config variables are at the top of this file: PI_HOST, PI_USER.
exit /b 0

:init_log
if not exist "logs\bat" mkdir "logs\bat" >nul 2>&1
for /f %%T in ('powershell -NoProfile -Command "Get-Date -Format yyyyMMdd_HHmmss"') do set "STAMP=%%T"
set "LOG_FILE=%CD%\logs\bat\stop_all_services_%STAMP%.log"
exit /b 0

:stop_port
set "PORT=%~1"
set "LABEL=%~2"
set "FOUND=0"
for /f "tokens=5" %%P in ('netstat -ano ^| findstr ":%PORT%" ^| findstr "LISTENING"') do (
  set "FOUND=1"
  echo [INFO] Stopping !LABEL! on port %PORT% ^(PID %%P^)
  taskkill /PID %%P /F >nul 2>&1
)
if "!FOUND!"=="0" echo [INFO] No listener found on port %PORT% for !LABEL!.
exit /b 0

:stop_process
set "PROCNAME=%~1"
tasklist /FI "IMAGENAME eq python.exe" /V | findstr /I "%PROCNAME%" >nul 2>&1
if errorlevel 1 (
  echo [INFO] No python window matched %PROCNAME%.
  exit /b 0
)
for /f "tokens=2" %%P in ('tasklist /FI "IMAGENAME eq python.exe" /V ^| findstr /I "%PROCNAME%"') do (
  echo [INFO] Stopping python process %%P matching %PROCNAME%
  taskkill /PID %%P /F >nul 2>&1
)
exit /b 0

:close_window
set "WTITLE=%~1"
tasklist /FI "IMAGENAME eq cmd.exe" /V | findstr /I /C:"%WTITLE%" >nul 2>&1
if errorlevel 1 (
  echo [INFO] No terminal window matched "%WTITLE%".
  exit /b 0
)

for /f "tokens=2" %%P in ('tasklist /FI "IMAGENAME eq cmd.exe" /V ^| findstr /I /C:"%WTITLE%"') do (
  echo [INFO] Closing terminal window "%WTITLE%" ^(PID %%P^)
  taskkill /PID %%P /T /F >nul 2>&1
)
exit /b 0

:stop_remote_pi
where ssh >nul 2>&1
if not %errorlevel%==0 (
  echo [ERROR] SSH client not found. Install OpenSSH client and rerun.
  exit /b 1
)

echo [INFO] Remote target: %PI_USER%@%PI_HOST%
ssh %PI_USER%@%PI_HOST% "pkill -f 'start_agent.sh'; pkill -f 'start_web.sh'; pkill -f 'python.*agent.py'; pkill -f 'python.*web_app.py'; echo stopped"
exit /b 0

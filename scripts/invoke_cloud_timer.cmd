@echo off
setlocal

REM Invoke deployed cloud function in timer mode (Windows CMD wrapper).
REM Usage:
REM   scripts\invoke_cloud_timer.cmd [FUNCTION_URL] [--live]
REM Examples:
REM   scripts\invoke_cloud_timer.cmd
REM   scripts\invoke_cloud_timer.cmd https://dtm-api-test.solofarm.ru --live

cd /d "%~dp0\.."
set "PYTHONIOENCODING=utf-8"

if not exist ".venv\Scripts\python.exe" (
  if not exist "venv\Scripts\python.exe" (
    echo [ERROR] python venv not found in .venv or venv
    exit /b 1
  )
  set "PYTHON_BIN=venv\Scripts\python.exe"
) else (
  set "PYTHON_BIN=.venv\Scripts\python.exe"
)

set "FUNCTION_URL=%~1"
set "DEFAULT_FUNCTION_URL=https://dtm-api-test.solofarm.ru"
set "RUN_MODE_FLAG=--dry-run"
set "MOCK_FLAG=--mock-external"

if /I "%~2"=="--live" (
  set "RUN_MODE_FLAG="
  set "MOCK_FLAG="
)
if /I "%~1"=="--live" (
  set "FUNCTION_URL=%DEFAULT_FUNCTION_URL%"
  set "RUN_MODE_FLAG="
  set "MOCK_FLAG="
)

if not defined FUNCTION_URL set "FUNCTION_URL=%DEFAULT_FUNCTION_URL%"

if defined FUNCTION_URL (
  "%PYTHON_BIN%" agent\invoke_function_smoke.py --url "%FUNCTION_URL%" --mode timer %RUN_MODE_FLAG% %MOCK_FLAG%
) else (
  "%PYTHON_BIN%" agent\invoke_function_smoke.py --mode timer %RUN_MODE_FLAG% %MOCK_FLAG%
)

set EXIT_CODE=%ERRORLEVEL%
endlocal & exit /b %EXIT_CODE%

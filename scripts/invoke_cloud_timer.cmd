@echo off
setlocal

REM Invoke deployed cloud function in timer mode (Windows CMD wrapper).
REM Usage:
REM   scripts\invoke_cloud_timer.cmd [FUNCTION_URL] [--live] [--sync-only] [--force-refresh]
REM Examples:
REM   scripts\invoke_cloud_timer.cmd
REM   scripts\invoke_cloud_timer.cmd https://dtm-api-test.solofarm.ru --live
REM   scripts\invoke_cloud_timer.cmd --sync-only --force-refresh --live

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

set "DEFAULT_FUNCTION_URL=https://dtm-api-test.solofarm.ru"
set "FUNCTION_URL="
set "RUN_MODE=timer"
set "RUN_MODE_FLAG=--dry-run"
set "MOCK_FLAG=--mock-external"
set "FORCE_REFRESH_FLAG="

:parse_args
if "%~1"=="" goto :args_done
if /I "%~1"=="--live" (
  set "RUN_MODE_FLAG="
  set "MOCK_FLAG="
  shift
  goto :parse_args
)
if /I "%~1"=="--sync-only" (
  set "RUN_MODE=sync-only"
  shift
  goto :parse_args
)
if /I "%~1"=="--force-refresh" (
  set "FORCE_REFRESH_FLAG=--force-refresh"
  shift
  goto :parse_args
)
if not defined FUNCTION_URL (
  set "FUNCTION_URL=%~1"
  shift
  goto :parse_args
)
echo [WARN] Unknown argument ignored: %~1
shift
goto :parse_args

:args_done

if not defined FUNCTION_URL set "FUNCTION_URL=%DEFAULT_FUNCTION_URL%"

if defined FUNCTION_URL (
  "%PYTHON_BIN%" agent\invoke_function_smoke.py --url "%FUNCTION_URL%" --mode %RUN_MODE% %RUN_MODE_FLAG% %MOCK_FLAG% %FORCE_REFRESH_FLAG%
) else (
  "%PYTHON_BIN%" agent\invoke_function_smoke.py --mode %RUN_MODE% %RUN_MODE_FLAG% %MOCK_FLAG% %FORCE_REFRESH_FLAG%
)

set EXIT_CODE=%ERRORLEVEL%
endlocal & exit /b %EXIT_CODE%

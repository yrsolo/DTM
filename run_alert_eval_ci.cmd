@echo off
setlocal

REM Run from project root regardless of current directory
cd /d "%~dp0"

if not exist ".venv\Scripts\activate.bat" (
  if not exist "venv\Scripts\activate.bat" (
    echo [ERROR] virtualenv not found in .venv or venv
    echo Create environment first, for example:
    echo   py -m venv .venv
    echo   .venv\Scripts\python -m pip install -r requirements.txt
    exit /b 1
  )
  call "venv\Scripts\activate.bat"
) else (
  call ".venv\Scripts\activate.bat"
)

set "PYTHONIOENCODING=utf-8"
python agent\reminder_alert_evaluator.py --format text --fail-profile ci %*
set EXIT_CODE=%ERRORLEVEL%

endlocal & exit /b %EXIT_CODE%

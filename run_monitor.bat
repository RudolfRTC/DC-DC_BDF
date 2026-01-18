@echo off
REM DC-DC Monitor Windows Launcher
echo ======================================================================
echo   DC-DC Converter Monitor - Windows Edition
echo ======================================================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from https://www.python.org/downloads/
    pause
    exit /b 1
)

echo Python found:
python --version
echo.

echo Checking dependencies...
python check_dependencies.py
set DEPS_STATUS=%errorlevel%

if %DEPS_STATUS% neq 0 (
    echo.
    echo ================================================================
    echo.
    set /p DEMO="Do you want to run in DEMO mode? (y/n): "

    if /i "%DEMO%"=="y" (
        echo.
        echo Starting GUI DEMO mode...
        echo.
        python dcdc_monitor_demo.py
    ) else if /i "%DEMO%"=="Y" (
        echo.
        echo Starting GUI DEMO mode...
        echo.
        python dcdc_monitor_demo.py
    ) else (
        echo.
        echo Please install dependencies first:
        echo   pip install python-can cantools
        echo.
        echo Or run manually:
        echo   python dcdc_monitor_demo.py  (demo mode)
        echo   python dcdc_monitor_cli.py   (terminal mode)
        pause
        exit /b 1
    )
) else (
    echo.
    echo Starting DC-DC Monitor (full version)...
    echo.
    python dcdc_monitor.py
)

echo.
echo Application closed.
pause

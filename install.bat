@echo off

rem Set project root directory
set "PROJECT_ROOT=%~dp0"
set "VENV_DIR=%PROJECT_ROOT%backend\venv"

rem Check if Python is installed
echo Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python not found, please install Python 3.8+ first
    pause
    exit /b 1
)

echo Starting installation of Autonomous Decision Agent project...

rem Remove old virtual environment if it exists
if exist "%VENV_DIR%" (
    echo Removing old virtual environment...
    rmdir /s /q "%VENV_DIR%"
    if %errorlevel% neq 0 (
        echo Warning: Failed to remove old virtual environment, continuing execution
    )
)

rem Create virtual environment
echo Creating virtual environment...
python -m venv "%VENV_DIR%"
if %errorlevel% neq 0 (
    echo Error: Failed to create virtual environment
    pause
    exit /b 1
)

rem Set Python and pip executables paths
set "PYTHON_EXE=%VENV_DIR%\Scripts\python.exe"
set "PIP_EXE=%VENV_DIR%\Scripts\pip.exe"

rem Activate virtual environment
echo Activating virtual environment...
call "%VENV_DIR%\Scripts\activate.bat"
if %errorlevel% neq 0 (
    echo Error: Failed to activate virtual environment
    pause
    exit /b 1
)

rem Upgrade pip
echo Upgrading pip...
%PYTHON_EXE% -m pip install --upgrade --no-cache-dir pip
if %errorlevel% neq 0 (
    echo Warning: Failed to upgrade pip, continuing execution
)

rem Install Python dependencies
echo Installing Python dependencies (without cache)...
%PIP_EXE% install --no-cache-dir -r "%PROJECT_ROOT%backend\requirements.txt"
if %errorlevel% neq 0 (
    echo Error: Failed to install Python dependencies
    pause
    exit /b 1
)

rem Check if frontend directory exists
if exist "%PROJECT_ROOT%frontend" (
    echo Installing frontend dependencies...
    cd "%PROJECT_ROOT%frontend"
    
    rem Check if npm is installed
    npm --version >nul 2>&1
    if %errorlevel% neq 0 (
        echo Warning: npm not found, skipping frontend dependency installation
    ) else (
        echo Installing npm dependencies (without cache)...
        npm install --no-cache
        if %errorlevel% neq 0 (
            echo Warning: Failed to install frontend dependencies, continuing execution
        )
    )
    
    cd "%PROJECT_ROOT%"
)

rem Installation complete
echo Installation completed!
echo Project has been successfully installed, you can use start.bat script to start the project
echo Press any key to exit...
pause >nul
exit /b 0
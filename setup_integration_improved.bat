@echo off
setlocal enabledelayedexpansion

echo ===============================================
echo  RingCentral-Zoho CRM Integration Setup Script
echo ===============================================
echo.
echo This script will set up the RingCentral-Zoho CRM integration.
echo It will:
echo  - Check Python installation
echo  - Create necessary directories
echo  - Install required dependencies
echo  - Set up configuration files
echo  - Create run scripts
echo.
echo Press Ctrl+C to cancel or any key to continue...
pause > nul

:: Create base directories
echo.
echo Creating directories...
mkdir core 2>nul
mkdir core\data 2>nul
mkdir core\logs 2>nul
mkdir core\logs\reports 2>nul
mkdir core\scripts 2>nul
mkdir core\utils 2>nul
mkdir core\source 2>nul
mkdir core\sorted 2>nul
mkdir core\sorted\data 2>nul
mkdir core\sorted\utils 2>nul
mkdir core\scheduling 2>nul
mkdir core\documentation 2>nul
mkdir core\documentation\research 2>nul

:: Check Python installation
echo.
echo Checking Python installation...
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH.
    echo Please install Python 3.8 or higher from https://www.python.org/downloads/
    echo and make sure it's added to your PATH.
    pause
    exit /b 1
)

:: Set up virtual environment
echo.
echo Setting up virtual environment...
if not exist core\venv (
    python -m venv core\venv
    if %errorlevel% neq 0 (
        echo ERROR: Failed to create virtual environment.
        echo Please make sure you have the venv module installed.
        pause
        exit /b 1
    )
)

:: Activate virtual environment and install dependencies
echo.
echo Installing required packages...
call core\venv\Scripts\activate.bat
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo WARNING: Failed to install some dependencies.
    echo You may need to install them manually.
    echo See requirements.txt for the list of required packages.
)

:: Clone the repository from GitHub
echo.
echo Cloning files from GitHub repository...
git --version > nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Git is not installed or not in PATH.
    echo Please install Git from https://git-scm.com/downloads
    echo and make sure it's added to your PATH.
    pause
    exit /b 1
)

git clone https://github.com/inimical023/rc_zoho_public.git temp_repo
if %errorlevel% neq 0 (
    echo ERROR: Failed to clone repository.
    echo Please check your internet connection and try again.
    pause
    exit /b 1
)

:: Copy files from the cloned repository
echo.
echo Setting up core files...
copy /Y temp_repo\*.py core\
copy /Y temp_repo\README.md .

:: Copy configuration files
echo.
echo Setting up configuration files...
copy /Y temp_repo\data\*.json core\data\
mkdir core\sorted\data 2>nul
copy /Y temp_repo\sorted\data\*.json core\sorted\data\

:: Set up Philadelphia office files
echo.
echo Setting up Philadelphia office configuration...
mkdir core\sorted\philadelphia 2>nul
copy /Y temp_repo\sorted\philadelphia\*.json core\sorted\philadelphia\

:: Clean up temporary repository
rmdir /S /Q temp_repo

:: Create PYTHONPATH file to help imports work
echo.
echo Setting up Python path configuration...
echo %CD%\core > core\venv\Lib\site-packages\rc_zoho.pth

:: Create batch files for running scripts
echo.
echo Creating run scripts...

:: Setup credentials script
echo @echo off > run_setup_credentials.bat
echo call core\venv\Scripts\activate.bat >> run_setup_credentials.bat
echo cd core >> run_setup_credentials.bat
echo python setup_credentials.py %* >> run_setup_credentials.bat
echo pause >> run_setup_credentials.bat

:: Accepted calls script
echo @echo off > run_accepted_calls.bat
echo call core\venv\Scripts\activate.bat >> run_accepted_calls.bat
echo cd core >> run_accepted_calls.bat
echo python accepted_calls.py %* >> run_accepted_calls.bat
echo pause >> run_accepted_calls.bat

:: Missed calls script
echo @echo off > run_missed_calls.bat
echo call core\venv\Scripts\activate.bat >> run_missed_calls.bat
echo cd core >> run_missed_calls.bat
echo python missed_calls.py %* >> run_missed_calls.bat
echo pause >> run_missed_calls.bat

:: Single company all calls with report script
echo @echo off > run_single_company_all_calls_with_report.bat
echo call core\venv\Scripts\activate.bat >> run_single_company_all_calls_with_report.bat
echo cd core >> run_single_company_all_calls_with_report.bat
echo python scripts\run_all_reports.py --office singlecompany %* >> run_single_company_all_calls_with_report.bat
echo pause >> run_single_company_all_calls_with_report.bat

:: Multi-location all calls with report ordered script
echo @echo off > run_multi_location_all_calls_with_report_ordered.bat
echo call core\venv\Scripts\activate.bat >> run_multi_location_all_calls_with_report_ordered.bat
echo cd core >> run_multi_location_all_calls_with_report_ordered.bat
echo python scripts\run_all_reports.py --all-offices --ordered %* >> run_multi_location_all_calls_with_report_ordered.bat
echo pause >> run_multi_location_all_calls_with_report_ordered.bat

:: Admin interface launch script
echo @echo off > launch_admin.bat
echo call core\venv\Scripts\activate.bat >> launch_admin.bat
echo cd core >> launch_admin.bat
echo python unified_admin.py %* >> launch_admin.bat

:: Requirements file
echo.
echo Creating requirements.txt...
echo cryptography==41.0.1 > requirements.txt
echo python-dateutil==2.8.2 >> requirements.txt
echo pytz==2023.3 >> requirements.txt
echo requests==2.31.0 >> requirements.txt
echo ttkbootstrap==1.10.1 >> requirements.txt
echo tkcalendar==1.6.1 >> requirements.txt
echo phonenumbers==8.13.11 >> requirements.txt
echo beautifulsoup4==4.12.2 >> requirements.txt
echo matplotlib==3.7.1 >> requirements.txt
echo Pillow==10.0.0 >> requirements.txt

:: Final steps
echo.
echo ===============================================
echo  Setup completed successfully!
echo ===============================================
echo.
echo Next steps:
echo  1. Run 'run_setup_credentials.bat' to configure your API credentials
echo  2. Customize the office configurations in core\sorted\
echo  3. Run 'launch_admin.bat' to access the admin interface
echo  4. Or run one of the processing scripts directly:
echo     - run_accepted_calls.bat
echo     - run_missed_calls.bat
echo     - run_single_company_all_calls_with_report.bat
echo     - run_multi_location_all_calls_with_report_ordered.bat
echo.
echo Documentation is available in the README.md file.
echo.
pause

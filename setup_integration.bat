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
echo requests-file==1.5.1 >> requirements.txt

:: Activate virtual environment and install dependencies
echo.
echo Installing required packages...
call core\venv\Scripts\activate.bat
python -m pip install --upgrade pip

echo.
echo Installing dependencies from requirements.txt...
if exist requirements.txt (
    python -m pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to install some package dependencies.
        echo Please check the error messages above to identify the specific packages.
        echo You may need to install them manually or resolve the issues.
    )
) else (
    echo [WARNING] requirements.txt not found.
    echo Creating base requirements file...
    python -m pip install cryptography python-dateutil pytz requests ttkbootstrap tkcalendar phonenumbers beautifulsoup4 matplotlib pillow requests-file
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to install some basic dependencies.
        echo Please check the error messages above to identify the specific packages.
    )
)

:: Try to Clone repository using Git if available
echo.
echo Attempting to download files from GitHub repository...
git --version > nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] Git is not installed. Falling back to direct download...
    
    :: Test for PowerShell availability directly
    echo Testing PowerShell availability...
    
    mkdir temp_dir 2>nul
    powershell -Command "Write-Host 'PowerShell is available'" > temp_dir\ps_test.txt 2>&1
    if not exist temp_dir\ps_test.txt (
        echo [ERROR] PowerShell test file creation failed.
    )
    
    set PS_AVAILABLE=0
    findstr /C:"PowerShell is available" temp_dir\ps_test.txt > nul 2>&1
    if %errorlevel% equ 0 (
        set PS_AVAILABLE=1
        echo PowerShell is available and working.
    ) else (
        echo [WARNING] PowerShell may be installed but not working properly.
        type temp_dir\ps_test.txt
    )
    rmdir /S /Q temp_dir 2>nul
    
    if %PS_AVAILABLE% equ 0 (
        echo [ERROR] Cannot use PowerShell for download. Please install Git or download manually.
        echo Please install Git from https://git-scm.com/downloads
        echo or download the files manually from https://github.com/inimical023/rc_zoho_public
        pause
        exit /b 1
    )
    
    echo Using PowerShell to download repository as ZIP file...
    mkdir temp_repo 2>nul
    
    :: Create and run a PowerShell script for downloading
    echo [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; > download_repo.ps1
    echo try { >> download_repo.ps1
    echo   Invoke-WebRequest -Uri 'https://github.com/inimical023/rc_zoho_public/archive/refs/heads/master.zip' -OutFile 'repo.zip' >> download_repo.ps1
    echo   Write-Host "Download successful" >> download_repo.ps1
    echo } catch { >> download_repo.ps1
    echo   Write-Host "Error: $_" >> download_repo.ps1
    echo   exit 1 >> download_repo.ps1
    echo } >> download_repo.ps1
    
    powershell -ExecutionPolicy Bypass -File download_repo.ps1
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to download repository using PowerShell.
        echo Please check your internet connection or download manually from:
        echo https://github.com/inimical023/rc_zoho_public
        pause
        exit /b 1
    )
    del download_repo.ps1
    
    :: Extract ZIP file if available
    if exist repo.zip (
        echo Extracting repository files...
        powershell -Command "& {Add-Type -AssemblyName System.IO.Compression.FileSystem; [System.IO.Compression.ZipFile]::ExtractToDirectory('repo.zip', 'temp_extract')}"
        if %errorlevel% neq 0 (
            echo [ERROR] Failed to extract ZIP file.
            echo Please download and extract manually from:
            echo https://github.com/inimical023/rc_zoho_public
            pause
            exit /b 1
        )
        
        echo Moving files from ZIP extract...
        xcopy /E /Y temp_extract\rc_zoho_public-master\* temp_repo\
        if %errorlevel% neq 0 (
            echo [ERROR] Failed to copy extracted files.
            pause
            exit /b 1
        )
        
        :: Clean up extraction directory
        rmdir /S /Q temp_extract
        del repo.zip
    )
) else (
    echo Git is installed, cloning repository...
    git clone https://github.com/inimical023/rc_zoho_public.git temp_repo
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to clone repository with Git.
        echo Please check your internet connection and try again.
        pause
        exit /b 1
    )
    echo Repository cloned successfully.
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

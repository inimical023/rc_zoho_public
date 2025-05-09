#!/bin/bash

echo "==============================================="
echo " RingCentral-Zoho CRM Integration Setup Script"
echo "==============================================="
echo ""
echo "This script will set up the RingCentral-Zoho CRM integration."
echo "It will:"
echo " - Check Python installation"
echo " - Create necessary directories"
echo " - Install required dependencies"
echo " - Set up configuration files"
echo " - Create run scripts"
echo ""
echo "Press Ctrl+C to cancel or Enter to continue..."
read

# Create base directories
echo ""
echo "Creating directories..."
mkdir -p core/data
mkdir -p core/logs/reports
mkdir -p core/scripts
mkdir -p core/utils
mkdir -p core/source
mkdir -p core/sorted/data
mkdir -p core/sorted/utils
mkdir -p core/scheduling
mkdir -p core/documentation/research

# Check Python installation
echo ""
echo "Checking Python installation..."
if ! python3 --version &> /dev/null; then
    echo "ERROR: Python 3 is not installed or not in PATH."
    echo "Please install Python 3.8 or higher from your package manager"
    echo "or https://www.python.org/downloads/"
    exit 1
fi

# Set up virtual environment
echo ""
echo "Setting up virtual environment..."
if [ ! -d "core/venv" ]; then
    python3 -m venv core/venv
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to create virtual environment."
        echo "Please make sure you have the venv module installed."
        echo "Try: sudo apt-get install python3-venv (Ubuntu/Debian)"
        echo "or: sudo dnf install python3-venv (Fedora/CentOS)"
        exit 1
    fi
fi

# Requirements file
echo ""
echo "Creating requirements.txt..."
cat > requirements.txt << EOF
cryptography==41.0.1
python-dateutil==2.8.2
pytz==2023.3
requests==2.31.0
ttkbootstrap==1.10.1
tkcalendar==1.6.1
phonenumbers==8.13.11
beautifulsoup4==4.12.2
matplotlib==3.7.1
Pillow==10.0.0
requests-file==1.5.1
EOF

# Activate virtual environment and install dependencies
echo ""
echo "Installing required packages..."
source core/venv/bin/activate
python -m pip install --upgrade pip

echo ""
echo "Installing dependencies from requirements.txt..."
if [ -f requirements.txt ]; then
    python -m pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "[ERROR] Failed to install some package dependencies."
        echo "Please check the error messages above to identify the specific packages."
        echo "You may need to install them manually or resolve the issues."
    fi
else
    echo "[WARNING] requirements.txt not found."
    echo "Creating base requirements file..."
    python -m pip install cryptography python-dateutil pytz requests ttkbootstrap tkcalendar phonenumbers beautifulsoup4 matplotlib pillow requests-file
    if [ $? -ne 0 ]; then
        echo "[ERROR] Failed to install some basic dependencies."
        echo "Please check the error messages above to identify the specific packages."
    fi
fi

# Attempt to install Git if not available, or use existing Git installation
echo ""
echo "Checking Git installation..."
if ! git --version &> /dev/null; then
    echo "[INFO] Git is not installed. Attempting to install Git..."

    # Detect the Linux distribution and package manager
    if command -v apt-get &> /dev/null; then
        echo "Debian/Ubuntu detected, using apt-get to install Git..."
        sudo apt-get update
        sudo apt-get install -y git
    elif command -v dnf &> /dev/null; then
        echo "Fedora/RHEL detected, using dnf to install Git..."
        sudo dnf install -y git
    elif command -v yum &> /dev/null; then
        echo "CentOS/RHEL detected, using yum to install Git..."
        sudo yum install -y git
    elif command -v pacman &> /dev/null; then
        echo "Arch Linux detected, using pacman to install Git..."
        sudo pacman -Sy --noconfirm git
    elif command -v zypper &> /dev/null; then
        echo "openSUSE detected, using zypper to install Git..."
        sudo zypper install -y git
    elif command -v apk &> /dev/null; then
        echo "Alpine Linux detected, using apk to install Git..."
        sudo apk add git
    else
        echo "[WARNING] Could not detect package manager to install Git automatically."
        echo "Please install Git manually using your distribution's package manager."
    fi

    # Check if Git was installed successfully
    if git --version &> /dev/null; then
        echo "Git was installed successfully!"
    else
        echo "[INFO] Git still not available. Falling back to direct download..."
    
    # Check for curl or wget
    if command -v curl &> /dev/null; then
        echo "Using curl to download repository as ZIP file..."
        mkdir -p temp_extract
        curl -L https://github.com/inimical023/rc_zoho_public/archive/refs/heads/master.zip -o repo.zip
        if [ $? -ne 0 ]; then
            echo "[ERROR] Failed to download repository with curl."
            echo "Please check your internet connection or download manually from:"
            echo "https://github.com/inimical023/rc_zoho_public"
            exit 1
        fi
    elif command -v wget &> /dev/null; then
        echo "Using wget to download repository as ZIP file..."
        mkdir -p temp_extract
        wget https://github.com/inimical023/rc_zoho_public/archive/refs/heads/master.zip -O repo.zip
        if [ $? -ne 0 ]; then
            echo "[ERROR] Failed to download repository with wget."
            echo "Please check your internet connection or download manually from:"
            echo "https://github.com/inimical023/rc_zoho_public"
            exit 1
        fi
    else
        echo "[ERROR] Neither Git, curl, nor wget is available."
        echo "Please install Git using your package manager:"
        echo "  - For Ubuntu/Debian: sudo apt install git"
        echo "  - For Fedora/CentOS/RHEL: sudo dnf install git"
        echo "Or download the files manually from: https://github.com/inimical023/rc_zoho_public"
        exit 1
    fi
    
    # Extract ZIP file
    if [ -f repo.zip ]; then
        echo "Extracting repository files..."
        if command -v unzip &> /dev/null; then
            unzip -q repo.zip -d temp_extract
            if [ $? -ne 0 ]; then
                echo "[ERROR] Failed to extract ZIP file."
                echo "Please install unzip or download and extract manually from:"
                echo "https://github.com/inimical023/rc_zoho_public"
                exit 1
            fi
            
            mkdir -p temp_repo
            echo "Moving files from ZIP extract..."
            cp -r temp_extract/rc_zoho_public-master/* temp_repo/
            if [ $? -ne 0 ]; then
                echo "[ERROR] Failed to copy extracted files."
                exit 1
            fi
            
            # Clean up extraction directory
            rm -rf temp_extract
            rm repo.zip
        else
            echo "[ERROR] unzip command not available to extract the downloaded file."
            echo "Please install unzip using your package manager:"
            echo "  - For Ubuntu/Debian: sudo apt install unzip"
            echo "  - For Fedora/CentOS/RHEL: sudo dnf install unzip"
            exit 1
        fi
    fi
else
    echo "Git is installed, cloning repository..."
    git clone https://github.com/inimical023/rc_zoho_public.git temp_repo
    if [ $? -ne 0 ]; then
        echo "[ERROR] Failed to clone repository with Git."
        echo "Please check your internet connection and try again."
        exit 1
    fi
    echo "Repository cloned successfully."
fi

# Copy files from the cloned repository
echo ""
echo "Setting up core files..."
cp -v temp_repo/*.py core/
cp -v temp_repo/README.md .

# Copy configuration files
echo ""
echo "Setting up configuration files..."
cp -v temp_repo/data/*.json core/data/
mkdir -p core/sorted/data
cp -v temp_repo/sorted/data/*.json core/sorted/data/

# Set up Philadelphia office files
echo ""
echo "Setting up Philadelphia office configuration..."
mkdir -p core/sorted/philadelphia
cp -v temp_repo/sorted/philadelphia/*.json core/sorted/philadelphia/

# Clean up temporary repository
rm -rf temp_repo

# Create PYTHONPATH file to help imports work
echo ""
echo "Setting up Python path configuration..."
mkdir -p core/venv/lib/python3.8/site-packages
echo "$(pwd)/core" > core/venv/lib/python3.8/site-packages/rc_zoho.pth

# Create shell scripts for running commands
echo ""
echo "Creating run scripts..."

# Setup credentials script
cat > run_setup_credentials.sh << EOF
#!/bin/bash
source core/venv/bin/activate
cd core
python setup_credentials.py "\$@"
EOF
chmod +x run_setup_credentials.sh

# Accepted calls script
cat > run_accepted_calls.sh << EOF
#!/bin/bash
source core/venv/bin/activate
cd core
python accepted_calls.py "\$@"
EOF
chmod +x run_accepted_calls.sh

# Missed calls script
cat > run_missed_calls.sh << EOF
#!/bin/bash
source core/venv/bin/activate
cd core
python missed_calls.py "\$@"
EOF
chmod +x run_missed_calls.sh

# Single company all calls with report script
cat > run_single_company_all_calls_with_report.sh << EOF
#!/bin/bash
source core/venv/bin/activate
cd core
python scripts/run_all_reports.py --office singlecompany "\$@"
EOF
chmod +x run_single_company_all_calls_with_report.sh

# Multi-location all calls with report ordered script
cat > run_multi_location_all_calls_with_report_ordered.sh << EOF
#!/bin/bash
source core/venv/bin/activate
cd core
python scripts/run_all_reports.py --all-offices --ordered "\$@"
EOF
chmod +x run_multi_location_all_calls_with_report_ordered.sh

# Admin interface launch script
cat > launch_admin.sh << EOF
#!/bin/bash
source core/venv/bin/activate
cd core
python unified_admin.py "\$@"
EOF
chmod +x launch_admin.sh


# Final steps
echo ""
echo "==============================================="
echo " Setup completed successfully!"
echo "==============================================="
echo ""
echo "Next steps:"
echo " 1. Run './run_setup_credentials.sh' to configure your API credentials"
echo " 2. Customize the office configurations in core/sorted/"
echo " 3. Run './launch_admin.sh' to access the admin interface"
echo " 4. Or run one of the processing scripts directly:"
echo "    - ./run_accepted_calls.sh"
echo "    - ./run_missed_calls.sh"
echo "    - ./run_single_company_all_calls_with_report.sh"
echo "    - ./run_multi_location_all_calls_with_report_ordered.sh"
echo ""
echo "Documentation is available in the README.md file."
echo ""

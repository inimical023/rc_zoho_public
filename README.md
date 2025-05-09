# RingCentral-Zoho CRM Integration

[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/downloads/)

A powerful integration tool that automates the synchronization of call data between RingCentral's telephony platform and Zoho CRM. This integration processes both accepted and missed calls, attaches call recordings and voicemails, and creates/updates leads in Zoho CRM.

## Features

- **Accepted Calls Processing**: Processes calls marked as "Accepted" in RingCentral and creates or updates leads in Zoho CRM.
- **Missed Calls Processing**: Handles missed calls from RingCentral, with special attention to those that include voicemail recordings.
- **Recording Attachment**: Attaches call recordings and voicemail recordings to lead records in Zoho CRM.
- **Multi-Office Support**: Processes call data for multiple office locations with customizable processing order.
- **Single Company Mode**: Simpler configuration for organizations with just one location.
- **Configurable Lead Assignment**: Round-robin assignment of leads to lead owners with support for weighted distribution.
- **Email Reporting**: Generates and sends HTML email reports after processing.
- **Unified Admin Interface**: Graphical user interface for managing the integration.

## Table of Contents

- [Requirements](#requirements)
- [Quick Start](#quick-start)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Architecture](#architecture)
- [Advanced Configuration](#advanced-configuration)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

## Requirements

- Python 3.8 or higher
- RingCentral API credentials (JWT auth)
- Zoho CRM API credentials (OAuth2)
- Windows or Linux environment (Windows preferred for batch script support)

## Quick Start

1. Clone this repository:
   ```bash
   git clone https://github.com/yourorganization/ringcentral-zoho.git
   cd ringcentral-zoho
   ```

2. Run the setup script:
   ```bash
   setup_integration_improved.bat
   ```

3. Follow the prompts to configure your API credentials.

4. Launch the admin interface:
   ```bash
   launch_admin.bat
   ```

## Installation

### Windows Installation

1. Run the setup script:
   ```
   setup_integration_improved.bat
   ```

   This will:
   - Create necessary directories
   - Set up a Python virtual environment
   - Install required dependencies
   - Copy configuration files
   - Create run scripts

2. Configure your API credentials:
   ```
   run_setup_credentials.bat
   ```

3. Customize your office configuration in the `data/` (single company) or `sorted/` (multi-company) directories.

### Linux Installation

1. Make the setup script executable:
   ```bash
   chmod +x setup_integration_improved.sh
   ```

2. Run the setup script:
   ```bash
   ./setup_integration_improved.sh
   ```

3. Configure your API credentials:
   ```bash
   ./run_setup_credentials.sh
   ```

## Configuration

### API Credentials

You'll need to configure credentials for both RingCentral and Zoho CRM:

#### RingCentral
- Client ID
- Client Secret
- JWT Private Key

#### Zoho CRM
- Client ID
- Client Secret
- Refresh Token

These are configured during the setup process and stored securely using encryption.

### Office Configuration

For multi-company setups, configure each office in the `sorted/` directory:

1. `sorted/data/offices.json`: Define your office locations and processing order
2. `sorted/<office>/extensions.json`: Configure RingCentral extensions for each office
3. `sorted/<office>/lead_owners.json`: Configure Zoho CRM lead owners for each office

For single-company setups, use:
1. `data/extensions.json`
2. `data/lead_owners.json`

### Field Mappings

Configure how RingCentral call data maps to Zoho CRM fields in `data/zoho_field_mappings.json`.

### Email Reports

Configure email notifications in `data/email_config.json`.

## Usage

### Unified Admin Interface

Launch the graphical admin interface:
```
launch_admin.bat
```

The admin interface provides:
- Call processing configuration
- Credential management
- Report viewing
- Office configuration

### Command Line Usage

Process accepted calls:
```
run_accepted_calls.bat --office <office_id> [--hours-back <hours>] [--dry-run] [--debug]
```

Process missed calls:
```
run_missed_calls.bat --office <office_id> [--hours-back <hours>] [--dry-run] [--debug]
```

Process both call types with report (single company):
```
run_single_company_all_calls_with_report.bat [--hours-back <hours>] [--dry-run] [--debug]
```

Process both call types with report (multi-company):
```
run_multi_location_all_calls_with_report_ordered.bat [--hours-back <hours>] [--dry-run] [--debug]
```

### Scheduling

For automatic processing, set up scheduled tasks (Windows) or cron jobs (Linux):

#### Windows Task Scheduler
```powershell
schtasks /create /tn "RingCentral-Zoho Integration" /tr "C:\path\to\run_multi_location_all_calls_with_report_ordered.bat" /sc DAILY /st 08:00
```

#### Linux Cron Job
```bash
0 8 * * * /path/to/run_multi_location_all_calls_with_report_ordered.sh
```

## Architecture

The integration follows a modular architecture:

- **Core Modules**:
  - `common.py`: Base functionality with client classes for RingCentral and Zoho
  - `accepted_calls.py`: Processes accepted calls and creates/updates leads
  - `missed_calls.py`: Processes missed calls with special handling for voicemails

- **Security**:
  - `secure_credentials.py`: Handles encryption/decryption of API credentials
  - `setup_credentials.py`: Interactive credential setup script

- **User Interface**:
  - `unified_admin.py`: GUI admin interface for managing the integration

- **Configuration Files**:
  - JSON config files for field mappings, email settings, offices, etc.

Key design patterns used:
- Circuit breaker pattern for API resilience
- Repository pattern for data access
- Factory pattern for client creation
- Strategy pattern for processing different call types

## Advanced Configuration

### Custom Field Mappings

For custom Zoho CRM fields, modify `data/zoho_field_mappings.json`:

```json
{
  "accepted_calls": {
    "Phone": "Phone",
    "Custom_Field": "Custom_Zoho_Field"
  }
}
```

### Lead Assignment Rules

Configure advanced lead assignment in the lead_owners.json files:

```json
{
  "assignment_rules": {
    "round_robin": true,
    "respect_weights": true,
    "fallback_owner_id": "5678901234",
    "office_hours_only": true,
    "department_specific": {
      "enabled": true,
      "mappings": {
        "Sales": ["owner1_id", "owner2_id"],
        "Support": ["owner3_id", "owner4_id"]
      }
    }
  }
}
```

## Troubleshooting

Common issues and solutions:

### API Authentication Errors
- Ensure credentials are correctly configured with `run_setup_credentials.bat`
- Check log files in `logs/` directory
- Verify API keys are still valid in RingCentral and Zoho consoles

### Call Processing Issues
- Use `--debug` flag for more detailed logging
- Use `--dry-run` flag to test without making changes to Zoho CRM
- Check extension and lead owner configurations

### Email Report Problems
- Verify SMTP settings in `data/email_config.json`
- Ensure the email account allows sending through SMTP
- Check firewall settings if emails aren't being sent

For more information, see the [troubleshooting guide](docs/troubleshooting.md).

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit your changes: `git commit -am 'Add some feature'`
4. Push to the branch: `git push origin feature-name`
5. Submit a pull request

For major changes, please open an issue first to discuss what you would like to change.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- RingCentral API documentation: https://developers.ringcentral.com/api-reference
- Zoho CRM API documentation: https://www.zoho.com/crm/developer/docs/api/

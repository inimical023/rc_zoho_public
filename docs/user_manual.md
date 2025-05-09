# RingCentral-Zoho CRM Integration
# User Manual

## Table of Contents

1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
   - [System Requirements](#system-requirements)
   - [Installation](#installation)
   - [Initial Configuration](#initial-configuration)
3. [Understanding the Integration](#understanding-the-integration)
   - [Call Processing Flow](#call-processing-flow)
   - [Lead Management](#lead-management)
   - [Recording and Voicemail Handling](#recording-and-voicemail-handling)
4. [Using the Admin Interface](#using-the-admin-interface)
   - [Dashboard](#dashboard)
   - [Processing Tab](#processing-tab)
   - [Configuration Tab](#configuration-tab)
   - [Reports Tab](#reports-tab)
5. [Command Line Usage](#command-line-usage)
   - [Basic Commands](#basic-commands)
   - [Common Options](#common-options)
   - [Examples](#examples)
6. [Configuration Files](#configuration-files)
   - [API Credentials](#api-credentials)
   - [Office Configuration](#office-configuration)
   - [Extensions](#extensions)
   - [Lead Owners](#lead-owners)
   - [Field Mappings](#field-mappings)
   - [Email Settings](#email-settings)
7. [Automated Scheduling](#automated-scheduling)
   - [Windows Task Scheduler](#windows-task-scheduler)
   - [Linux Cron Jobs](#linux-cron-jobs)
8. [Reports and Monitoring](#reports-and-monitoring)
   - [Email Reports](#email-reports)
   - [Log Files](#log-files)
   - [Performance Monitoring](#performance-monitoring)
9. [Troubleshooting](#troubleshooting)
   - [Common Issues](#common-issues)
   - [Diagnostic Steps](#diagnostic-steps)
   - [Error Reference](#error-reference)
10. [Security Considerations](#security-considerations)
    - [Encryption](#encryption)
    - [API Permissions](#api-permissions)
    - [Best Practices](#best-practices)
11. [Advanced Usage](#advanced-usage)
    - [Custom Field Mappings](#custom-field-mappings)
    - [Advanced Lead Assignment](#advanced-lead-assignment)
    - [Multiple Environments](#multiple-environments)
12. [Appendices](#appendices)
    - [API Rate Limits](#api-rate-limits)
    - [Version History](#version-history)
    - [Glossary](#glossary)

## Introduction

The RingCentral-Zoho CRM Integration automatically synchronizes call data from RingCentral to Zoho CRM. It processes both accepted and missed calls, creating or updating leads in Zoho CRM and attaching call recordings and voicemails.

This user manual provides comprehensive guidance on how to install, configure, and operate the integration.

## Getting Started

### System Requirements

- **Operating System**: Windows 10/11 or Linux (Ubuntu 20.04+, CentOS 7+)
- **Python**: Version 3.8 or higher
- **Memory**: Minimum 4GB RAM (8GB recommended)
- **Disk Space**: Minimum 500MB free space
- **Network**: Internet access to RingCentral and Zoho APIs
- **API Access**:
  - RingCentral Admin access with API permissions
  - Zoho CRM Admin access with API permissions

### Installation

#### Windows Installation

1. Download the release or clone the repository
2. Run `setup_integration_improved.bat`
3. Follow on-screen prompts
4. Configure API credentials using `run_setup_credentials.bat`

#### Linux Installation

1. Download the release or clone the repository
2. Make the setup script executable: `chmod +x setup_integration_improved.sh`
3. Run setup: `./setup_integration_improved.sh`
4. Configure API credentials: `./run_setup_credentials.sh`

### Initial Configuration

After installation, you'll need to configure:

1. **API Credentials**:
   - Run `run_setup_credentials.bat` (Windows) or `./run_setup_credentials.sh` (Linux)
   - Follow the prompts to enter your RingCentral and Zoho CRM API credentials

2. **Office Configuration**:
   - For single company: Edit `data/extensions.json` and `data/lead_owners.json`
   - For multi-company: Edit files in the `sorted/` directory structure

3. **Email Reports**:
   - Edit `data/email_config.json` to configure SMTP settings for email reporting

4. **Field Mappings**:
   - Optionally customize `data/zoho_field_mappings.json` if you have custom fields in Zoho CRM

After completing these steps, the integration is ready to use.

## Understanding the Integration

### Call Processing Flow

The integration follows this general processing flow:

1. **Call Data Retrieval**:
   - Retrieves call logs from RingCentral API for configured extensions
   - Filters calls by type (accepted/missed) and time range

2. **Call Processing**:
   - Extracts caller information (phone number, name if available)
   - Determines if the call should be processed based on configuration

3. **Zoho CRM Integration**:
   - Searches for existing leads by phone number
   - Creates new leads or updates existing ones
   - Adds notes with call details

4. **Media Attachment**:
   - Retrieves call recordings for accepted calls if available
   - Retrieves voicemail recordings for missed calls if available
   - Attaches media files to lead records in Zoho CRM

5. **Reporting**:
   - Generates processing statistics
   - Creates HTML reports
   - Sends email notifications if configured

### Lead Management

The integration manages leads in Zoho CRM as follows:

- **New Leads**: Created when a caller is not found in Zoho CRM
  - Assigned to a lead owner based on configuration (round-robin)
  - Basic information populated from call data
  - Lead source set to "RingCentral Integration"

- **Existing Leads**: Updated when a caller is found in Zoho CRM
  - Notes added with call details
  - Recording/voicemail attached if available
  - Status updated based on call type

### Recording and Voicemail Handling

Call recordings and voicemails are:

1. Retrieved from RingCentral API
2. Temporarily stored locally (encrypted)
3. Uploaded to Zoho CRM as attachments to the lead
4. Removed from local storage after processing

## Using the Admin Interface

Launch the admin interface using:
```
launch_admin.bat
```

### Dashboard

The Dashboard provides an overview of the integration status:

- **Credentials Status**: Shows if RingCentral and Zoho CRM credentials are configured
- **Quick Actions**: Buttons for common operations
- **Processing Statistics**: Overview of recent processing results

### Processing Tab

The Processing Tab allows you to run call processing operations:

1. Select an office from the dropdown
2. Set the hours to look back for call data
3. Configure processing options (dry run, debug mode)
4. Select call types to process (accepted calls, missed calls)
5. Click "Run Processing" to start
6. View real-time output in the console area

### Configuration Tab

The Configuration Tab provides access to configuration files:

- **Offices**: Configure office locations and processing order
- **Extensions**: Manage RingCentral extensions
- **Lead Owners**: Configure Zoho CRM lead owners and assignment rules
- **Field Mappings**: Customize how call data maps to Zoho CRM fields

### Reports Tab

The Reports Tab lists available processing reports:

- View a list of generated HTML reports
- Select a report to view it in your browser
- Refresh the list to see new reports

## Command Line Usage

For automated operations or advanced users, command-line scripts are available.

### Basic Commands

- **Process Accepted Calls**:
  ```
  run_accepted_calls.bat --office <office_id>
  ```

- **Process Missed Calls**:
  ```
  run_missed_calls.bat --office <office_id>
  ```

- **Process All Call Types (Single Company)**:
  ```
  run_single_company_all_calls_with_report.bat
  ```

- **Process All Call Types (Multi-Company)**:
  ```
  run_multi_location_all_calls_with_report_ordered.bat
  ```

### Common Options

All command-line scripts support these options:

- `--hours-back <hours>`: Number of hours to look back for calls (default: 24)
- `--dry-run`: Run without making changes to Zoho CRM
- `--debug`: Enable detailed debug logging
- `--no-email`: Skip sending email reports

### Examples

Process the last 48 hours of calls for the Philadelphia office:
```
run_accepted_calls.bat --office philadelphia --hours-back 48
```

Test processing without making changes:
```
run_missed_calls.bat --office pittsburgh --dry-run
```

Process all offices with detailed logging:
```
run_multi_location_all_calls_with_report_ordered.bat --debug
```

## Configuration Files

### API Credentials

API credentials are stored in encrypted format:

- `data/credentials.enc`: Encrypted credentials file
- `data/encryption.key`: Encryption key

To update credentials, run:
```
run_setup_credentials.bat
```

### Office Configuration

For multi-company setups, configure offices in:
```
sorted/data/offices.json
```

Example structure:
```json
{
  "offices": {
    "philadelphia": {
      "name": "Philadelphia Office",
      "processing_order": 1,
      "timezone": "America/New_York"
    },
    "pittsburgh": {
      "name": "Pittsburgh Office",
      "processing_order": 2,
      "timezone": "America/New_York"
    }
  },
  "global_config": {
    "default_timezone": "America/New_York",
    "processing": {
      "default_hours_back": 24,
      "max_hours_back": 168
    }
  }
}
```

### Extensions

RingCentral extensions are configured in:
- Single company: `data/extensions.json`
- Multi-company: `sorted/<office>/extensions.json`

Example:
```json
{
  "extensions": [
    {
      "id": "101",
      "name": "Reception",
      "type": "Department",
      "number": "1001",
      "process_calls": true
    },
    {
      "id": "201",
      "name": "John Smith",
      "type": "User",
      "number": "2001",
      "process_calls": true
    }
  ]
}
```

The `process_calls` flag determines if calls to this extension should be processed.

### Lead Owners

Zoho CRM lead owners are configured in:
- Single company: `data/lead_owners.json`
- Multi-company: `sorted/<office>/lead_owners.json`

Example:
```json
{
  "lead_owners": [
    {
      "id": "5678901234",
      "name": "Sarah Reynolds",
      "email": "sarah.reynolds@example.com",
      "active": true,
      "assignment_weight": 2.0
    },
    {
      "id": "6789012345",
      "name": "David Chen",
      "email": "david.chen@example.com",
      "active": true,
      "assignment_weight": 1.5
    }
  ],
  "assignment_rules": {
    "round_robin": true,
    "respect_weights": true,
    "fallback_owner_id": "5678901234"
  }
}
```

The `assignment_weight` determines how frequently leads are assigned to each owner when using weighted distribution.

### Field Mappings

Field mappings between RingCentral call data and Zoho CRM fields are configured in:
```
data/zoho_field_mappings.json
```

Example:
```json
{
  "accepted_calls": {
    "Phone": "Phone",
    "Email": "Email",
    "First_Name": "First_Name",
    "Last_Name": "Last_Name",
    "Company": "Company"
  },
  "missed_calls": {
    "Phone": "Phone",
    "First_Name": "First_Name",
    "Last_Name": "Last_Name",
    "Company": "Company"
  },
  "lead_status": {
    "new": "New",
    "accepted_call": "Accepted Call",
    "missed_call": "Missed Call",
    "missed_call_with_voicemail": "Missed Call with Voicemail"
  }
}
```

### Email Settings

Email notification settings are configured in:
```
data/email_config.json
```

Example:
```json
{
  "smtp_server": "smtp.example.com",
  "smtp_port": 587,
  "use_tls": true,
  "sender_email": "integration@example.com",
  "sender_name": "RC-Zoho Integration",
  "recipients": [
    {
      "name": "Admin",
      "email": "admin@example.com",
      "receive_daily": true,
      "receive_errors": true
    }
  ],
  "report_settings": {
    "send_empty_reports": false,
    "include_charts": true
  }
}
```

## Automated Scheduling

### Windows Task Scheduler

To set up automated processing in Windows:

1. Open Task Scheduler
2. Click "Create Basic Task"
3. Enter a name and description
4. Set the trigger (daily/weekly/etc.)
5. Select "Start a Program"
6. Browse to the batch file:
   ```
   C:\path\to\run_multi_location_all_calls_with_report_ordered.bat
   ```
7. Optionally add arguments like `--hours-back 24`
8. Complete the wizard

PowerShell commands to create a scheduled task:
```powershell
$action = New-ScheduledTaskAction -Execute "C:\path\to\run_multi_location_all_calls_with_report_ordered.bat"
$trigger = New-ScheduledTaskTrigger -Daily -At 8am
Register-ScheduledTask -Action $action -Trigger $trigger -TaskName "RingCentral-Zoho Integration" -Description "Process RingCentral calls into Zoho CRM"
```

### Linux Cron Jobs

To set up automated processing in Linux:

1. Open your crontab:
   ```bash
   crontab -e
   ```

2. Add an entry:
   ```
   0 8 * * * /path/to/run_multi_location_all_calls_with_report_ordered.sh
   ```

3. For more complex schedules:
   ```
   # Run at 8 AM and 2 PM every weekday
   0 8,14 * * 1-5 /path/to/run_multi_location_all_calls_with_report_ordered.sh
   
   # Run every 4 hours
   0 */4 * * * /path/to/run_multi_location_all_calls_with_report_ordered.sh --hours-back 4
   ```

## Reports and Monitoring

### Email Reports

The integration can send HTML email reports after processing. Reports include:

- Processing summary (calls processed, leads created/updated)
- Error summary (if any errors occurred)
- Charts showing call distribution and processing results
- Detailed call listing (configurable)

Example email report configuration:
```json
{
  "smtp_server": "smtp.example.com",
  "smtp_port": 587,
  "use_tls": true,
  "sender_email": "integration@example.com",
  "sender_name": "RC-Zoho Integration",
  "recipients": [
    {
      "name": "Admin",
      "email": "admin@example.com",
      "receive_daily": true,
      "receive_errors": true
    },
    {
      "name": "Manager",
      "email": "manager@example.com",
      "receive_daily": true,
      "receive_errors": false
    }
  ]
}
```

### Log Files

The integration creates several log files:

- **Accepted calls logs**: `logs/accepted_calls_YYYYMMDD.log`
- **Missed calls logs**: `logs/missed_calls_YYYYMMDD.log`
- **Multi-location logs**: `logs/multi_location_report_YYYYMMDD.log`
- **Raw call logs**: `logs/YYYY-MM-DD/office/raw_logs/raw_call_logs_YYYYMMDD_HHMMSS.json`

Log rotation happens automatically with date-stamped filenames.

### Performance Monitoring

To monitor the performance of the integration:

1. **Processing Statistics**: Available in log files and email reports
2. **Error Monitoring**: Check log files for ERROR level messages
3. **API Monitoring**:
   - RingCentral API rate limit usage is logged
   - Zoho CRM API request counts are tracked

For advanced monitoring, consider setting up log forwarding to a central logging system.

## Troubleshooting

### Common Issues

#### API Authentication Errors

**Symptoms**:
- Error messages about invalid tokens
- "Unauthorized" errors in logs

**Solutions**:
1. Verify credentials are correctly configured:
   ```
   run_setup_credentials.bat
   ```
2. Ensure API access hasn't been revoked in RingCentral/Zoho admin consoles
3. Check for expired tokens or keys

#### Call Processing Issues

**Symptoms**:
- No calls being processed
- Missing call recordings/voicemails

**Solutions**:
1. Verify extensions are correctly configured with `process_calls: true`
2. Check if calls are within the configured time range (--hours-back)
3. Ensure RingCentral account has call recording enabled if needed
4. Run with debug logging to see detailed API responses:
   ```
   run_accepted_calls.bat --office philadelphia --debug
   ```

#### Email Sending Failures

**Symptoms**:
- Reports not being delivered
- Error messages related to SMTP

**Solutions**:
1. Verify SMTP settings in `data/email_config.json`
2. Check if the SMTP server requires authentication
3. Test SMTP settings with a simple mail client
4. Check firewall settings that might block SMTP traffic

### Diagnostic Steps

When troubleshooting issues, follow these steps:

1. **Enable Debug Logging**:
   ```
   run_accepted_calls.bat --office philadelphia --debug
   ```

2. **Run in Dry-Run Mode**:
   ```
   run_accepted_calls.bat --office philadelphia --dry-run --debug
   ```

3. **Check Log Files**:
   - Look for ERROR or WARNING level messages
   - Check for API error responses
   - Verify call log retrieval is successful

4. **Verify Configurations**:
   - Confirm extensions.json has correct extension IDs
   - Ensure lead_owners.json has valid Zoho CRM user IDs
   - Check field mappings match your Zoho CRM setup

5. **Test API Access**:
   - Use the admin interface to check credential status
   - Test RingCentral API access manually if possible
   - Test Zoho CRM API access manually if possible

### Error Reference

Common error codes and their solutions:

| Error Code | Message | Solution |
|------------|---------|----------|
| RC-401 | RingCentral unauthorized | Refresh or reconfigure RC credentials |
| RC-429 | Rate limit exceeded | Add delay between API calls or reduce processing frequency |
| ZOHO-401 | Zoho CRM unauthorized | Refresh or reconfigure Zoho credentials |
| ZOHO-422 | Invalid lead data | Check field mappings and required fields |
| IO-001 | Failed to read/write file | Check file permissions |
| SMTP-001 | Failed to send email | Verify SMTP settings |

## Security Considerations

### Encryption

The integration encrypts sensitive data:

- **API Credentials**: Encrypted with Fernet symmetric encryption
- **Encryption Key**: Stored in `data/encryption.key`
- **Temporary Files**: Call recordings and voicemails are encrypted during processing

Important security notes:
- Protect the encryption key file
- Consider storing the key file on a separate secure storage
- Regularly rotate encryption keys for enhanced security

### API Permissions

Required API permissions:

#### RingCentral
- Read Call Log Records
- Read Call Recordings
- Read Extensions
- Read Accounts

#### Zoho CRM
- ZohoCRM.modules.ALL
- ZohoCRM.settings.ALL
- ZohoCRM.users.ALL

Principle of least privilege:
- Create dedicated API users with only required permissions
- Regularly audit API access and rotate credentials

### Best Practices

Follow these security best practices:

1. **Credential Management**:
   - Store credentials securely
   - Rotate API credentials regularly
   - Use dedicated API users with limited permissions

2. **Network Security**:
   - Run the integration on a secure, isolated network when possible
   - Use HTTPS/TLS for all API communications
   - Consider using a VPN for remote deployments

3. **Data Protection**:
   - Implement log rotation and purging policy
   - Avoid storing raw call logs longer than necessary
   - Configure the integration to clean up temporary files

4. **Access Control**:
   - Limit access to the integration server
   - Protect configuration files with appropriate permissions
   - Consider using a service account to run the integration

## Advanced Usage

### Custom Field Mappings

To map call data to custom Zoho CRM fields:

1. Update `data/zoho_field_mappings.json`:
   ```json
   {
     "accepted_calls": {
       "Phone": "Phone",
       "Custom_Field": "${caller_company}"
     }
   }
   ```

2. Available dynamic variables:
   - `${caller_name}`: Caller's name from RingCentral
   - `${caller_number}`: Caller's phone number
   - `${caller_company}`: Caller's company if available
   - `${call_time}`: Call date/time
   - `${call_duration}`: Call duration in seconds
   - `${extension_name}`: Extension name that received the call
   - `${lead_owner_id}`: ID of the assigned lead owner

3. Apply transforms to variables:
   ```json
   {
     "accepted_calls": {
       "Custom_Field": "${call_duration:minutes}"
     }
   }
   ```

   Available transforms: `:uppercase`, `:lowercase`, `:minutes`, `:seconds`, `:date`

### Advanced Lead Assignment

Configure complex lead assignment rules:

1. **Weighted Assignment**:
   ```json
   {
     "assignment_rules": {
       "round_robin": true,
       "respect_weights": true
     },
     "lead_owners": [
       {
         "id": "123456",
         "assignment_weight": 2.0
       },
       {
         "id": "789012",
         "assignment_weight": 1.0
       }
     ]
   }
   ```

2. **Department-Specific Assignment**:
   ```json
   {
     "assignment_rules": {
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

3. **Office Hours Assignment**:
   ```json
   {
     "assignment_rules": {
       "office_hours_only": true,
       "office_hours": {
         "start": "09:00",
         "end": "17:00",
         "timezone": "America/New_York",
         "days": [1, 2, 3, 4, 5]
       },
       "after_hours_owner_id": "emergency_owner_id"
     }
   }
   ```

### Multiple Environments

To set up multiple environments (development, production, etc.):

1. Create separate installation directories
2. Use different configuration files for each environment
3. For a single codebase with multiple configurations:
   ```
   run_accepted_calls.bat --config-dir configs/production
   ```

4. Example directory structure:
   ```
   integration/
   ├── configs/
   │   ├── development/
   │   │   ├── data/
   │   │   └── sorted/
   │   └── production/
   │       ├── data/
   │       └── sorted/
   └── core/
       ├── accepted_calls.py
       ├── missed_calls.py
       └── ...
   ```

## Appendices

### API Rate Limits

#### RingCentral API
- Default rate limit: 60 requests per minute
- Batch operations count as 1 request
- The integration implements circuit breaker pattern to handle rate limiting

#### Zoho CRM API
- Default rate limit: 100 requests per minute per organization
- Search operations count as 2 requests
- Create/update operations count as 1 request
- Attachment operations count as 2 requests

### Version History

| Version | Release Date | Major Features |
|---------|--------------|---------------|
| 1.0.0   | 2024-01-15   | Initial release |
| 1.1.0   | 2024-02-28   | Added multi-office support |
| 1.2.0   | 2024-03-15   | Added unified admin interface |
| 1.3.0   | 2024-04-10   | Added email reporting |
| 1.4.0   | 2024-05-01   | Added weighted lead assignment |
| 1.5.0   | 2024-05-09   | Improved security features |

### Glossary

- **Accepted Call**: A call that was answered by a RingCentral extension
- **Circuit Breaker**: A design pattern that prevents repeated failed API calls
- **Extension**: A RingCentral phone number or department
- **Lead Assignment**: The process of assigning new leads to owners in Zoho CRM
- **Lead Owner**: A user in Zoho CRM who is responsible for leads
- **Missed Call**: A call that was not answered by any extension
- **Round-Robin**: A method of distributing leads evenly among owners
- **Voicemail**: A voice message left after a missed call

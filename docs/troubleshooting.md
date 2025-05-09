# Troubleshooting Guide for RingCentral-Zoho CRM Integration

This guide provides solutions for common issues encountered when using the RingCentral-Zoho CRM Integration.

## Table of Contents

- [Installation Issues](#installation-issues)
- [API Authentication Issues](#api-authentication-issues)
- [Call Processing Issues](#call-processing-issues)
- [Email Report Issues](#email-report-issues)
- [Multi-Office Configuration Issues](#multi-office-configuration-issues)
- [Performance Issues](#performance-issues)
- [Diagnostic Tools](#diagnostic-tools)

## Installation Issues

### Python Installation Problems

**Issue**: Setup fails with `Python is not installed or not in PATH` error.

**Solution**:
1. Ensure Python 3.8 or higher is installed:
   - Windows: Download from [python.org](https://www.python.org/downloads/)
   - Linux: Use your package manager (e.g., `sudo apt install python3`)
2. Add Python to your PATH environment variable
3. Verify installation with `python --version` or `python3 --version`

### Virtual Environment Creation Fails

**Issue**: Setup fails to create a virtual environment.

**Solution**:
1. Install the venv module:
   - Windows: It should be included with Python installation
   - Linux: `sudo apt install python3-venv` (Ubuntu/Debian) or `sudo dnf install python3-venv` (Fedora/CentOS)
2. Ensure you have permissions to create directories in the installation location
3. Run setup script again

### Package Installation Failures

**Issue**: Required packages fail to install during setup.

**Solution**:
1. Ensure you have internet connectivity
2. Check if pip is up to date: `python -m pip install --upgrade pip`
3. Manually install packages from requirements.txt:
   ```
   python -m pip install cryptography python-dateutil pytz requests ttkbootstrap tkcalendar phonenumbers beautifulsoup4 matplotlib Pillow
   ```
4. If you see SSL errors, ensure your Python installation has SSL support

## API Authentication Issues

### RingCentral Authentication Failures

**Issue**: Errors like "RingCentral unauthorized" or "Invalid token"

**Solution**:
1. Reconfigure credentials: `run_setup_credentials.bat` or `./run_setup_credentials.sh`
2. Check that your JWT credentials are valid in the RingCentral Developer Console
3. Verify you have the correct permissions (Read Call Log Records, Read Call Recordings)
4. Check log files for specific error messages

### Zoho CRM Authentication Failures

**Issue**: Errors like "Zoho CRM unauthorized" or "Invalid token"

**Solution**:
1. Reconfigure credentials: `run_setup_credentials.bat` or `./run_setup_credentials.sh`
2. Verify the refresh token is still valid (they expire after a certain period)
3. Check that your API client is still active in Zoho Developer Console
4. Verify your Zoho CRM account has not been suspended or deactivated

### Encryption Key Issues

**Issue**: "Failed to decrypt credentials" or "Invalid key" errors

**Solution**:
1. Check if `data/encryption.key` exists and is readable
2. If the key file is corrupted or missing, you'll need to reconfigure your credentials
3. Do not move credentials between different installations without moving the encryption key too

## Call Processing Issues

### No Calls Being Processed

**Issue**: Integration runs without errors, but no calls are processed

**Solution**:
1. Verify that calls exist in the configured time range (--hours-back parameter)
2. Check extension configuration to ensure `process_calls` is set to `true`
3. Verify that the extensions in your configuration match actual RingCentral extensions
4. Run with debug logging to see API responses:
   ```
   run_accepted_calls.bat --debug
   ```

### Missing Call Recordings or Voicemails

**Issue**: Calls are processed, but recordings/voicemails are not attached

**Solution**:
1. Verify that call recording is enabled in your RingCentral account
2. Check if the calls actually have recordings available
3. Verify your RingCentral API user has permission to access recordings
4. Check if temporary file storage has sufficient space
5. Run with debug logging to see detailed API responses

### Duplicated Leads in Zoho CRM

**Issue**: Multiple leads created for the same caller

**Solution**:
1. Check your Zoho CRM for existing duplicate leads
2. Verify phone number formatting settings in the integration
3. Consider setting up a deduplication process in Zoho CRM
4. Check if there are multiple Zoho CRM integrations running simultaneously

## Email Report Issues

### Email Reports Not Being Sent

**Issue**: Processing completes but no email reports are received

**Solution**:
1. Verify SMTP settings in `data/email_config.json`
2. Check if the SMTP server requires authentication
3. If using Gmail, ensure "Less secure app access" is enabled or use App Passwords
4. Check firewall settings that might block outgoing SMTP traffic
5. Run with --debug flag to see SMTP communication details

### Email Formatting Problems

**Issue**: Email reports are sent but display incorrectly

**Solution**:
1. Check if your email client supports HTML emails
2. Verify that chart images are being generated correctly
3. Ensure the temp directory for report generation exists and is writable
4. Check for specific error messages in the logs related to report generation

## Multi-Office Configuration Issues

### Office-Specific Configuration Not Applied

**Issue**: Integration doesn't use the correct configuration for specific offices

**Solution**:
1. Verify the office directory structure matches what's in `sorted/data/offices.json`
2. Check that office identifiers used in command line match configuration file names
3. Ensure each office has its own extensions.json and lead_owners.json files
4. Verify the processing order in offices.json is correct

### Processing Order Issues

**Issue**: Offices are processed in the wrong order

**Solution**:
1. Check the `processing_order` values in `sorted/data/offices.json`
2. Ensure they are sequential integers (1, 2, 3...)
3. When running with --ordered flag, verify the log output shows correct sequence
4. Consider running each office individually to test configurations

## Performance Issues

### Slow Processing Times

**Issue**: Integration takes a long time to process calls

**Solution**:
1. Limit the time range with --hours-back parameter
2. Check your internet connection speed
3. Monitor API rate limits in the logs
4. Consider processing offices separately or at different times
5. Implement a circuit breaker pattern in the code (already present but may need tuning)

### High Memory Usage

**Issue**: Application uses excessive memory during processing

**Solution**:
1. Process smaller time ranges of calls
2. Ensure you're not processing an excessive number of calls
3. Close other memory-intensive applications
4. Consider increasing system RAM if regularly processing large call volumes

## Diagnostic Tools

### Log File Analysis

Use these commands to check log files for errors:

**Windows**:
```
type logs\accepted_calls_YYYYMMDD.log | findstr ERROR
```

**Linux**:
```
grep ERROR logs/accepted_calls_YYYYMMDD.log
```

### Testing API Access

To test API access directly:

1. **RingCentral API Test**:
   Use admin interface "Test Connection" button or run with --debug flag

2. **Zoho CRM API Test**:
   Use admin interface "Test Connection" button or run with --debug flag

### Database Connection Testing

For advanced users, you can directly test database connectivity:

```python
from common import ZohoClient
client = ZohoClient("path/to/credentials.enc", "path/to/encryption.key")
result = client.test_connection()
print(result)
```

### Network Connectivity Testing

If experiencing API connectivity issues:

```
ping api.ringcentral.com
ping zohoapis.com
```

## Still Having Issues?

If you continue to experience problems after trying these troubleshooting steps:

1. Check if there are any known issues in the GitHub repository
2. Open an issue on GitHub with detailed information about your problem
3. Include relevant log files with any sensitive information redacted
4. Provide details about your environment (OS, Python version, etc.)

## Logging Levels

To get more detailed troubleshooting information, use these logging flags:

- `--debug`: Most verbose logging, shows API calls and responses
- `--verbose`: Detailed logging without API responses
- `--quiet`: Only error messages

Example:
```
run_accepted_calls.bat --office philadelphia --debug

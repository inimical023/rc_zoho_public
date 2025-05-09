#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
RingCentral-Zoho CRM Integration - Missed Calls Processor
This script processes missed calls from RingCentral and creates/updates leads in Zoho CRM.
"""

import os
import sys
import json
import logging
import argparse
import datetime
import itertools
from common import (
    RingCentralClient, 
    ZohoClient, 
    SecureStorage, 
    LogExporter,
    normalize_phone_number,
    format_call_time,
    setup_logging,
    parse_arguments,
    get_date_range,
    check_and_install_dependencies
)

# Check dependencies before importing other modules
check_and_install_dependencies()

def process_office(office_id, hours_back=24, debug=False, dry_run=False):
    """
    Process missed calls for a specific office.
    
    Args:
        office_id (str): Office identifier
        hours_back (int): Hours to look back for calls
        debug (bool): Enable debug logging
        dry_run (bool): Run without making changes to Zoho
        
    Returns:
        dict: Processing statistics
    """
    # Set up logging
    logger = setup_logging("missed_calls", debug)
    logger.info(f"Starting missed calls processing for office: {office_id}")
    logger.info(f"Looking back {hours_back} hours")
    
    if dry_run:
        logger.info("DRY RUN MODE: No changes will be made to Zoho")
    
    # Track statistics
    stats = {
        "total_calls_processed": 0,
        "missed_with_voicemail": 0,
        "missed_without_voicemail": 0,
        "new_leads_created": 0,
        "existing_leads_updated": 0,
        "voicemail_attachments": 0,
        "errors": 0,
        "start_time": datetime.datetime.now().isoformat(),
        "office_id": office_id,
        "hours_back": hours_back
    }
    
    try:
        # Initialize services
        storage = SecureStorage(debug)
        
        # Load configuration
        credentials = storage.load_credentials()
        extensions = storage.load_extensions(office_id)
        lead_owners = storage.load_lead_owners(office_id)
        field_mappings = storage.load_field_mappings()
        
        # Initialize clients
        rc_client = RingCentralClient(credentials["ringcentral"], debug)
        zoho_client = ZohoClient(credentials["zoho"], debug)
        
        # Setup lead owner cycle for round-robin assignment
        lead_owner_cycle = itertools.cycle(lead_owners)
        
        # Get date range for call logs
        start_date, end_date = get_date_range(hours_back)
        
        # Create log exporter
        date_str = datetime.datetime.now().strftime("%Y-%m-%d")
        log_exporter = LogExporter("missed_calls", office_id, date_str, debug)
        
        # Process each extension
        for extension in extensions:
            logger.info(f"Processing extension: {extension['name']} (ID: {extension['id']})")
            
            # Get missed calls for this extension
            call_logs = rc_client.get_call_logs(
                extension['id'], 
                start_date=start_date, 
                end_date=end_date, 
                direction="Inbound",
                type="Voice",
                result="Missed"
            )
            
            if not call_logs:
                logger.info(f"No missed calls found for extension {extension['id']}")
                continue
            
            # Export raw call logs
            log_exporter.export_raw_logs(call_logs, "raw_call_logs")
            
            # Process each call
            for call in call_logs:
                stats["total_calls_processed"] += 1
                
                # Extract caller information
                caller_number = normalize_phone_number(call.get("from", {}).get("phoneNumber", ""))
                
                if not caller_number:
                    logger.warning(f"Skipping call {call['id']} with no caller number")
                    continue
                
                call_time = format_call_time(call.get("startTime", ""))
                call_id = call.get("id", "unknown")
                
                # Check for voicemail
                has_voicemail = False
                message_id = None
                
                for leg in call.get("legs", []):
                    message = leg.get("message", {})
                    if message and message.get("type") == "VoiceMail":
                        has_voicemail = True
                        message_id = message.get("id")
                        break
                
                if has_voicemail:
                    stats["missed_with_voicemail"] += 1
                    logger.info(f"Found voicemail for call {call_id}")
                else:
                    stats["missed_without_voicemail"] += 1
                    logger.info(f"No voicemail for call {call_id}")
                
                # Skip processing if in dry-run mode
                if dry_run:
                    logger.info(f"DRY RUN: Would process missed call {call_id}")
                    continue
                
                # Search for existing lead by phone number
                existing_lead = zoho_client.search_by_phone(caller_number)
                
                if existing_lead:
                    # Lead exists, update it
                    lead_id = existing_lead.get("id")
                    logger.info(f"Found existing lead {lead_id} for caller {caller_number}")
                    
                    # Only add note, do not update fields on existing leads
                    stats["existing_leads_updated"] += 1
                    
                    # Check for existing notes for this call to prevent duplicates
                    existing_notes = zoho_client.get_lead_notes(lead_id)
                    
                    if existing_notes:
                        has_note_for_call = any(f"Call ID: {call_id}" in note.get("Note_Content", "") for note in existing_notes)
                        if has_note_for_call:
                            logger.info(f"Skipping note creation for call {call_id} as it already exists")
                            continue
                    
                    # Add note with call details
                    note_title = f"Missed Call - {call_time}"
                    note_content = f"Missed call at {call_time}\n"
                    note_content += f"Caller: {call.get('from', {}).get('name', 'Unknown')} <{caller_number}>\n"
                    note_content += f"Call ID: {call_id}\n"
                    
                    if has_voicemail:
                        note_content += "Voicemail attached"
                    
                    zoho_client.add_note_to_lead(lead_id, note_content, note_title)
                    
                    # Attach voicemail if available
                    if has_voicemail and message_id:
                        voicemail_content = rc_client.get_voicemail_content(message_id)
                        if voicemail_content:
                            zoho_client.attach_audio_to_lead(
                                lead_id,
                                call,
                                voicemail_content,
                                "audio/wav",
                                call_time,
                                "voicemail"
                            )
                            stats["voicemail_attachments"] += 1
                
                else:
                    # Create new lead
                    lead_owner = next(lead_owner_cycle)
                    
                    # Set base lead data
                    lead_data = {
                        "Company": call.get("from", {}).get("name", "Unknown Caller"),
                        "First_Name": "", 
                        "Last_Name": "Unknown Caller",
                        "Phone": caller_number,
                        "Lead_Status": "Missed Call",
                        "Lead_Source": "RingCentral Integration",
                        "Lead_Owner": {"id": lead_owner["id"]}
                    }
                    
                    # Create lead in Zoho
                    new_lead = zoho_client.create_lead(lead_data)
                    
                    if new_lead:
                        lead_id = new_lead["id"]
                        logger.info(f"Created new lead {lead_id} for caller {caller_number}")
                        stats["new_leads_created"] += 1
                        
                        # Add note with call details
                        note_title = f"Missed Call - {call_time}"
                        note_content = f"Missed call at {call_time}\n"
                        note_content += f"Caller: {call.get('from', {}).get('name', 'Unknown')} <{caller_number}>\n"
                        note_content += f"Call ID: {call_id}\n"
                        
                        if has_voicemail:
                            note_content += "Voicemail attached"
                        
                        zoho_client.add_note_to_lead(lead_id, note_content, note_title)
                        
                        # Attach voicemail if available
                        if has_voicemail and message_id:
                            voicemail_content = rc_client.get_voicemail_content(message_id)
                            if voicemail_content:
                                zoho_client.attach_audio_to_lead(
                                    lead_id,
                                    call,
                                    voicemail_content,
                                    "audio/wav",
                                    call_time,
                                    "voicemail"
                                )
                                stats["voicemail_attachments"] += 1
        
        # Log completion
        stats["end_time"] = datetime.datetime.now().isoformat()
        stats["success"] = True
        logger.info(f"Missed calls processing completed for office: {office_id}")
        logger.info(f"Stats: {json.dumps(stats, indent=2)}")
        
    except Exception as e:
        logger.error(f"Error processing office {office_id}: {str(e)}", exc_info=True)
        stats["success"] = False
        stats["error"] = str(e)
        stats["end_time"] = datetime.datetime.now().isoformat()
    
    # Export processing statistics
    if 'log_exporter' in locals():
        log_exporter.export_stats(stats, "processing_stats")
    
    return stats

if __name__ == "__main__":
    # Parse command line arguments
    args = parse_arguments()
    
    # Process single office or multiple offices based on arguments
    if args.office:
        process_office(args.office, args.hours_back, args.debug, args.dry_run)
    elif args.office_order:
        offices = [o.strip() for o in args.office_order.split(',')]
        for office in offices:
            process_office(office, args.hours_back, args.debug, args.dry_run)
    elif args.all_offices:
        storage = SecureStorage(args.debug)
        offices = storage.load_office_list()
        for office in sorted(offices, key=lambda o: o.get('processing_order', 999)):
            process_office(office['id'], args.hours_back, args.debug, args.dry_run)
    else:
        print("Error: Must specify --office, --office-order, or --all-offices")
        sys.exit(1)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
RingCentral-Zoho CRM Integration - Unified Admin Interface
This script provides a GUI to manage the RingCentral-Zoho integration.
"""

import os
import sys
import json
import logging
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, messagebox
import subprocess
import datetime
import threading
import queue
from secure_credentials import SecureCredentials

# Try to import ttkbootstrap for better styling
try:
    import ttkbootstrap as ttk
    from ttkbootstrap.constants import *
    USING_BOOTSTRAP = True
except ImportError:
    import tkinter.ttk as ttk
    USING_BOOTSTRAP = False

# Try to import tkcalendar
try:
    from tkcalendar import DateEntry
    HAVE_CALENDAR = True
except ImportError:
    HAVE_CALENDAR = False

# Configure logging
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/unified_admin.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ProcessOutputReader:
    """Class to read output from a subprocess in a separate thread."""
    
    def __init__(self, process, text_widget):
        self.process = process
        self.text_widget = text_widget
        self.queue = queue.Queue()
        self.running = True
        self.thread = threading.Thread(target=self._read_output)
        self.thread.daemon = True
        self.thread.start()
        self.text_widget.after(100, self._update_text)
    
    def _read_output(self):
        while self.running:
            if self.process.poll() is not None:
                self.running = False
                break
            try:
                line = self.process.stdout.readline()
                if line:
                    self.queue.put(line.decode('utf-8', errors='replace'))
            except:
                self.running = False
                break
    
    def _update_text(self):
        try:
            while True:
                line = self.queue.get_nowait()
                self.text_widget.insert(tk.END, line)
                self.text_widget.see(tk.END)
                self.queue.task_done()
        except queue.Empty:
            if self.running:
                self.text_widget.after(100, self._update_text)
            else:
                self.text_widget.insert(tk.END, "\n--- Process completed ---\n")
                self.text_widget.see(tk.END)

class UnifiedAdmin:
    """Main admin interface class."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("RingCentral-Zoho Integration Admin")
        self.root.geometry("900x600")
        self.current_process = None
        
        # Set icon if available
        try:
            if os.name == 'nt':  # Windows
                self.root.iconbitmap("resources/icon.ico")
            else:  # Linux/Mac
                icon = tk.PhotoImage(file="resources/icon.png")
                self.root.iconphoto(True, icon)
        except:
            pass
        
        self._create_variables()
        self._create_widgets()
        self._create_layout()
        self._check_credentials()
        self._load_offices()
    
    def _create_variables(self):
        """Initialize UI variables."""
        self.selected_office = tk.StringVar()
        self.hours_back = tk.IntVar(value=24)
        self.dry_run = tk.BooleanVar(value=False)
        self.debug_mode = tk.BooleanVar(value=False)
        self.process_accepted = tk.BooleanVar(value=True)
        self.process_missed = tk.BooleanVar(value=True)
        self.send_email = tk.BooleanVar(value=True)
        self.log_level = tk.StringVar(value="INFO")
    
    def _create_widgets(self):
        """Create UI widgets."""
        # Main notebook
        self.notebook = ttk.Notebook(self.root)
        
        # Dashboard tab
        self.dashboard_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.dashboard_frame, text="Dashboard")
        
        # Processing tab
        self.processing_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.processing_frame, text="Processing")
        
        # Configuration tab
        self.config_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.config_frame, text="Configuration")
        
        # Reports tab
        self.reports_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.reports_frame, text="Reports")
        
        # Status bar
        self.status_bar = ttk.Label(self.root, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
        
        # Dashboard widgets
        self.dash_title = ttk.Label(self.dashboard_frame, text="RingCentral-Zoho Integration Dashboard", font=("Helvetica", 16))
        self.cred_status_frame = ttk.LabelFrame(self.dashboard_frame, text="Credentials Status")
        self.rc_status = ttk.Label(self.cred_status_frame, text="RingCentral: Checking...")
        self.zoho_status = ttk.Label(self.cred_status_frame, text="Zoho CRM: Checking...")
        
        self.quick_actions_frame = ttk.LabelFrame(self.dashboard_frame, text="Quick Actions")
        self.setup_creds_btn = ttk.Button(self.quick_actions_frame, text="Setup Credentials", command=self._run_setup_credentials)
        self.run_accepted_btn = ttk.Button(self.quick_actions_frame, text="Process Accepted Calls", command=lambda: self._run_accepted_calls())
        self.run_missed_btn = ttk.Button(self.quick_actions_frame, text="Process Missed Calls", command=lambda: self._run_missed_calls())
        
        self.stats_frame = ttk.LabelFrame(self.dashboard_frame, text="Processing Statistics")
        # Stats content would be populated dynamically
        
        # Processing widgets
        self.proc_title = ttk.Label(self.processing_frame, text="Run Call Processing", font=("Helvetica", 16))
        
        self.proc_config_frame = ttk.LabelFrame(self.processing_frame, text="Processing Configuration")
        self.office_label = ttk.Label(self.proc_config_frame, text="Office:")
        self.office_combo = ttk.Combobox(self.proc_config_frame, textvariable=self.selected_office)
        
        self.hours_label = ttk.Label(self.proc_config_frame, text="Hours back:")
        self.hours_spin = ttk.Spinbox(self.proc_config_frame, from_=1, to=168, textvariable=self.hours_back)
        
        self.dry_run_check = ttk.Checkbutton(self.proc_config_frame, text="Dry run (no changes)", variable=self.dry_run)
        self.debug_check = ttk.Checkbutton(self.proc_config_frame, text="Debug mode", variable=self.debug_mode)
        
        self.call_types_frame = ttk.LabelFrame(self.proc_config_frame, text="Call Types")
        self.accepted_check = ttk.Checkbutton(self.call_types_frame, text="Process accepted calls", variable=self.process_accepted)
        self.missed_check = ttk.Checkbutton(self.call_types_frame, text="Process missed calls", variable=self.process_missed)
        self.email_check = ttk.Checkbutton(self.call_types_frame, text="Send email report", variable=self.send_email)
        
        self.run_btn = ttk.Button(self.proc_config_frame, text="Run Processing", command=self._run_processing)
        
        self.output_frame = ttk.LabelFrame(self.processing_frame, text="Processing Output")
        self.output_text = tk.Text(self.output_frame, height=15, wrap=tk.WORD)
        self.output_scrollbar = ttk.Scrollbar(self.output_frame, orient=tk.VERTICAL, command=self.output_text.yview)
        self.output_text.configure(yscrollcommand=self.output_scrollbar.set)
        
        # Configuration widgets
        self.config_title = ttk.Label(self.config_frame, text="Configuration Management", font=("Helvetica", 16))
        
        self.config_tabs = ttk.Notebook(self.config_frame)
        
        # Offices tab
        self.offices_frame = ttk.Frame(self.config_tabs)
        self.config_tabs.add(self.offices_frame, text="Offices")
        
        # Extensions tab
        self.extensions_frame = ttk.Frame(self.config_tabs)
        self.config_tabs.add(self.extensions_frame, text="Extensions")
        
        # Lead Owners tab
        self.lead_owners_frame = ttk.Frame(self.config_tabs)
        self.config_tabs.add(self.lead_owners_frame, text="Lead Owners")
        
        # Field Mappings tab
        self.mappings_frame = ttk.Frame(self.config_tabs)
        self.config_tabs.add(self.mappings_frame, text="Field Mappings")
        
        # Reports widgets
        self.reports_title = ttk.Label(self.reports_frame, text="Processing Reports", font=("Helvetica", 16))
        
        self.report_list_frame = ttk.LabelFrame(self.reports_frame, text="Available Reports")
        self.report_listbox = tk.Listbox(self.report_list_frame, height=10)
        self.report_scrollbar = ttk.Scrollbar(self.report_list_frame, orient=tk.VERTICAL, command=self.report_listbox.yview)
        self.report_listbox.configure(yscrollcommand=self.report_scrollbar.set)
        
        self.report_view_btn = ttk.Button(self.report_list_frame, text="View Report", command=self._view_report)
        self.report_refresh_btn = ttk.Button(self.report_list_frame, text="Refresh List", command=self._refresh_reports)
    
    def _create_layout(self):
        """Create UI layout."""
        # Main layout
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        
        # Dashboard layout
        self.dash_title.pack(pady=10)
        
        self.cred_status_frame.pack(fill=tk.X, padx=10, pady=5)
        self.rc_status.pack(anchor=tk.W, padx=5, pady=2)
        self.zoho_status.pack(anchor=tk.W, padx=5, pady=2)
        
        self.quick_actions_frame.pack(fill=tk.X, padx=10, pady=5)
        self.setup_creds_btn.pack(side=tk.LEFT, padx=5, pady=5)
        self.run_accepted_btn.pack(side=tk.LEFT, padx=5, pady=5)
        self.run_missed_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.stats_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Processing layout
        self.proc_title.pack(pady=10)
        
        self.proc_config_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.office_label.grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.office_combo.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        self.hours_label.grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.hours_spin.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        self.dry_run_check.grid(row=2, column=0, columnspan=2, sticky=tk.W, padx=5, pady=5)
        self.debug_check.grid(row=3, column=0, columnspan=2, sticky=tk.W, padx=5, pady=5)
        
        self.call_types_frame.grid(row=4, column=0, columnspan=2, sticky=tk.W+tk.E, padx=5, pady=5)
        self.accepted_check.pack(anchor=tk.W, padx=5, pady=2)
        self.missed_check.pack(anchor=tk.W, padx=5, pady=2)
        self.email_check.pack(anchor=tk.W, padx=5, pady=2)
        
        self.run_btn.grid(row=5, column=0, columnspan=2, padx=5, pady=10)
        
        self.output_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.output_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.output_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Configuration layout
        self.config_title.pack(pady=10)
        self.config_tabs.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Reports layout
        self.reports_title.pack(pady=10)
        
        self.report_list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.report_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.report_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.report_view_btn.pack(side=tk.LEFT, padx=5, pady=5)
        self.report_refresh_btn.pack(side=tk.LEFT, padx=5, pady=5)
    
    def _check_credentials(self):
        """Check if credentials are configured and valid."""
        try:
            secure = SecureCredentials()
            credentials = secure.decrypt_credentials()
            
            if credentials and credentials.get("ringcentral"):
                self.rc_status.config(text="RingCentral: Configured")
            else:
                self.rc_status.config(text="RingCentral: Not configured")
            
            if credentials and credentials.get("zoho"):
                self.zoho_status.config(text="Zoho CRM: Configured")
            else:
                self.zoho_status.config(text="Zoho CRM: Not configured")
        except Exception as e:
            logger.error(f"Error checking credentials: {str(e)}")
            self.rc_status.config(text="RingCentral: Error checking")
            self.zoho_status.config(text="Zoho CRM: Error checking")
    
    def _load_offices(self):
        """Load office list from configuration."""
        try:
            if os.path.exists("data/offices.json"):
                with open("data/offices.json", "r") as f:
                    offices_data = json.load(f)
                    offices = [
                        {"id": office_id, "name": office_data.get("name", office_id), "processing_order": office_data.get("processing_order", 999)}
                        for office_id, office_data in offices_data.get("offices", {}).items()
                    ]
                    
                    # Sort by processing order
                    offices.sort(key=lambda x: x["processing_order"])
                    
                    # Populate combobox
                    self.office_combo["values"] = [o["id"] for o in offices]
                    
                    if offices:
                        self.office_combo.current(0)
            elif os.path.exists("sorted/data/offices.json"):
                with open("sorted/data/offices.json", "r") as f:
                    offices_data = json.load(f)
                    offices = [
                        {"id": office_id, "name": office_data.get("name", office_id), "processing_order": office_data.get("processing_order", 999)}
                        for office_id, office_data in offices_data.get("offices", {}).items()
                    ]
                    
                    # Sort by processing order
                    offices.sort(key=lambda x: x["processing_order"])
                    
                    # Populate combobox
                    self.office_combo["values"] = [o["id"] for o in offices]
                    
                    if offices:
                        self.office_combo.current(0)
            else:
                # No offices.json, check if we have single company configuration
                if os.path.exists("data/extensions.json") and os.path.exists("data/lead_owners.json"):
                    # Single company mode
                    self.office_combo["values"] = ["singlecompany"]
                    self.office_combo.current(0)
                else:
                    messagebox.showwarning("Configuration Missing", "No office configuration found. Please run setup_integration.bat first.")
        except Exception as e:
            logger.error(f"Error loading offices: {str(e)}")
            messagebox.showerror("Error", f"Failed to load office configuration: {str(e)}")
    
    def _run_setup_credentials(self):
        """Run the credentials setup script."""
        if os.path.exists("run_setup_credentials.bat"):
            self._run_command("run_setup_credentials.bat")
        else:
            self._run_script("setup_credentials.py")
    
    def _run_accepted_calls(self):
        """Run accepted calls processing."""
        office = self.selected_office.get()
        if not office:
            messagebox.showerror("Error", "Please select an office")
            return
        
        if os.path.exists("run_accepted_calls.bat"):
            cmd = f"run_accepted_calls.bat --office {office}"
            if self.dry_run.get():
                cmd += " --dry-run"
            if self.debug_mode.get():
                cmd += " --debug"
            if self.hours_back.get() != 24:
                cmd += f" --hours-back {self.hours_back.get()}"
            
            self._run_command(cmd)
        else:
            args = ["accepted_calls.py", "--office", office]
            if self.dry_run.get():
                args.append("--dry-run")
            if self.debug_mode.get():
                args.append("--debug")
            if self.hours_back.get() != 24:
                args.extend(["--hours-back", str(self.hours_back.get())])
            
            self._run_script(*args)
    
    def _run_missed_calls(self):
        """Run missed calls processing."""
        office = self.selected_office.get()
        if not office:
            messagebox.showerror("Error", "Please select an office")
            return
        
        if os.path.exists("run_missed_calls.bat"):
            cmd = f"run_missed_calls.bat --office {office}"
            if self.dry_run.get():
                cmd += " --dry-run"
            if self.debug_mode.get():
                cmd += " --debug"
            if self.hours_back.get() != 24:
                cmd += f" --hours-back {self.hours_back.get()}"
            
            self._run_command(cmd)
        else:
            args = ["missed_calls.py", "--office", office]
            if self.dry_run.get():
                args.append("--dry-run")
            if self.debug_mode.get():
                args.append("--debug")
            if self.hours_back.get() != 24:
                args.extend(["--hours-back", str(self.hours_back.get())])
            
            self._run_script(*args)
    
    def _run_processing(self):
        """Run full processing with selected options."""
        office = self.selected_office.get()
        if not office:
            messagebox.showerror("Error", "Please select an office")
            return
        
        # Determine single or multi-company mode
        if office == "singlecompany" and os.path.exists("run_single_company_all_calls_with_report.bat"):
            # Single company mode
            cmd = "run_single_company_all_calls_with_report.bat"
            if self.dry_run.get():
                cmd += " --dry-run"
            if self.debug_mode.get():
                cmd += " --debug"
            if self.hours_back.get() != 24:
                cmd += f" --hours-back {self.hours_back.get()}"
            
            self._run_command(cmd)
        else:
            # Multi-company mode, run scripts sequentially
            if self.process_missed.get():
                self._run_missed_calls()
            
            if self.process_accepted.get():
                self._run_accepted_calls()
            
            if self.send_email.get():
                # TODO: Implement email report generation
                pass
    
    def _run_command(self, cmd):
        """Run a command in a new process and capture output."""
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, f"Running command: {cmd}\n\n")
        self.status_bar.config(text=f"Running: {cmd}")
        
        try:
            if os.name == 'nt':  # Windows
                self.current_process = subprocess.Popen(
                    cmd, 
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.STDOUT,
                    shell=True,
                    bufsize=1,
                    universal_newlines=False
                )
            else:  # Linux/Mac
                self.current_process = subprocess.Popen(
                    cmd, 
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.STDOUT,
                    shell=True,
                    bufsize=1,
                    universal_newlines=False
                )
            
            # Start reading output
            ProcessOutputReader(self.current_process, self.output_text)
            
        except Exception as e:
            logger.error(f"Error running command: {str(e)}")
            self.output_text.insert(tk.END, f"Error: {str(e)}")
            self.status_bar.config(text="Error running command")
    
    def _run_script(self, script_name, *args):
        """Run a Python script with given arguments."""
        cmd = [sys.executable, script_name] + list(args)
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, f"Running: {' '.join(cmd)}\n\n")
        self.status_bar.config(text=f"Running: {script_name}")
        
        try:
            self.current_process = subprocess.Popen(
                cmd, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.STDOUT,
                bufsize=1,
                universal_newlines=False
            )
            
            # Start reading output
            ProcessOutputReader(self.current_process, self.output_text)
            
        except Exception as e:
            logger.error(f"Error running script: {str(e)}")
            self.output_text.insert(tk.END, f"Error: {str(e)}")
            self.status_bar.config(text="Error running script")
    
    def _refresh_reports(self):
        """Refresh the list of available reports."""
        self.report_listbox.delete(0, tk.END)
        
        reports_dir = "logs/reports"
        if not os.path.exists(reports_dir):
            return
        
        # List HTML reports
        reports = [f for f in os.listdir(reports_dir) if f.endswith(".html")]
        reports.sort(reverse=True)  # Most recent first
        
        for report in reports:
            self.report_listbox.insert(tk.END, report)
    
    def _view_report(self):
        """View the selected report."""
        selected = self.report_listbox.curselection()
        if not selected:
            messagebox.showinfo("No Selection", "Please select a report to view")
            return
        
        report_name = self.report_listbox.get(selected[0])
        report_path = os.path.join("logs/reports", report_name)
        
        if not os.path.exists(report_path):
            messagebox.showerror("Error", f"Report file not found: {report_path}")
            return
        
        # Open the report in the default browser
        try:
            import webbrowser
            webbrowser.open_new_tab(f"file://{os.path.abspath(report_path)}")
        except Exception as e:
            logger.error(f"Error opening report: {str(e)}")
            messagebox.showerror("Error", f"Failed to open report: {str(e)}")

def main():
    """Main function."""
    try:
        if USING_BOOTSTRAP:
            # Use ttkbootstrap style if available
            root = ttk.Window(
                title="RingCentral-Zoho Integration Admin",
                themename="cosmo",
                resizable=(True, True),
                size=(900, 600)
            )
        else:
            # Fall back to standard tkinter
            root = tk.Tk()
        
        app = UnifiedAdmin(root)
        root.mainloop()
    except Exception as e:
        logger.error(f"Application error: {str(e)}", exc_info=True)
        messagebox.showerror("Error", f"Application error: {str(e)}")

if __name__ == "__main__":
    main()

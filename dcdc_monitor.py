#!/usr/bin/env python3
"""
DC-DC Converter Monitoring Application
Real-time monitoring and control for TAME-POWER DC-DC converters via CAN bus
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import csv
from datetime import datetime
from pathlib import Path
import threading
import queue
from typing import Dict, List, Optional
import cantools
from can_handler import CANBusHandler, CANMessage
from data_logger import DataLogger
from config_manager import ConfigManager


class DCDCMonitorApp:
    """Main application for DC-DC converter monitoring"""

    def __init__(self, root):
        self.root = root
        self.root.title("DC-DC Converter Monitor - TAME-POWER COMETi")
        self.root.geometry("1400x900")

        # Initialize components
        self.config = ConfigManager()
        self.can_handler = CANBusHandler(self.config)
        self.data_logger = DataLogger(self.config)
        self.message_queue = queue.Queue()

        # Data storage
        self.converter_data = {
            'DCDC_Primary': {},
            'DCDC_Primary_1': {},
            'DCDC_Primary_2': {}
        }

        # UI state
        self.is_monitoring = False
        self.selected_converter = 'DCDC_Primary'

        # Build UI
        self.setup_ui()

        # Start update loop
        self.update_display()

    def setup_ui(self):
        """Create the user interface"""
        # Menu bar
        self.create_menu()

        # Top control panel
        control_frame = ttk.Frame(self.root, padding="10")
        control_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E))

        # CAN Bus connection controls
        ttk.Label(control_frame, text="CAN Interface:").grid(row=0, column=0, padx=5)
        self.can_interface = ttk.Combobox(control_frame, values=['can0', 'can1', 'vcan0'], width=15)
        self.can_interface.set(self.config.get('can_interface', 'can0'))
        self.can_interface.grid(row=0, column=1, padx=5)

        self.start_btn = ttk.Button(control_frame, text="▶ Start Monitoring", command=self.start_monitoring)
        self.start_btn.grid(row=0, column=2, padx=5)

        self.stop_btn = ttk.Button(control_frame, text="⏸ Stop", command=self.stop_monitoring, state=tk.DISABLED)
        self.stop_btn.grid(row=0, column=3, padx=5)

        self.status_label = ttk.Label(control_frame, text="Status: Disconnected", foreground="red")
        self.status_label.grid(row=0, column=4, padx=20)

        # Converter selection
        ttk.Label(control_frame, text="Select Converter:").grid(row=0, column=5, padx=5)
        self.converter_select = ttk.Combobox(control_frame,
                                            values=['DCDC_Primary', 'DCDC_Primary_1', 'DCDC_Primary_2'],
                                            width=20)
        self.converter_select.set(self.selected_converter)
        self.converter_select.bind('<<ComboboxSelected>>', self.on_converter_changed)
        self.converter_select.grid(row=0, column=6, padx=5)

        # Main content area with tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.grid(row=1, column=0, columnspan=2, sticky=(tk.N, tk.S, tk.E, tk.W), padx=10, pady=10)

        # Tab 1: Real-time monitoring
        self.monitoring_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.monitoring_tab, text="Real-time Monitoring")
        self.setup_monitoring_tab()

        # Tab 2: Data visualization
        self.visualization_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.visualization_tab, text="Data Visualization")
        self.setup_visualization_tab()

        # Tab 3: All converters overview
        self.overview_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.overview_tab, text="All Converters")
        self.setup_overview_tab()

        # Tab 4: Configuration
        self.config_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.config_tab, text="Configuration")
        self.setup_config_tab()

        # Bottom status bar
        status_frame = ttk.Frame(self.root)
        status_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E))

        self.msg_count_label = ttk.Label(status_frame, text="Messages: 0")
        self.msg_count_label.pack(side=tk.LEFT, padx=10)

        self.log_status_label = ttk.Label(status_frame, text="Logging: Off")
        self.log_status_label.pack(side=tk.LEFT, padx=10)

        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)

    def create_menu(self):
        """Create application menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Export Data...", command=self.export_data)
        file_menu.add_command(label="Load DBC File...", command=self.load_dbc)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)

        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Clear Display", command=self.clear_display)
        view_menu.add_command(label="Refresh", command=self.refresh_display)

        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Start Logging", command=self.start_logging)
        tools_menu.add_command(label="Stop Logging", command=self.stop_logging)
        tools_menu.add_separator()
        tools_menu.add_command(label="Send CAN Message...", command=self.send_can_message_dialog)

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
        help_menu.add_command(label="User Manual", command=self.show_manual)

    def setup_monitoring_tab(self):
        """Setup real-time monitoring display"""
        # Left panel: Parameter values
        left_frame = ttk.LabelFrame(self.monitoring_tab, text="Current Values", padding="10")
        left_frame.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.E, tk.W), padx=5, pady=5)

        # Create scrollable frame for parameters
        canvas = tk.Canvas(left_frame, width=500)
        scrollbar = ttk.Scrollbar(left_frame, orient="vertical", command=canvas.yview)
        self.param_frame = ttk.Frame(canvas)

        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        canvas.create_window((0, 0), window=self.param_frame, anchor=tk.NW)

        self.param_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        # Parameter display widgets
        self.param_labels = {}
        self.create_parameter_displays()

        # Right panel: CAN message log
        right_frame = ttk.LabelFrame(self.monitoring_tab, text="CAN Message Log", padding="10")
        right_frame.grid(row=0, column=1, sticky=(tk.N, tk.S, tk.E, tk.W), padx=5, pady=5)

        # Message list with scrollbar
        self.msg_tree = ttk.Treeview(right_frame, columns=('Time', 'ID', 'Name', 'Data'), show='tree headings')
        self.msg_tree.heading('#0', text='#')
        self.msg_tree.heading('Time', text='Time')
        self.msg_tree.heading('ID', text='CAN ID')
        self.msg_tree.heading('Name', text='Message')
        self.msg_tree.heading('Data', text='Data')

        self.msg_tree.column('#0', width=50)
        self.msg_tree.column('Time', width=100)
        self.msg_tree.column('ID', width=100)
        self.msg_tree.column('Name', width=200)
        self.msg_tree.column('Data', width=150)

        msg_scrollbar = ttk.Scrollbar(right_frame, orient=tk.VERTICAL, command=self.msg_tree.yview)
        self.msg_tree.configure(yscrollcommand=msg_scrollbar.set)

        self.msg_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        msg_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Configure grid
        self.monitoring_tab.columnconfigure(0, weight=1)
        self.monitoring_tab.columnconfigure(1, weight=1)
        self.monitoring_tab.rowconfigure(0, weight=1)

    def create_parameter_displays(self):
        """Create display widgets for all monitored parameters"""
        parameters = [
            ('Input Voltage', 'V', 'input_voltage'),
            ('Input Current', 'A', 'input_current'),
            ('Input Power', 'W', 'input_power'),
            ('Output Voltage', 'V', 'output_voltage'),
            ('Output Current', 'A', 'output_current'),
            ('Output Power', 'W', 'output_power'),
            ('Efficiency', '%', 'efficiency'),
            ('Temperature 1', '°C', 'temp_1'),
            ('Temperature 2', '°C', 'temp_2'),
            ('Status', '', 'status'),
            ('Error Code', '', 'error_code'),
            ('Operating Mode', '', 'mode'),
        ]

        for idx, (name, unit, key) in enumerate(parameters):
            # Label
            label = ttk.Label(self.param_frame, text=f"{name}:", font=('Arial', 10, 'bold'))
            label.grid(row=idx, column=0, sticky=tk.W, padx=5, pady=3)

            # Value
            value_label = ttk.Label(self.param_frame, text="--", font=('Arial', 12))
            value_label.grid(row=idx, column=1, sticky=tk.W, padx=10, pady=3)

            # Unit
            if unit:
                unit_label = ttk.Label(self.param_frame, text=unit, font=('Arial', 10))
                unit_label.grid(row=idx, column=2, sticky=tk.W, padx=5, pady=3)

            self.param_labels[key] = value_label

    def setup_visualization_tab(self):
        """Setup data visualization tab"""
        ttk.Label(self.visualization_tab, text="Data visualization charts will be displayed here",
                 font=('Arial', 12)).pack(pady=100)

        plot_frame = ttk.Frame(self.visualization_tab)
        plot_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        ttk.Button(plot_frame, text="Plot Voltage Over Time",
                  command=lambda: self.plot_parameter('voltage')).pack(pady=5)
        ttk.Button(plot_frame, text="Plot Current Over Time",
                  command=lambda: self.plot_parameter('current')).pack(pady=5)
        ttk.Button(plot_frame, text="Plot Power Over Time",
                  command=lambda: self.plot_parameter('power')).pack(pady=5)
        ttk.Button(plot_frame, text="Plot Efficiency",
                  command=lambda: self.plot_parameter('efficiency')).pack(pady=5)

    def setup_overview_tab(self):
        """Setup overview tab showing all converters"""
        # Create a grid showing all three converters side by side
        for idx, converter_name in enumerate(['DCDC_Primary', 'DCDC_Primary_1', 'DCDC_Primary_2']):
            frame = ttk.LabelFrame(self.overview_tab, text=converter_name, padding="10")
            frame.grid(row=0, column=idx, sticky=(tk.N, tk.S, tk.E, tk.W), padx=5, pady=5)

            # Mini display for each converter
            info_text = tk.Text(frame, width=30, height=20, font=('Courier', 9))
            info_text.pack(fill=tk.BOTH, expand=True)
            info_text.insert('1.0', f"{converter_name}\n\nWaiting for data...")
            info_text.config(state=tk.DISABLED)

        self.overview_tab.columnconfigure(0, weight=1)
        self.overview_tab.columnconfigure(1, weight=1)
        self.overview_tab.columnconfigure(2, weight=1)

    def setup_config_tab(self):
        """Setup configuration tab"""
        config_frame = ttk.Frame(self.config_tab, padding="20")
        config_frame.pack(fill=tk.BOTH, expand=True)

        # CAN configuration
        ttk.Label(config_frame, text="CAN Bus Configuration", font=('Arial', 12, 'bold')).grid(row=0, column=0, columnspan=2, pady=10)

        ttk.Label(config_frame, text="Bitrate:").grid(row=1, column=0, sticky=tk.W, pady=5)
        bitrate_entry = ttk.Entry(config_frame, width=20)
        bitrate_entry.insert(0, self.config.get('can_bitrate', '500000'))
        bitrate_entry.grid(row=1, column=1, pady=5)

        # DBC file
        ttk.Label(config_frame, text="DBC File:").grid(row=2, column=0, sticky=tk.W, pady=5)
        dbc_entry = ttk.Entry(config_frame, width=40)
        dbc_entry.insert(0, self.config.get('dbc_file', 'DCDC_COMETI_Primary_Customer_001_3units.dbc'))
        dbc_entry.grid(row=2, column=1, pady=5)

        ttk.Button(config_frame, text="Browse...", command=lambda: self.browse_file(dbc_entry)).grid(row=2, column=2, padx=5)

        # Logging configuration
        ttk.Label(config_frame, text="Data Logging", font=('Arial', 12, 'bold')).grid(row=3, column=0, columnspan=2, pady=(20, 10))

        ttk.Label(config_frame, text="Log Directory:").grid(row=4, column=0, sticky=tk.W, pady=5)
        log_dir_entry = ttk.Entry(config_frame, width=40)
        log_dir_entry.insert(0, self.config.get('log_directory', './logs'))
        log_dir_entry.grid(row=4, column=1, pady=5)

        ttk.Button(config_frame, text="Browse...", command=lambda: self.browse_directory(log_dir_entry)).grid(row=4, column=2, padx=5)

        # Save button
        ttk.Button(config_frame, text="Save Configuration",
                  command=lambda: self.save_configuration({
                      'can_bitrate': bitrate_entry.get(),
                      'dbc_file': dbc_entry.get(),
                      'log_directory': log_dir_entry.get()
                  })).grid(row=5, column=0, columnspan=3, pady=20)

    def start_monitoring(self):
        """Start CAN bus monitoring"""
        interface = self.can_interface.get()

        try:
            self.can_handler.connect(interface)
            self.is_monitoring = True

            # Update UI
            self.start_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)
            self.status_label.config(text=f"Status: Connected to {interface}", foreground="green")

            # Start receiver thread
            self.receiver_thread = threading.Thread(target=self.receive_messages, daemon=True)
            self.receiver_thread.start()

            messagebox.showinfo("Success", f"Connected to {interface}")

        except Exception as e:
            messagebox.showerror("Connection Error", f"Failed to connect to {interface}:\n{str(e)}")

    def stop_monitoring(self):
        """Stop CAN bus monitoring"""
        self.is_monitoring = False
        self.can_handler.disconnect()

        # Update UI
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.status_label.config(text="Status: Disconnected", foreground="red")

    def receive_messages(self):
        """Background thread to receive CAN messages"""
        while self.is_monitoring:
            try:
                message = self.can_handler.receive_message(timeout=0.1)
                if message:
                    self.message_queue.put(message)
            except Exception as e:
                print(f"Error receiving message: {e}")

    def update_display(self):
        """Update display with latest data"""
        try:
            # Process messages from queue
            while not self.message_queue.empty():
                message = self.message_queue.get_nowait()
                self.process_message(message)

        except queue.Empty:
            pass

        # Schedule next update
        self.root.after(100, self.update_display)

    def process_message(self, message: CANMessage):
        """Process a received CAN message"""
        # Update message log
        self.add_message_to_log(message)

        # Update converter data
        if message.data:
            converter = self.identify_converter(message.can_id)
            if converter:
                self.converter_data[converter].update(message.data)

        # Update displays if showing this converter
        if self.identify_converter(message.can_id) == self.selected_converter:
            self.update_parameter_display(message.data)

    def add_message_to_log(self, message: CANMessage):
        """Add message to the log display"""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]

        self.msg_tree.insert('', 0, text=len(self.msg_tree.get_children()) + 1,
                            values=(timestamp, hex(message.can_id), message.name,
                                   message.data_hex))

        # Keep only last 100 messages
        children = self.msg_tree.get_children()
        if len(children) > 100:
            self.msg_tree.delete(children[-1])

    def update_parameter_display(self, data: Dict):
        """Update parameter display with new data"""
        for key, value in data.items():
            if key in self.param_labels:
                if isinstance(value, float):
                    self.param_labels[key].config(text=f"{value:.2f}")
                else:
                    self.param_labels[key].config(text=str(value))

    def identify_converter(self, can_id: int) -> Optional[str]:
        """Identify which converter a CAN ID belongs to"""
        # Based on CAN ID ranges from DBC file
        # DCDC_Primary: base IDs
        # DCDC_Primary_1: base + 1
        # DCDC_Primary_2: base + 2

        base_ids = [2148532224, 2148532480, 2148532736]  # Example base IDs

        for base_id in base_ids:
            if can_id == base_id:
                return 'DCDC_Primary'
            elif can_id == base_id + 1:
                return 'DCDC_Primary_1'
            elif can_id == base_id + 2:
                return 'DCDC_Primary_2'

        return None

    def on_converter_changed(self, event):
        """Handle converter selection change"""
        self.selected_converter = self.converter_select.get()
        self.refresh_display()

    def clear_display(self):
        """Clear all displays"""
        for item in self.msg_tree.get_children():
            self.msg_tree.delete(item)

    def refresh_display(self):
        """Refresh all displays"""
        data = self.converter_data.get(self.selected_converter, {})
        self.update_parameter_display(data)

    def start_logging(self):
        """Start data logging"""
        try:
            self.data_logger.start_logging()
            self.log_status_label.config(text="Logging: Active", foreground="green")
            messagebox.showinfo("Logging", "Data logging started")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start logging: {e}")

    def stop_logging(self):
        """Stop data logging"""
        self.data_logger.stop_logging()
        self.log_status_label.config(text="Logging: Off", foreground="gray")
        messagebox.showinfo("Logging", "Data logging stopped")

    def export_data(self):
        """Export logged data to file"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("JSON files", "*.json"), ("All files", "*.*")]
        )

        if filename:
            try:
                self.data_logger.export_data(filename)
                messagebox.showinfo("Success", f"Data exported to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Export failed: {e}")

    def load_dbc(self):
        """Load DBC file"""
        filename = filedialog.askopenfilename(
            filetypes=[("DBC files", "*.dbc"), ("All files", "*.*")]
        )

        if filename:
            try:
                self.can_handler.load_dbc(filename)
                self.config.set('dbc_file', filename)
                messagebox.showinfo("Success", f"Loaded DBC file: {Path(filename).name}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load DBC: {e}")

    def send_can_message_dialog(self):
        """Show dialog to send custom CAN message"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Send CAN Message")
        dialog.geometry("400x250")

        ttk.Label(dialog, text="CAN ID (hex):").grid(row=0, column=0, padx=10, pady=10)
        id_entry = ttk.Entry(dialog, width=20)
        id_entry.grid(row=0, column=1, padx=10, pady=10)

        ttk.Label(dialog, text="Data (hex):").grid(row=1, column=0, padx=10, pady=10)
        data_entry = ttk.Entry(dialog, width=20)
        data_entry.grid(row=1, column=1, padx=10, pady=10)

        def send():
            try:
                can_id = int(id_entry.get(), 16)
                data = bytes.fromhex(data_entry.get())
                self.can_handler.send_message(can_id, data)
                messagebox.showinfo("Success", "Message sent")
                dialog.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to send: {e}")

        ttk.Button(dialog, text="Send", command=send).grid(row=2, column=0, columnspan=2, pady=20)

    def plot_parameter(self, param_type):
        """Plot parameter over time"""
        messagebox.showinfo("Visualization",
                          f"Plotting {param_type} data...\n\n"
                          "Note: Install matplotlib for advanced plotting:\n"
                          "pip install matplotlib")

    def browse_file(self, entry_widget):
        """Browse for file"""
        filename = filedialog.askopenfilename()
        if filename:
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, filename)

    def browse_directory(self, entry_widget):
        """Browse for directory"""
        dirname = filedialog.askdirectory()
        if dirname:
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, dirname)

    def save_configuration(self, config_dict):
        """Save configuration"""
        for key, value in config_dict.items():
            self.config.set(key, value)
        self.config.save()
        messagebox.showinfo("Success", "Configuration saved")

    def show_about(self):
        """Show about dialog"""
        messagebox.showinfo("About",
                          "DC-DC Converter Monitor v1.0\n\n"
                          "Real-time monitoring application for TAME-POWER\n"
                          "COMETi DC-DC converters via CAN bus\n\n"
                          "© 2026")

    def show_manual(self):
        """Show user manual"""
        messagebox.showinfo("User Manual",
                          "Quick Start:\n\n"
                          "1. Select CAN interface (e.g., can0)\n"
                          "2. Click 'Start Monitoring'\n"
                          "3. View real-time data in tabs\n"
                          "4. Use 'Tools' menu for logging\n"
                          "5. Export data from File menu\n\n"
                          "See COMETi UserManual.pdf for details")


def main():
    """Main entry point"""
    root = tk.Tk()
    app = DCDCMonitorApp(root)
    root.mainloop()


if __name__ == '__main__':
    main()

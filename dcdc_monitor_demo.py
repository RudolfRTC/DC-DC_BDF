#!/usr/bin/env python3
"""
DC-DC Monitor - DEMO MODE
Works without external dependencies (python-can, cantools)
Simulates CAN data for demonstration purposes
"""

import sys

# Check if tkinter is available
try:
    import tkinter as tk
    from tkinter import ttk, messagebox
    HAS_TKINTER = True
except ImportError:
    HAS_TKINTER = False

from datetime import datetime
from pathlib import Path
import threading
import queue
import random
import time
from typing import Dict, List


class DemoCANSimulator:
    """Simulates CAN messages for demo purposes"""

    def __init__(self):
        self.running = False
        self.message_id = 0

    def generate_message(self, converter_id=0):
        """Generate simulated CAN message"""
        base_voltage = 400 + random.uniform(-20, 20)
        base_current = 50 + random.uniform(-5, 5)

        can_id = 0x18FF50E5 + converter_id

        data = {
            'input_voltage': base_voltage + random.uniform(-10, 10),
            'input_current': base_current + random.uniform(-2, 2),
            'output_voltage': 350 + random.uniform(-15, 15),
            'output_current': base_current * 1.2 + random.uniform(-3, 3),
            'efficiency': 94 + random.uniform(-2, 3),
            'temp_1': 45 + random.uniform(-5, 15),
            'temp_2': 42 + random.uniform(-5, 15),
            'status': 'Running',
            'error_code': 0,
        }

        # Calculate power
        data['input_power'] = data['input_voltage'] * data['input_current']
        data['output_power'] = data['output_voltage'] * data['output_current']

        return {
            'can_id': can_id,
            'name': f'DCDC_Status_{converter_id}',
            'data': data,
            'timestamp': time.time()
        }


class DCDCMonitorDemo:
    """Demo application with simulated data"""

    def __init__(self, root):
        self.root = root
        self.root.title("DC-DC Monitor - DEMO MODE")
        self.root.geometry("1200x800")

        # State
        self.is_running = False
        self.message_count = 0
        self.simulator = DemoCANSimulator()
        self.message_queue = queue.Queue()

        # Data storage
        self.converter_data = {
            'DCDC_Primary': {},
            'DCDC_Primary_1': {},
            'DCDC_Primary_2': {}
        }

        self.selected_converter = 'DCDC_Primary'
        self.param_labels = {}

        # Setup UI
        self.setup_ui()

        # Start display update loop
        self.update_display()

    def setup_ui(self):
        """Create user interface"""
        # Top banner
        banner = ttk.Label(
            self.root,
            text="⚠️  DEMO MODE - Simulated Data  ⚠️",
            font=('Arial', 12, 'bold'),
            background='#FFD700',
            foreground='#000000'
        )
        banner.pack(fill=tk.X, pady=5)

        # Control panel
        control_frame = ttk.Frame(self.root, padding="10")
        control_frame.pack(fill=tk.X)

        self.start_btn = ttk.Button(
            control_frame,
            text="▶ Start Simulation",
            command=self.start_simulation
        )
        self.start_btn.pack(side=tk.LEFT, padx=5)

        self.stop_btn = ttk.Button(
            control_frame,
            text="⏸ Stop",
            command=self.stop_simulation,
            state=tk.DISABLED
        )
        self.stop_btn.pack(side=tk.LEFT, padx=5)

        self.status_label = ttk.Label(
            control_frame,
            text="Status: Stopped",
            foreground="red"
        )
        self.status_label.pack(side=tk.LEFT, padx=20)

        self.msg_count_label = ttk.Label(
            control_frame,
            text="Messages: 0"
        )
        self.msg_count_label.pack(side=tk.LEFT, padx=20)

        # Converter selector
        ttk.Label(control_frame, text="Converter:").pack(side=tk.LEFT, padx=5)
        self.converter_select = ttk.Combobox(
            control_frame,
            values=['DCDC_Primary', 'DCDC_Primary_1', 'DCDC_Primary_2'],
            width=20
        )
        self.converter_select.set(self.selected_converter)
        self.converter_select.bind('<<ComboboxSelected>>', self.on_converter_changed)
        self.converter_select.pack(side=tk.LEFT, padx=5)

        # Main notebook
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Tab 1: Real-time data
        self.data_tab = ttk.Frame(notebook)
        notebook.add(self.data_tab, text="Real-time Data")
        self.setup_data_tab()

        # Tab 2: All converters
        self.overview_tab = ttk.Frame(notebook)
        notebook.add(self.overview_tab, text="All Converters")
        self.setup_overview_tab()

        # Status bar
        status_bar = ttk.Label(
            self.root,
            text="Demo mode: No CAN hardware required | Data is simulated",
            relief=tk.SUNKEN
        )
        status_bar.pack(fill=tk.X, side=tk.BOTTOM)

    def setup_data_tab(self):
        """Setup real-time data display"""
        # Parameter display
        param_frame = ttk.LabelFrame(self.data_tab, text="Current Values", padding="10")
        param_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

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
        ]

        for idx, (name, unit, key) in enumerate(parameters):
            row = idx // 2
            col = (idx % 2) * 3

            ttk.Label(
                param_frame,
                text=f"{name}:",
                font=('Arial', 10, 'bold')
            ).grid(row=row, column=col, sticky=tk.W, padx=5, pady=5)

            value_label = ttk.Label(
                param_frame,
                text="--",
                font=('Arial', 12)
            )
            value_label.grid(row=row, column=col+1, sticky=tk.W, padx=10, pady=5)

            if unit:
                ttk.Label(
                    param_frame,
                    text=unit,
                    font=('Arial', 10)
                ).grid(row=row, column=col+2, sticky=tk.W, padx=5, pady=5)

            self.param_labels[key] = value_label

    def setup_overview_tab(self):
        """Setup overview display"""
        self.overview_widgets = {}

        for idx, converter_name in enumerate(['DCDC_Primary', 'DCDC_Primary_1', 'DCDC_Primary_2']):
            frame = ttk.LabelFrame(self.overview_tab, text=converter_name, padding="10")
            frame.grid(row=0, column=idx, sticky=(tk.N, tk.S, tk.E, tk.W), padx=5, pady=5)

            text_widget = tk.Text(frame, width=35, height=15, font=('Courier', 10))
            text_widget.pack(fill=tk.BOTH, expand=True)
            text_widget.insert('1.0', f"{converter_name}\n\nWaiting for data...")
            text_widget.config(state=tk.DISABLED)

            self.overview_widgets[converter_name] = text_widget

        self.overview_tab.columnconfigure(0, weight=1)
        self.overview_tab.columnconfigure(1, weight=1)
        self.overview_tab.columnconfigure(2, weight=1)

    def start_simulation(self):
        """Start data simulation"""
        self.is_running = True
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.status_label.config(text="Status: Running (Simulated)", foreground="green")

        # Start simulation thread
        self.sim_thread = threading.Thread(target=self.simulation_loop, daemon=True)
        self.sim_thread.start()

    def stop_simulation(self):
        """Stop data simulation"""
        self.is_running = False
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.status_label.config(text="Status: Stopped", foreground="red")

    def simulation_loop(self):
        """Generate simulated messages"""
        while self.is_running:
            # Generate messages for all 3 converters
            for converter_id in range(3):
                message = self.simulator.generate_message(converter_id)
                self.message_queue.put(message)

            time.sleep(0.5)  # 2 Hz update rate

    def update_display(self):
        """Update display with latest data"""
        try:
            # Process all messages in queue
            while not self.message_queue.empty():
                message = self.message_queue.get_nowait()
                self.process_message(message)

        except queue.Empty:
            pass

        # Schedule next update
        self.root.after(100, self.update_display)

    def process_message(self, message):
        """Process simulated message"""
        # Identify converter
        converter_id = message['can_id'] - 0x18FF50E5
        converter_names = ['DCDC_Primary', 'DCDC_Primary_1', 'DCDC_Primary_2']

        if 0 <= converter_id < len(converter_names):
            converter = converter_names[converter_id]
            self.converter_data[converter].update(message['data'])

            # Update message counter
            self.message_count += 1
            self.msg_count_label.config(text=f"Messages: {self.message_count}")

            # Update selected converter display
            if converter == self.selected_converter:
                self.update_parameter_display(message['data'])

            # Update overview (throttled)
            if self.message_count % 3 == 0:
                self.update_overview_display()

    def update_parameter_display(self, data):
        """Update parameter labels"""
        for key, value in data.items():
            if key in self.param_labels:
                if isinstance(value, (int, float)):
                    self.param_labels[key].config(text=f"{value:.1f}")
                else:
                    self.param_labels[key].config(text=str(value))

    def update_overview_display(self):
        """Update overview tab"""
        for converter_name, data in self.converter_data.items():
            if converter_name in self.overview_widgets and data:
                text_widget = self.overview_widgets[converter_name]

                display_text = f"{converter_name}\n{'='*30}\n\n"
                display_text += f"Input:  {data.get('input_voltage', 0):.1f}V  {data.get('input_current', 0):.1f}A\n"
                display_text += f"Output: {data.get('output_voltage', 0):.1f}V  {data.get('output_current', 0):.1f}A\n"
                display_text += f"Power:  {data.get('output_power', 0):.0f}W\n"
                display_text += f"Eff:    {data.get('efficiency', 0):.1f}%\n"
                display_text += f"Temp:   {data.get('temp_1', 0):.0f}°C / {data.get('temp_2', 0):.0f}°C\n"
                display_text += f"Status: {data.get('status', 'Unknown')}\n"

                text_widget.config(state=tk.NORMAL)
                text_widget.delete('1.0', tk.END)
                text_widget.insert('1.0', display_text)
                text_widget.config(state=tk.DISABLED)

    def on_converter_changed(self, event):
        """Handle converter selection"""
        self.selected_converter = self.converter_select.get()
        data = self.converter_data.get(self.selected_converter, {})
        self.update_parameter_display(data)


def main():
    """Main entry point"""
    if not HAS_TKINTER:
        print("=" * 70)
        print("ERROR: tkinter not found")
        print("=" * 70)
        print()
        print("This demo requires tkinter (Python's standard GUI library).")
        print()
        print("Install it with:")
        print("  Ubuntu/Debian: sudo apt-get install python3-tk")
        print("  Fedora/RHEL:   sudo dnf install python3-tkinter")
        print("  macOS:         Usually included with Python")
        print()
        print("=" * 70)
        return 1

    print("=" * 70)
    print("DC-DC Monitor - DEMO MODE")
    print("=" * 70)
    print()
    print("Starting demo with simulated data...")
    print("No CAN hardware or external dependencies required.")
    print()

    root = tk.Tk()
    app = DCDCMonitorDemo(root)
    root.mainloop()

    return 0


if __name__ == '__main__':
    sys.exit(main())

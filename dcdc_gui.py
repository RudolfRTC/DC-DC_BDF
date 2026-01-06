#!/usr/bin/env python3
"""
DC-DC Converter GUI Control Application
Graphical interface for controlling DC-DC converters via CAN bus
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
from dcdc_controller import (
    DCDCController, ConverterMode, ControlType,
    SoftwareMode, RequestedInfo
)


class DCDCGui:
    """GUI for DC-DC Converter Control"""

    def __init__(self, root, dbc_file='DCDC_COMETI_Primary_Customer_001_3units.dbc',
                 can_interface='vcan0', dcdc_id=0):
        """Initialize GUI"""
        self.root = root
        self.root.title(f"DC-DC Converter Control - Unit {dcdc_id}")
        self.root.geometry("1400x800")

        # Initialize controller
        try:
            self.controller = DCDCController(dbc_file, can_interface, dcdc_id=dcdc_id)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to initialize controller: {e}")
            root.destroy()
            return

        # Variables for measurements
        self.measurements = {
            'vBus1': tk.StringVar(value="0.00"),
            'vBus2': tk.StringVar(value="0.00"),
            'iBus1': tk.StringVar(value="0.00"),
            'iBus2': tk.StringVar(value="0.00"),
            'pBus1': tk.StringVar(value="0.00"),
            'pBus2': tk.StringVar(value="0.00"),
        }

        # Temperature variables
        self.temperatures = {
            'TempMaxTransfo': tk.StringVar(value="0.00"),
            'TempMaxMosfetPSFB': tk.StringVar(value="0.00"),
            'TempMaxMosfetBoost': tk.StringVar(value="0.00"),
            'TempMaxSelfBoost': tk.StringVar(value="0.00"),
            'TempMaxMosfetSecondary': tk.StringVar(value="0.00"),
            'TempMaxCooling': tk.StringVar(value="0.00"),
            'TempAmbiant': tk.StringVar(value="0.00"),
        }

        # Status variables
        self.software_mode = tk.StringVar(value="Unknown")
        self.regulation_type = tk.StringVar(value="Unknown")
        self.regulation_mode = tk.StringVar(value="Unknown")
        self.setpoint_display = tk.StringVar(value="0.0")
        self.current_limit_display = tk.StringVar(value="0.0")

        # Control variables
        self.setpoint_input = tk.StringVar(value="24")
        self.current_limit_input = tk.StringVar(value="200")
        self.control_type_var = tk.StringVar(value="vBus2")
        self.control_mode_var = tk.StringVar(value="Bus1ToBus2")

        # Build GUI
        self.build_gui()

        # Start update thread
        self.running = True
        self.update_thread = threading.Thread(target=self.update_loop, daemon=True)
        self.update_thread.start()

        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def build_gui(self):
        """Build the GUI layout"""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Left side - Measurements
        self.build_measurements_section(main_frame)

        # Center - Status and Control
        self.build_status_section(main_frame)
        self.build_control_section(main_frame)

        # Right side - Errors and Warnings
        self.build_errors_section(main_frame)

    def build_measurements_section(self, parent):
        """Build measurements display section"""
        frame = ttk.LabelFrame(parent, text="Measurements", padding="10")
        frame.grid(row=0, column=0, rowspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5)

        # Voltage, Current, Power
        measurements = [
            ('vBus1', 'V'), ('vBus2', 'V'),
            ('iBus1', 'A'), ('iBus2', 'A'),
            ('pBus1', 'W'), ('pBus2', 'W')
        ]

        for idx, (name, unit) in enumerate(measurements):
            row = idx // 2
            col = idx % 2

            measure_frame = ttk.Frame(frame)
            measure_frame.grid(row=row, column=col, padx=5, pady=5)

            ttk.Label(measure_frame, text=name, font=('Arial', 10, 'bold')).pack()
            value_label = ttk.Label(
                measure_frame,
                textvariable=self.measurements[name],
                font=('Arial', 16),
                background='black',
                foreground='lime',
                relief='sunken',
                padding=10
            )
            value_label.pack()
            ttk.Label(measure_frame, text=unit).pack()

    def build_status_section(self, parent):
        """Build status display section"""
        frame = ttk.LabelFrame(parent, text="Status", padding="10")
        frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)

        # Software Mode
        mode_frame = ttk.Frame(frame, relief='sunken', borderwidth=2)
        mode_frame.grid(row=0, column=0, padx=5, pady=5, sticky=(tk.W, tk.E))
        ttk.Label(mode_frame, text="Software Mode:", font=('Arial', 10)).pack()
        ttk.Label(
            mode_frame,
            textvariable=self.software_mode,
            font=('Arial', 14, 'bold'),
            background='lightblue',
            padding=10
        ).pack(fill='x')

        # Regulation Type
        reg_type_frame = ttk.Frame(frame, relief='sunken', borderwidth=2)
        reg_type_frame.grid(row=0, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
        ttk.Label(reg_type_frame, text="Regulation Type:", font=('Arial', 10)).pack()
        ttk.Label(
            reg_type_frame,
            textvariable=self.regulation_type,
            font=('Arial', 14, 'bold'),
            background='lightgreen',
            padding=10
        ).pack(fill='x')

        # Regulation Mode
        reg_mode_frame = ttk.Frame(frame, relief='sunken', borderwidth=2)
        reg_mode_frame.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky=(tk.W, tk.E))
        ttk.Label(reg_mode_frame, text="Regulation Mode:", font=('Arial', 10)).pack()
        ttk.Label(
            reg_mode_frame,
            textvariable=self.regulation_mode,
            font=('Arial', 14, 'bold'),
            background='lightgreen',
            padding=10
        ).pack(fill='x')

        # Setpoint and Current Limit
        info_frame = ttk.Frame(frame)
        info_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)

        ttk.Label(info_frame, text="Setpoint:").grid(row=0, column=0, sticky=tk.W)
        ttk.Label(
            info_frame,
            textvariable=self.setpoint_display,
            font=('Arial', 12, 'bold')
        ).grid(row=0, column=1, sticky=tk.W)

        ttk.Label(info_frame, text="Current Limit:").grid(row=1, column=0, sticky=tk.W)
        ttk.Label(
            info_frame,
            textvariable=self.current_limit_display,
            font=('Arial', 12, 'bold')
        ).grid(row=1, column=1, sticky=tk.W)

        # Temperatures
        temp_frame = ttk.LabelFrame(parent, text="Temperatures", padding="10")
        temp_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)

        temp_names = [
            ('TempMaxTransfo', 'Max Transfos'),
            ('TempMaxMosfetPSFB', 'Max Mos PSFB'),
            ('TempMaxSelfBoost', 'Max Self PSFB'),
            ('TempMaxMosfetBoost', 'Max Mos Boost'),
            ('TempMaxMosfetSecondary', 'Max Mos Second'),
            ('TempMaxCooling', 'Max Cooling'),
            ('TempAmbiant', 'Ambient'),
        ]

        for idx, (var_name, display_name) in enumerate(temp_names):
            row = idx // 2
            col = idx % 2

            temp_item = ttk.Frame(temp_frame)
            temp_item.grid(row=row, column=col, padx=5, pady=3)

            ttk.Label(temp_item, text=display_name, width=15).pack(side='left')
            ttk.Label(
                temp_item,
                textvariable=self.temperatures[var_name],
                font=('Arial', 12),
                background='black',
                foreground='orange',
                relief='sunken',
                padding=5,
                width=8
            ).pack(side='left')
            ttk.Label(temp_item, text="°C").pack(side='left')

    def build_control_section(self, parent):
        """Build control section"""
        frame = ttk.LabelFrame(parent, text="Control", padding="10")
        frame.grid(row=2, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)

        # Control Type
        ttk.Label(frame, text="Control Type:").grid(row=0, column=0, sticky=tk.W, pady=5)
        control_type_combo = ttk.Combobox(
            frame,
            textvariable=self.control_type_var,
            values=['vBus1', 'vBus2', 'iBus1', 'iBus2', 'pBus1', 'pBus2',
                   'vBus1ILim', 'vBus2ILim'],
            state='readonly',
            width=15
        )
        control_type_combo.grid(row=0, column=1, pady=5)

        # Control Mode
        ttk.Label(frame, text="Control Mode:").grid(row=1, column=0, sticky=tk.W, pady=5)
        control_mode_combo = ttk.Combobox(
            frame,
            textvariable=self.control_mode_var,
            values=['Bus1ToBus2', 'Bus2ToBus1', 'Bidirectional'],
            state='readonly',
            width=15
        )
        control_mode_combo.grid(row=1, column=1, pady=5)

        # Setpoint
        ttk.Label(frame, text="Setpoint:").grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Entry(frame, textvariable=self.setpoint_input, width=17).grid(row=2, column=1, pady=5)

        # Current Limit
        ttk.Label(frame, text="Current Limit (A):").grid(row=3, column=0, sticky=tk.W, pady=5)
        ttk.Entry(frame, textvariable=self.current_limit_input, width=17).grid(row=3, column=1, pady=5)

        # Buttons
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=10)

        ttk.Button(
            button_frame,
            text="Start Converter",
            command=self.start_converter,
            style='Green.TButton'
        ).grid(row=0, column=0, padx=5, pady=5, sticky=(tk.W, tk.E))

        ttk.Button(
            button_frame,
            text="Stop Converter",
            command=self.stop_converter
        ).grid(row=0, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))

        ttk.Button(
            button_frame,
            text="Reset Errors",
            command=self.reset_errors,
            style='Red.TButton'
        ).grid(row=1, column=0, padx=5, pady=5, sticky=(tk.W, tk.E))

        ttk.Button(
            button_frame,
            text="Update Setpoint",
            command=self.update_setpoint
        ).grid(row=1, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))

    def build_errors_section(self, parent):
        """Build errors and warnings section"""
        frame = ttk.LabelFrame(parent, text="Errors & Warnings", padding="10")
        frame.grid(row=0, column=2, rowspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5)

        # Critical Errors
        ttk.Label(frame, text="Critical Errors:", font=('Arial', 10, 'bold')).pack(anchor='w')
        self.critical_errors_text = tk.Text(frame, height=8, width=30, bg='#FFE0E0')
        self.critical_errors_text.pack(fill='both', expand=True, pady=5)

        # Functional Errors
        ttk.Label(frame, text="Functional Errors:", font=('Arial', 10, 'bold')).pack(anchor='w')
        self.functional_errors_text = tk.Text(frame, height=8, width=30, bg='#FFFFE0')
        self.functional_errors_text.pack(fill='both', expand=True, pady=5)

        # Warnings
        ttk.Label(frame, text="Warnings:", font=('Arial', 10, 'bold')).pack(anchor='w')
        self.warnings_text = tk.Text(frame, height=8, width=30, bg='#E0E0FF')
        self.warnings_text.pack(fill='both', expand=True, pady=5)

    def start_converter(self):
        """Start converter button handler"""
        try:
            setpoint = float(self.setpoint_input.get())
            current_limit = float(self.current_limit_input.get())

            # Map control type
            control_map = {
                'vBus1': ControlType.V_BUS1,
                'vBus2': ControlType.V_BUS2,
                'iBus1': ControlType.I_BUS1,
                'iBus2': ControlType.I_BUS2,
                'pBus1': ControlType.P_BUS1,
                'pBus2': ControlType.P_BUS2,
                'vBus1ILim': ControlType.V_BUS1_ILIM,
                'vBus2ILim': ControlType.V_BUS2_ILIM,
            }

            mode_map = {
                'Bus1ToBus2': ConverterMode.BUS1_TO_BUS2,
                'Bus2ToBus1': ConverterMode.BUS2_TO_BUS1,
                'Bidirectional': ConverterMode.BIDIRECTIONAL,
            }

            control_type = control_map[self.control_type_var.get()]
            converter_mode = mode_map[self.control_mode_var.get()]

            self.controller.start_converter(
                setpoint=setpoint,
                control_type=control_type,
                converter_mode=converter_mode,
                current_limit=current_limit
            )

            messagebox.showinfo("Success", "Converter started")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to start converter: {e}")

    def stop_converter(self):
        """Stop converter button handler"""
        try:
            self.controller.stop_converter()
            messagebox.showinfo("Success", "Converter stopped")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to stop converter: {e}")

    def update_setpoint(self):
        """Update setpoint button handler"""
        try:
            setpoint = float(self.setpoint_input.get())
            current_limit = float(self.current_limit_input.get())
            self.controller.set_setpoint(setpoint, current_limit)
            messagebox.showinfo("Success", "Setpoint updated")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update setpoint: {e}")

    def reset_errors(self):
        """Reset errors button handler"""
        try:
            self.controller.reset_errors()
            messagebox.showinfo("Success", "Error reset command sent")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to reset errors: {e}")

    def update_loop(self):
        """Background thread to update measurements"""
        while self.running:
            try:
                # Receive messages
                self.controller.receive_messages(timeout=0.1)

                # Update measurements
                measurements = self.controller.get_measurements()

                # Update voltage
                if 'voltage' in measurements:
                    v = measurements['voltage']
                    self.measurements['vBus1'].set(f"{v.get('vBus1', 0):.2f}")
                    self.measurements['vBus2'].set(f"{v.get('vBus2', 0):.2f}")

                # Update current
                if 'current' in measurements:
                    i = measurements['current']
                    self.measurements['iBus1'].set(f"{i.get('iBus1', 0):.2f}")
                    self.measurements['iBus2'].set(f"{i.get('iBus2', 0):.2f}")

                # Update power
                if 'power' in measurements:
                    p = measurements['power']
                    self.measurements['pBus1'].set(f"{p.get('pBus1', 0):.2f}")
                    self.measurements['pBus2'].set(f"{p.get('pBus2', 0):.2f}")

                # Update temperatures
                if 'temperature' in measurements:
                    t = measurements['temperature']
                    for key in self.temperatures:
                        self.temperatures[key].set(f"{t.get(key, 0):.2f}")

                # Update status
                status = self.controller.get_status()
                if 'regulation_info' in status and status['regulation_info']:
                    reg = status['regulation_info']
                    mode = reg.get('softwareMode', 0)
                    self.software_mode.set(SoftwareMode(mode).name)
                    self.setpoint_display.set(f"{reg.get('setpoint', 0)}")

                if 'control_info' in status and status['control_info']:
                    ctrl = status['control_info']
                    ctrl_type = ctrl.get('controlType', 0)
                    conv_mode = ctrl.get('converterMode', 0)
                    self.regulation_type.set(ControlType(ctrl_type).name)
                    self.regulation_mode.set(ConverterMode(conv_mode).name)
                    self.current_limit_display.set(f"{ctrl.get('currentLimit', 0):.1f} A")

                # Update errors
                if 'errors' in status:
                    self.update_errors_display(status['errors'])

                if 'warnings' in status:
                    self.update_warnings_display(status['warnings'])

            except Exception as e:
                print(f"Update error: {e}")

            time.sleep(0.05)  # 20Hz update rate

    def update_errors_display(self, errors):
        """Update errors display"""
        # This is a simplified version - you can expand with bit-by-bit decoding
        critical = errors.get('criticalErrors', 0)
        functional = errors.get('functionalErrors', 0)

        self.critical_errors_text.delete('1.0', tk.END)
        self.critical_errors_text.insert('1.0', f"Error Code: 0x{critical:08X}\n")

        self.functional_errors_text.delete('1.0', tk.END)
        self.functional_errors_text.insert('1.0', f"Error Code: 0x{functional:08X}\n")

    def update_warnings_display(self, warnings):
        """Update warnings display"""
        self.warnings_text.delete('1.0', tk.END)
        self.warnings_text.insert('1.0', f"Warning Code: 0x{warnings:08X}\n")

    def on_closing(self):
        """Handle window closing"""
        self.running = False
        self.update_thread.join(timeout=1.0)
        self.controller.close()
        self.root.destroy()


if __name__ == '__main__':
    root = tk.Tk()

    # Configure styles
    style = ttk.Style()
    style.configure('Green.TButton', background='green')
    style.configure('Red.TButton', background='red')

    # Create GUI
    app = DCDCGui(
        root,
        dbc_file='DCDC_COMETI_Primary_Customer_001_3units.dbc',
        can_interface='vcan0',  # Change to 'can0' for real hardware
        dcdc_id=0  # Change to 1 or 2 for other units
    )

    root.mainloop()

#!/usr/bin/env python3
"""
DC-DC Monitor - Command Line Interface
Works with ZERO external dependencies - only Python standard library
Displays simulated CAN data in terminal
"""

import sys
import time
import random
import threading
from datetime import datetime


class CLIMonitor:
    """Command-line monitor for DC-DC converters"""

    def __init__(self):
        self.running = False
        self.message_count = 0
        self.converter_data = {
            'Converter 1': {},
            'Converter 2': {},
            'Converter 3': {}
        }

    def clear_screen(self):
        """Clear terminal screen"""
        print('\033[2J\033[H', end='')

    def generate_data(self, converter_id):
        """Generate simulated converter data"""
        base_voltage = 400 + random.uniform(-20, 20)
        base_current = 50 + random.uniform(-5, 5)

        data = {
            'input_voltage': base_voltage + random.uniform(-10, 10),
            'input_current': base_current + random.uniform(-2, 2),
            'output_voltage': 350 + random.uniform(-15, 15),
            'output_current': base_current * 1.2 + random.uniform(-3, 3),
            'efficiency': 94 + random.uniform(-2, 3),
            'temp_1': 45 + random.uniform(-5, 15),
            'temp_2': 42 + random.uniform(-5, 15),
            'status': 'Running',
        }

        data['input_power'] = data['input_voltage'] * data['input_current']
        data['output_power'] = data['output_voltage'] * data['output_current']

        return data

    def display_header(self):
        """Display application header"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        print("╔═══════════════════════════════════════════════════════════════════╗")
        print("║       DC-DC Converter Monitor - COMMAND LINE INTERFACE           ║")
        print("║                    DEMO MODE - Simulated Data                     ║")
        print("╚═══════════════════════════════════════════════════════════════════╝")
        print(f"  Time: {timestamp}                       Messages: {self.message_count}")
        print("")

    def display_converter(self, name, data):
        """Display single converter data"""
        if not data:
            print(f"┌─ {name} ────────────────────────────")
            print("│  Waiting for data...")
            print("└──────────────────────────────────────────────────────")
            return

        print(f"┌─ {name} ────────────────────────────")
        print(f"│  Status: {data.get('status', 'Unknown')}")
        print(f"│")
        print(f"│  INPUT")
        print(f"│    Voltage:  {data.get('input_voltage', 0):6.1f} V")
        print(f"│    Current:  {data.get('input_current', 0):6.1f} A")
        print(f"│    Power:    {data.get('input_power', 0):6.0f} W")
        print(f"│")
        print(f"│  OUTPUT")
        print(f"│    Voltage:  {data.get('output_voltage', 0):6.1f} V")
        print(f"│    Current:  {data.get('output_current', 0):6.1f} A")
        print(f"│    Power:    {data.get('output_power', 0):6.0f} W")
        print(f"│")
        print(f"│  EFFICIENCY:  {data.get('efficiency', 0):5.1f} %")
        print(f"│")
        print(f"│  TEMPERATURE")
        print(f"│    Sensor 1:  {data.get('temp_1', 0):5.0f} °C")
        print(f"│    Sensor 2:  {data.get('temp_2', 0):5.0f} °C")
        print("└──────────────────────────────────────────────────────")

    def display_all(self):
        """Display all converters"""
        self.clear_screen()
        self.display_header()

        for name, data in self.converter_data.items():
            self.display_converter(name, data)
            print("")

        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("Press Ctrl+C to stop")

    def simulation_loop(self):
        """Generate simulated data"""
        while self.running:
            # Update data for all converters
            for idx, name in enumerate(self.converter_data.keys()):
                data = self.generate_data(idx)
                self.converter_data[name] = data
                self.message_count += 1

            # Display updated data
            self.display_all()

            # Wait before next update
            time.sleep(2)  # Update every 2 seconds

    def run(self):
        """Run the monitor"""
        print("\n" + "="*70)
        print("DC-DC Converter Monitor - CLI Mode")
        print("="*70)
        print("\nStarting simulation with 3 converters...")
        print("Data updates every 2 seconds")
        print("\nPress Ctrl+C to stop\n")

        time.sleep(2)

        self.running = True

        try:
            self.simulation_loop()
        except KeyboardInterrupt:
            print("\n\n" + "="*70)
            print("Stopping simulation...")
            print(f"Total messages processed: {self.message_count}")
            print("="*70)
            self.running = False


def main():
    """Main entry point"""
    monitor = CLIMonitor()
    monitor.run()
    return 0


if __name__ == '__main__':
    sys.exit(main())

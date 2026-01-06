#!/usr/bin/env python3
"""
Example usage of DC-DC Controller
Demonstrates basic control and monitoring operations
"""

import time
from dcdc_controller import (
    DCDCController,
    ConverterMode,
    ControlType,
    RequestedInfo
)


def example_voltage_regulation():
    """Example: Voltage regulation mode (Bus1 to Bus2)"""
    print("\n" + "="*70)
    print("EXAMPLE 1: Voltage Regulation (800V → 24V)")
    print("="*70)

    # Initialize controller
    controller = DCDCController(
        dbc_file='DCDC_COMETI_Primary_Customer_001_3units.dbc',
        can_interface='vcan0',  # Change to 'can0' for real hardware
        dcdc_id=0
    )

    try:
        # Start converter in voltage regulation mode
        print("\n1. Starting converter in voltage regulation mode (vBus2 = 24V)...")
        controller.start_converter(
            setpoint=24.0,                          # 24V output
            control_type=ControlType.V_BUS2,        # Regulate Bus2 voltage
            converter_mode=ConverterMode.BUS1_TO_BUS2,  # 800V → 24V
            current_limit=200.0                     # Max 200A
        )

        # Wait for converter to start
        time.sleep(1.0)

        # Request and display measurements
        print("\n2. Reading measurements...")
        for _ in range(5):
            controller.receive_messages(timeout=0.5)
            time.sleep(0.5)

        controller.print_measurements()
        controller.print_status()

        # Update setpoint during operation
        print("\n3. Changing setpoint to 12V...")
        controller.set_setpoint(120, 150.0)  # 12V in 0.1V units, 150A limit

        time.sleep(1.0)
        controller.receive_messages(timeout=0.5)
        controller.print_measurements()

        # Stop converter
        print("\n4. Stopping converter...")
        controller.stop_converter()

    finally:
        controller.close()


def example_current_regulation():
    """Example: Current regulation mode"""
    print("\n" + "="*70)
    print("EXAMPLE 2: Current Regulation")
    print("="*70)

    controller = DCDCController(
        dbc_file='DCDC_COMETI_Primary_Customer_001_3units.dbc',
        can_interface='vcan0',
        dcdc_id=0
    )

    try:
        # Start converter in current regulation mode
        print("\n1. Starting converter in current regulation mode (iBus2 = 50A)...")
        controller.start_converter(
            setpoint=50.0,                          # 50A output
            control_type=ControlType.I_BUS2,        # Regulate Bus2 current
            converter_mode=ConverterMode.BUS1_TO_BUS2,
            current_limit=100.0                     # Max 100A (safety limit)
        )

        # Monitor for 3 seconds
        print("\n2. Monitoring for 3 seconds...")
        for i in range(6):
            controller.receive_messages(timeout=0.5)
            print(f"  Reading {i+1}/6...")
            time.sleep(0.5)

        controller.print_measurements()
        controller.print_status()

        # Stop
        print("\n3. Stopping converter...")
        controller.stop_converter()

    finally:
        controller.close()


def example_power_regulation():
    """Example: Power regulation mode"""
    print("\n" + "="*70)
    print("EXAMPLE 3: Power Regulation")
    print("="*70)

    controller = DCDCController(
        dbc_file='DCDC_COMETI_Primary_Customer_001_3units.dbc',
        can_interface='vcan0',
        dcdc_id=0
    )

    try:
        # Start converter in power regulation mode
        print("\n1. Starting converter in power regulation mode (pBus2 = 1000W)...")
        controller.start_converter(
            setpoint=1000,                          # 1000W output
            control_type=ControlType.P_BUS2,        # Regulate Bus2 power
            converter_mode=ConverterMode.BUS1_TO_BUS2,
            current_limit=50.0                      # Max 50A
        )

        # Monitor
        time.sleep(1.0)
        controller.receive_messages(timeout=0.5)
        controller.print_measurements()
        controller.print_status()

        # Stop
        print("\n2. Stopping converter...")
        controller.stop_converter()

    finally:
        controller.close()


def example_bidirectional():
    """Example: Bidirectional operation"""
    print("\n" + "="*70)
    print("EXAMPLE 4: Bidirectional Operation")
    print("="*70)

    controller = DCDCController(
        dbc_file='DCDC_COMETI_Primary_Customer_001_3units.dbc',
        can_interface='vcan0',
        dcdc_id=0
    )

    try:
        # Start in bidirectional mode
        print("\n1. Starting converter in bidirectional mode...")
        controller.start_converter(
            setpoint=24.0,
            control_type=ControlType.V_BUS2,
            converter_mode=ConverterMode.BIDIRECTIONAL,
            current_limit=100.0
        )

        # Monitor
        time.sleep(1.0)
        controller.receive_messages(timeout=0.5)
        controller.print_status()

        # Stop
        print("\n2. Stopping converter...")
        controller.stop_converter()

    finally:
        controller.close()


def example_error_handling():
    """Example: Error monitoring and reset"""
    print("\n" + "="*70)
    print("EXAMPLE 5: Error Monitoring and Reset")
    print("="*70)

    controller = DCDCController(
        dbc_file='DCDC_COMETI_Primary_Customer_001_3units.dbc',
        can_interface='vcan0',
        dcdc_id=0
    )

    try:
        # Request error information
        print("\n1. Requesting error information...")
        controller.request_information(RequestedInfo.ERRORS)

        time.sleep(0.5)
        messages = controller.receive_messages(timeout=1.0)

        status = controller.get_status()
        if status['errors']:
            errors = status['errors']
            critical = errors.get('criticalErrors', 0)
            functional = errors.get('functionalErrors', 0)

            print(f"\nCritical Errors: 0x{critical:08X}")
            print(f"Functional Errors: 0x{functional:08X}")

            if critical != 0 or functional != 0:
                print("\n2. Errors detected! Resetting...")
                controller.reset_errors()
                time.sleep(0.5)
                print("   Errors reset command sent.")
            else:
                print("\n2. No errors detected.")
        else:
            print("\n2. No error information received.")

        # Request warnings
        print("\n3. Requesting warnings...")
        controller.request_information(RequestedInfo.WARNINGS)

        time.sleep(0.5)
        controller.receive_messages(timeout=1.0)

        status = controller.get_status()
        warnings = status.get('warnings', 0)
        print(f"Warnings: 0x{warnings:08X}")

    finally:
        controller.close()


def example_multi_unit():
    """Example: Control multiple DC-DC units"""
    print("\n" + "="*70)
    print("EXAMPLE 6: Multi-Unit Control (3 DC-DC Converters)")
    print("="*70)

    # Initialize 3 controllers
    controllers = []
    for dcdc_id in range(3):
        controller = DCDCController(
            dbc_file='DCDC_COMETI_Primary_Customer_001_3units.dbc',
            can_interface='vcan0',
            dcdc_id=dcdc_id
        )
        controllers.append(controller)

    try:
        # Start all converters with different setpoints
        print("\n1. Starting all 3 converters...")
        setpoints = [24.0, 12.0, 48.0]

        for i, (controller, setpoint) in enumerate(zip(controllers, setpoints)):
            print(f"\n   Unit {i}: Starting with setpoint {setpoint}V")
            controller.start_converter(
                setpoint=setpoint,
                control_type=ControlType.V_BUS2,
                converter_mode=ConverterMode.BUS1_TO_BUS2,
                current_limit=100.0
            )
            time.sleep(0.1)

        # Monitor all units
        print("\n2. Monitoring all units...")
        time.sleep(1.0)

        for i, controller in enumerate(controllers):
            controller.receive_messages(timeout=0.5)
            print(f"\n--- Unit {i} Status ---")
            controller.print_status()

        # Stop all converters
        print("\n3. Stopping all converters...")
        for i, controller in enumerate(controllers):
            print(f"   Stopping Unit {i}...")
            controller.stop_converter()
            time.sleep(0.1)

    finally:
        for controller in controllers:
            controller.close()


def main():
    """Run all examples"""
    print("\n" + "="*70)
    print("DC-DC CONVERTER CONTROL - USAGE EXAMPLES")
    print("="*70)
    print("\nNote: These examples use virtual CAN (vcan0).")
    print("For real hardware, change 'vcan0' to 'can0' in the code.")
    print("\nMake sure you have setup vcan0:")
    print("  sudo modprobe vcan")
    print("  sudo ip link add dev vcan0 type vcan")
    print("  sudo ip link set up vcan0")
    print("="*70)

    examples = [
        ("Voltage Regulation", example_voltage_regulation),
        ("Current Regulation", example_current_regulation),
        ("Power Regulation", example_power_regulation),
        ("Bidirectional Operation", example_bidirectional),
        ("Error Handling", example_error_handling),
        ("Multi-Unit Control", example_multi_unit),
    ]

    print("\nAvailable examples:")
    for i, (name, _) in enumerate(examples, 1):
        print(f"  {i}. {name}")

    print("\n  0. Run all examples")
    print("  q. Quit")

    while True:
        choice = input("\nSelect example (0-6, q): ").strip().lower()

        if choice == 'q':
            break
        elif choice == '0':
            for name, func in examples:
                print(f"\n\nRunning: {name}")
                try:
                    func()
                except Exception as e:
                    print(f"Error running example: {e}")
                time.sleep(2)
        elif choice.isdigit() and 1 <= int(choice) <= len(examples):
            idx = int(choice) - 1
            name, func = examples[idx]
            print(f"\n\nRunning: {name}")
            try:
                func()
            except Exception as e:
                print(f"Error running example: {e}")
        else:
            print("Invalid choice. Please try again.")

    print("\nGoodbye!")


if __name__ == '__main__':
    main()

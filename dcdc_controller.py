#!/usr/bin/env python3
"""
DC-DC Converter CAN Controller
Control and monitor DC-DC converters via CAN bus using the DBC protocol
"""

import can
import cantools
import time
from enum import IntEnum
from typing import Optional, Dict, Any


class ConverterMode(IntEnum):
    """Converter mode enumeration"""
    NOT_SET = 0
    BUS1_TO_BUS2 = 1
    BUS2_TO_BUS1 = 2
    BIDIRECTIONAL = 3


class ControlType(IntEnum):
    """Control/Regulation type enumeration"""
    NOT_SET = 0
    V_BUS2 = 1
    V_BUS1 = 2
    I_BUS2 = 3
    I_BUS1 = 4
    P_BUS2 = 5
    P_BUS1 = 6
    V_BUS2_ILIM = 7
    V_BUS1_ILIM = 8


class SoftwareMode(IntEnum):
    """Software mode enumeration"""
    EMERGENCY = 0
    STANDBY = 1
    RUNNING = 2
    POWERDOWN = 3
    SETTINGS = 4
    MAINTENANCE = 5


class RequestedInfo(IntEnum):
    """Information request types"""
    ERRORS = 1
    WARNINGS = 2
    CURRENT_MEASURES = 3
    POWER_MEASURES = 4
    VOLTAGE_MEASURES = 5
    TEMPERATURE_MEASURES = 6
    REGULATION_INFORMATION = 8
    CONTROL_INFORMATION = 9


class DCDCController:
    """DC-DC Converter CAN Controller"""

    def __init__(self, dbc_file: str, can_interface: str = 'can0',
                 can_bitrate: int = 500000, dcdc_id: int = 0):
        """
        Initialize DC-DC Controller

        Args:
            dbc_file: Path to DBC file
            can_interface: CAN interface name (e.g., 'can0', 'vcan0')
            can_bitrate: CAN bus bitrate in bps
            dcdc_id: DC-DC unit ID (0, 1, or 2)
        """
        self.dcdc_id = dcdc_id
        self.dcdc_suffix = f'_{dcdc_id}' if dcdc_id > 0 else ''

        # Load DBC file
        print(f"Loading DBC file: {dbc_file}")
        self.db = cantools.database.load_file(dbc_file)

        # Setup CAN bus
        print(f"Connecting to CAN interface: {can_interface} @ {can_bitrate} bps")
        self.bus = can.interface.Bus(
            channel=can_interface,
            bustype='socketcan',
            bitrate=can_bitrate
        )

        # Cache for received measurements
        self.measurements = {}
        self.errors = {'critical': 0, 'functional': 0}
        self.warnings = 0
        self.regulation_info = {}
        self.control_info = {}

        print(f"✓ DC-DC Controller initialized for unit {dcdc_id}")

    def _get_message_name(self, base_name: str) -> str:
        """Get message name with unit suffix"""
        return f"{base_name}{self.dcdc_suffix}"

    def start_converter(self, setpoint: float, control_type: ControlType,
                       converter_mode: ConverterMode, current_limit: float = 200.0):
        """
        Start the DC-DC converter

        Args:
            setpoint: Setpoint value (voltage in 0.1V, current in 0.1A, or power in W)
            control_type: Control/regulation type
            converter_mode: Converter mode (Bus1ToBus2, Bus2ToBus1, Bidirectional)
            current_limit: Current limitation in A (default 200.0)
        """
        print(f"Starting converter with:")
        print(f"  - Control Type: {ControlType(control_type).name}")
        print(f"  - Converter Mode: {ConverterMode(converter_mode).name}")
        print(f"  - Setpoint: {setpoint}")
        print(f"  - Current Limit: {current_limit} A")

        # First, set the mode
        self.set_mode(converter_mode, control_type)
        time.sleep(0.05)

        # Then send control request with start command
        msg_name = self._get_message_name('DCDC_ControlRequest')
        message = self.db.get_message_by_name(msg_name)

        # Convert setpoint based on control type
        if control_type in [ControlType.V_BUS1, ControlType.V_BUS2,
                           ControlType.V_BUS1_ILIM, ControlType.V_BUS2_ILIM]:
            setpoint_raw = int(setpoint * 10)  # Voltage in 0.1V
        elif control_type in [ControlType.I_BUS1, ControlType.I_BUS2]:
            setpoint_raw = int(setpoint * 10)  # Current in 0.1A
        else:  # Power
            setpoint_raw = int(setpoint)  # Power in W

        data = message.encode({
            'startCommand': 1,  # Start
            'setpointReq': setpoint_raw,
            'currentLimitReq': current_limit
        })

        msg = can.Message(
            arbitration_id=message.frame_id,
            data=data,
            is_extended_id=True
        )

        self.bus.send(msg)
        print("✓ Start command sent")

    def stop_converter(self):
        """Stop the DC-DC converter"""
        print("Stopping converter...")

        msg_name = self._get_message_name('DCDC_ControlRequest')
        message = self.db.get_message_by_name(msg_name)

        data = message.encode({
            'startCommand': 0,  # Stop
            'setpointReq': 0,
            'currentLimitReq': 0
        })

        msg = can.Message(
            arbitration_id=message.frame_id,
            data=data,
            is_extended_id=True
        )

        self.bus.send(msg)
        print("✓ Stop command sent")

    def set_mode(self, converter_mode: ConverterMode, control_type: ControlType):
        """
        Set converter mode and control type

        Args:
            converter_mode: Converter mode
            control_type: Control/regulation type
        """
        msg_name = self._get_message_name('DCDC_ModeRequest')
        message = self.db.get_message_by_name(msg_name)

        data = message.encode({
            'converterModeReq': converter_mode,
            'controlTypeReq': control_type
        })

        msg = can.Message(
            arbitration_id=message.frame_id,
            data=data,
            is_extended_id=True
        )

        self.bus.send(msg)
        print(f"✓ Mode set: {ConverterMode(converter_mode).name}, "
              f"Control: {ControlType(control_type).name}")

    def set_setpoint(self, setpoint: float, current_limit: float):
        """
        Update setpoint and current limit while running

        Args:
            setpoint: New setpoint value
            current_limit: Current limitation in A
        """
        msg_name = self._get_message_name('DCDC_ControlRequest')
        message = self.db.get_message_by_name(msg_name)

        data = message.encode({
            'startCommand': 1,  # Keep running
            'setpointReq': int(setpoint),
            'currentLimitReq': current_limit
        })

        msg = can.Message(
            arbitration_id=message.frame_id,
            data=data,
            is_extended_id=True
        )

        self.bus.send(msg)
        print(f"✓ Setpoint updated: {setpoint}, Current limit: {current_limit} A")

    def reset_errors(self):
        """Reset all errors"""
        print("Resetting errors...")

        msg_name = self._get_message_name('DCDC_ErrorResetRequest')
        message = self.db.get_message_by_name(msg_name)

        data = message.encode({})

        msg = can.Message(
            arbitration_id=message.frame_id,
            data=data,
            is_extended_id=True
        )

        self.bus.send(msg)
        print("✓ Error reset command sent")

    def request_information(self, info_type: RequestedInfo):
        """
        Request specific information from the converter

        Args:
            info_type: Type of information to request
        """
        msg_name = self._get_message_name('DCDC_InformationRequest')
        message = self.db.get_message_by_name(msg_name)

        data = message.encode({
            'requestdInfo': info_type
        })

        msg = can.Message(
            arbitration_id=message.frame_id,
            data=data,
            is_extended_id=True
        )

        self.bus.send(msg)

    def enter_settings_mode(self):
        """Enter settings mode"""
        print("Entering settings mode...")

        msg_name = self._get_message_name('DCDC_SettingsModeRequest')
        message = self.db.get_message_by_name(msg_name)

        data = message.encode({
            'request': 1  # Enter settings mode
        })

        msg = can.Message(
            arbitration_id=message.frame_id,
            data=data,
            is_extended_id=True
        )

        self.bus.send(msg)
        print("✓ Settings mode request sent")

    def exit_settings_mode(self):
        """Exit settings mode"""
        print("Exiting settings mode...")

        msg_name = self._get_message_name('DCDC_SettingsModeRequest')
        message = self.db.get_message_by_name(msg_name)

        data = message.encode({
            'request': 0  # Exit settings mode
        })

        msg = can.Message(
            arbitration_id=message.frame_id,
            data=data,
            is_extended_id=True
        )

        self.bus.send(msg)
        print("✓ Exit settings mode request sent")

    def receive_messages(self, timeout: float = 1.0) -> list:
        """
        Receive and decode CAN messages

        Args:
            timeout: Timeout in seconds

        Returns:
            List of decoded messages
        """
        decoded_messages = []
        start_time = time.time()

        while time.time() - start_time < timeout:
            msg = self.bus.recv(timeout=0.1)
            if msg is None:
                continue

            try:
                # Try to decode the message
                db_msg = self.db.get_message_by_frame_id(msg.arbitration_id)
                decoded = db_msg.decode(msg.data)

                # Store in cache based on message type
                msg_name = db_msg.name

                if 'CurrentMeasures' in msg_name:
                    self.measurements['current'] = decoded
                elif 'VoltageMeasures' in msg_name:
                    self.measurements['voltage'] = decoded
                elif 'PowerMeasures' in msg_name:
                    self.measurements['power'] = decoded
                elif 'TemperatureMeasures' in msg_name:
                    self.measurements['temperature'] = decoded
                elif 'Errors' in msg_name:
                    self.errors = decoded
                elif 'Warnings' in msg_name:
                    self.warnings = decoded.get('warnings', 0)
                elif 'RegulationInformation' in msg_name:
                    self.regulation_info = decoded
                elif 'ControlInformation' in msg_name:
                    self.control_info = decoded

                decoded_messages.append({
                    'name': msg_name,
                    'data': decoded
                })

            except (KeyError, cantools.database.errors.DecodeError):
                # Message not in DBC or decode error
                pass

        return decoded_messages

    def get_measurements(self) -> Dict[str, Any]:
        """Get all cached measurements"""
        return {
            'voltage': self.measurements.get('voltage', {}),
            'current': self.measurements.get('current', {}),
            'power': self.measurements.get('power', {}),
            'temperature': self.measurements.get('temperature', {})
        }

    def get_status(self) -> Dict[str, Any]:
        """Get converter status"""
        return {
            'control_info': self.control_info,
            'regulation_info': self.regulation_info,
            'errors': self.errors,
            'warnings': self.warnings
        }

    def print_measurements(self):
        """Print current measurements in a formatted way"""
        print("\n" + "="*60)
        print(f"DC-DC Unit {self.dcdc_id} - Measurements")
        print("="*60)

        # Voltage
        if 'voltage' in self.measurements:
            v = self.measurements['voltage']
            print(f"Voltages:")
            print(f"  vBus1: {v.get('vBus1', 0):.1f} V")
            print(f"  vBus2: {v.get('vBus2', 0):.1f} V")

        # Current
        if 'current' in self.measurements:
            i = self.measurements['current']
            print(f"Currents:")
            print(f"  iBus1: {i.get('iBus1', 0):.1f} A")
            print(f"  iBus2: {i.get('iBus2', 0):.1f} A")

        # Power
        if 'power' in self.measurements:
            p = self.measurements['power']
            print(f"Power:")
            print(f"  pBus1: {p.get('pBus1', 0)} W")
            print(f"  pBus2: {p.get('pBus2', 0)} W")

        # Temperatures
        if 'temperature' in self.measurements:
            t = self.measurements['temperature']
            print(f"Temperatures:")
            print(f"  Max Transformer: {t.get('TempMaxTransfo', 0)} °C")
            print(f"  Max MOSFET PSFB: {t.get('TempMaxMosfetPSFB', 0)} °C")
            print(f"  Max MOSFET Boost: {t.get('tempMaxMosfetBoost', 0)} °C")
            print(f"  Max Cooling: {t.get('TempMaxCooling', 0)} °C")
            print(f"  Ambient: {t.get('TempAmbiant', 0)} °C")

        print("="*60 + "\n")

    def print_status(self):
        """Print converter status"""
        print("\n" + "="*60)
        print(f"DC-DC Unit {self.dcdc_id} - Status")
        print("="*60)

        if self.regulation_info:
            mode = self.regulation_info.get('softwareMode', 0)
            print(f"Software Mode: {SoftwareMode(mode).name}")
            print(f"Setpoint: {self.regulation_info.get('setpoint', 0)}")

        if self.control_info:
            ctrl = self.control_info.get('controlType', 0)
            conv_mode = self.control_info.get('converterMode', 0)
            print(f"Control Type: {ControlType(ctrl).name}")
            print(f"Converter Mode: {ConverterMode(conv_mode).name}")
            print(f"Current Limit: {self.control_info.get('currentLimit', 0)} A")

        if self.errors:
            print(f"Critical Errors: 0x{self.errors.get('criticalErrors', 0):08X}")
            print(f"Functional Errors: 0x{self.errors.get('functionalErrors', 0):08X}")

        if self.warnings:
            print(f"Warnings: 0x{self.warnings:08X}")

        print("="*60 + "\n")

    def close(self):
        """Close CAN bus connection"""
        self.bus.shutdown()
        print("✓ CAN bus connection closed")


# Example usage
if __name__ == '__main__':
    # Initialize controller for DC-DC unit 0
    controller = DCDCController(
        dbc_file='DCDC_COMETI_Primary_Customer_001_3units.dbc',
        can_interface='vcan0',  # Use virtual CAN for testing
        dcdc_id=0
    )

    try:
        print("\n=== DC-DC Converter Control Example ===\n")

        # Example 1: Start converter in voltage regulation mode
        print("Example 1: Start converter")
        controller.start_converter(
            setpoint=24.0,  # 24V
            control_type=ControlType.V_BUS2,
            converter_mode=ConverterMode.BUS1_TO_BUS2,
            current_limit=200.0
        )

        # Wait and receive messages
        time.sleep(0.5)
        messages = controller.receive_messages(timeout=1.0)

        # Print status
        controller.print_status()
        controller.print_measurements()

        # Example 2: Update setpoint
        print("\nExample 2: Update setpoint to 12V")
        controller.set_setpoint(120, 150.0)  # 12V in 0.1V units

        time.sleep(0.5)
        messages = controller.receive_messages(timeout=1.0)
        controller.print_measurements()

        # Example 3: Stop converter
        print("\nExample 3: Stop converter")
        controller.stop_converter()

    finally:
        controller.close()

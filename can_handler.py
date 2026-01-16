#!/usr/bin/env python3
"""
CAN Bus Handler Module
Handles CAN bus communication and DBC file parsing
"""

import can
import cantools
from dataclasses import dataclass
from typing import Optional, Dict, Any
from pathlib import Path


@dataclass
class CANMessage:
    """Represents a decoded CAN message"""
    can_id: int
    name: str
    data: Dict[str, Any]
    data_hex: str
    timestamp: float


class CANBusHandler:
    """Handles CAN bus communication"""

    def __init__(self, config):
        self.config = config
        self.bus: Optional[can.Bus] = None
        self.db: Optional[cantools.database.Database] = None
        self.interface: Optional[str] = None

        # Try to load default DBC file
        dbc_file = config.get('dbc_file', 'DCDC_COMETI_Primary_Customer_001_3units.dbc')
        if Path(dbc_file).exists():
            try:
                self.load_dbc(dbc_file)
            except Exception as e:
                print(f"Warning: Could not load DBC file: {e}")

    def connect(self, interface: str, bitrate: int = 500000) -> None:
        """
        Connect to CAN bus interface

        Args:
            interface: CAN interface name (e.g., 'can0', 'vcan0')
            bitrate: CAN bus bitrate in bits/second
        """
        try:
            # Try socketcan first (Linux)
            self.bus = can.Bus(interface=interface, bustype='socketcan')
            self.interface = interface
            print(f"✓ Connected to {interface} (socketcan)")

        except Exception as e:
            # Fallback to virtual CAN for testing
            try:
                self.bus = can.Bus(interface=interface, bustype='virtual')
                self.interface = interface
                print(f"✓ Connected to {interface} (virtual)")
            except Exception as e2:
                raise ConnectionError(f"Failed to connect to {interface}: {e}\nVirtual fallback: {e2}")

    def disconnect(self) -> None:
        """Disconnect from CAN bus"""
        if self.bus:
            self.bus.shutdown()
            self.bus = None
            print(f"✓ Disconnected from {self.interface}")

    def load_dbc(self, filename: str) -> None:
        """
        Load DBC database file

        Args:
            filename: Path to DBC file
        """
        if not Path(filename).exists():
            raise FileNotFoundError(f"DBC file not found: {filename}")

        try:
            self.db = cantools.database.load_file(filename)
            print(f"✓ Loaded DBC: {filename}")
            print(f"  Messages: {len(self.db.messages)}")
            print(f"  Nodes: {len(self.db.nodes)}")
        except Exception as e:
            raise ValueError(f"Failed to parse DBC file: {e}")

    def send_message(self, can_id: int, data: bytes) -> None:
        """
        Send CAN message

        Args:
            can_id: CAN message ID
            data: Message data bytes
        """
        if not self.bus:
            raise ConnectionError("Not connected to CAN bus")

        message = can.Message(
            arbitration_id=can_id,
            data=data,
            is_extended_id=(can_id > 0x7FF)
        )

        self.bus.send(message)
        print(f"→ Sent: ID={hex(can_id)} Data={data.hex()}")

    def receive_message(self, timeout: float = 1.0) -> Optional[CANMessage]:
        """
        Receive and decode CAN message

        Args:
            timeout: Receive timeout in seconds

        Returns:
            Decoded CANMessage or None if timeout
        """
        if not self.bus:
            raise ConnectionError("Not connected to CAN bus")

        message = self.bus.recv(timeout=timeout)
        if not message:
            return None

        # Try to decode using DBC
        decoded_data = {}
        message_name = f"0x{message.arbitration_id:X}"

        if self.db:
            try:
                # Find message in database
                db_message = self.db.get_message_by_frame_id(message.arbitration_id)
                message_name = db_message.name

                # Decode signals
                decoded_data = db_message.decode(message.data)

            except (KeyError, Exception) as e:
                # Message not in database or decode error
                pass

        return CANMessage(
            can_id=message.arbitration_id,
            name=message_name,
            data=decoded_data,
            data_hex=message.data.hex(),
            timestamp=message.timestamp
        )

    def get_message_info(self, can_id: int) -> Optional[Dict[str, Any]]:
        """
        Get message information from DBC

        Args:
            can_id: CAN message ID

        Returns:
            Dictionary with message information
        """
        if not self.db:
            return None

        try:
            message = self.db.get_message_by_frame_id(can_id)
            return {
                'name': message.name,
                'length': message.length,
                'senders': list(message.senders),
                'signals': [
                    {
                        'name': signal.name,
                        'unit': signal.unit,
                        'min': signal.minimum,
                        'max': signal.maximum,
                        'offset': signal.offset,
                        'scale': signal.scale
                    }
                    for signal in message.signals
                ]
            }
        except KeyError:
            return None

    def list_messages(self) -> list:
        """
        List all messages in loaded DBC

        Returns:
            List of message names and IDs
        """
        if not self.db:
            return []

        return [
            {'id': msg.frame_id, 'name': msg.name, 'length': msg.length}
            for msg in self.db.messages
        ]

    def encode_message(self, message_name: str, data: Dict[str, Any]) -> bytes:
        """
        Encode message data using DBC

        Args:
            message_name: Name of message in DBC
            data: Dictionary of signal name: value pairs

        Returns:
            Encoded message bytes
        """
        if not self.db:
            raise ValueError("No DBC database loaded")

        try:
            message = self.db.get_message_by_name(message_name)
            return message.encode(data)
        except KeyError:
            raise ValueError(f"Message '{message_name}' not found in DBC")
        except Exception as e:
            raise ValueError(f"Failed to encode message: {e}")


# Virtual CAN bus simulator for testing
class VirtualCANSimulator:
    """Simulates CAN messages for testing without hardware"""

    def __init__(self):
        self.messages = []

    def generate_test_data(self) -> CANMessage:
        """Generate simulated CAN message"""
        import random
        from time import time

        # Simulate DC-DC converter messages
        can_id = random.choice([0x18FF50E5, 0x18FF50E6, 0x18FF50E7])

        data = {
            'input_voltage': random.uniform(200, 800),
            'input_current': random.uniform(0, 100),
            'output_voltage': random.uniform(200, 450),
            'output_current': random.uniform(0, 150),
            'temp_1': random.uniform(25, 85),
            'temp_2': random.uniform(25, 85),
            'status': 'Running',
            'efficiency': random.uniform(92, 98)
        }

        return CANMessage(
            can_id=can_id,
            name=f"DCDC_Status_{can_id & 0x03}",
            data=data,
            data_hex="".join([f"{random.randint(0, 255):02x}" for _ in range(8)]),
            timestamp=time()
        )

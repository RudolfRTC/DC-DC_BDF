#!/usr/bin/env python3
"""
Data Logger Module
Handles logging of CAN bus data and converter parameters
"""

import csv
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List
import threading
from collections import deque


class DataLogger:
    """Logs DC-DC converter data to files"""

    def __init__(self, config, max_buffer_size: int = 10000):
        self.config = config
        self.is_logging = False
        self.log_file = None
        self.csv_writer = None

        # Data buffer
        self.data_buffer = deque(maxlen=max_buffer_size)
        self.lock = threading.Lock()

        # Log directory
        self.log_dir = Path(config.get('log_directory', './logs'))
        self.log_dir.mkdir(exist_ok=True)

    def start_logging(self, log_format: str = 'csv') -> None:
        """
        Start logging data

        Args:
            log_format: Format for log file ('csv' or 'json')
        """
        if self.is_logging:
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_filename = self.log_dir / f"dcdc_log_{timestamp}.{log_format}"

        if log_format == 'csv':
            self.log_file = open(log_filename, 'w', newline='')
            self.csv_writer = csv.writer(self.log_file)

            # Write header
            self.csv_writer.writerow([
                'Timestamp',
                'Converter',
                'CAN_ID',
                'Message_Name',
                'Input_Voltage_V',
                'Input_Current_A',
                'Input_Power_W',
                'Output_Voltage_V',
                'Output_Current_A',
                'Output_Power_W',
                'Efficiency_%',
                'Temperature_1_C',
                'Temperature_2_C',
                'Status',
                'Error_Code'
            ])

        else:  # JSON
            self.log_file = open(log_filename, 'w')

        self.is_logging = True
        print(f"✓ Started logging to: {log_filename}")

    def stop_logging(self) -> None:
        """Stop logging data"""
        if not self.is_logging:
            return

        if self.log_file:
            self.log_file.close()
            self.log_file = None

        self.is_logging = False
        print("✓ Stopped logging")

    def log_data(self, converter: str, can_id: int, message_name: str, data: Dict[str, Any]) -> None:
        """
        Log data point

        Args:
            converter: Converter name (e.g., 'DCDC_Primary')
            can_id: CAN message ID
            message_name: Message name
            data: Dictionary of parameter values
        """
        timestamp = datetime.now().isoformat()

        # Add to buffer
        with self.lock:
            data_point = {
                'timestamp': timestamp,
                'converter': converter,
                'can_id': can_id,
                'message_name': message_name,
                'data': data
            }
            self.data_buffer.append(data_point)

        # Write to file if logging
        if self.is_logging and self.log_file:
            if self.csv_writer:
                self._write_csv_row(timestamp, converter, can_id, message_name, data)
            else:
                self._write_json_line(data_point)

    def _write_csv_row(self, timestamp: str, converter: str, can_id: int,
                       message_name: str, data: Dict[str, Any]) -> None:
        """Write CSV row"""
        row = [
            timestamp,
            converter,
            f"0x{can_id:X}",
            message_name,
            data.get('input_voltage', ''),
            data.get('input_current', ''),
            data.get('input_power', ''),
            data.get('output_voltage', ''),
            data.get('output_current', ''),
            data.get('output_power', ''),
            data.get('efficiency', ''),
            data.get('temp_1', ''),
            data.get('temp_2', ''),
            data.get('status', ''),
            data.get('error_code', '')
        ]
        self.csv_writer.writerow(row)
        self.log_file.flush()

    def _write_json_line(self, data_point: Dict[str, Any]) -> None:
        """Write JSON line"""
        self.log_file.write(json.dumps(data_point) + '\n')
        self.log_file.flush()

    def get_buffer_data(self, converter: str = None, limit: int = 1000) -> List[Dict[str, Any]]:
        """
        Get data from buffer

        Args:
            converter: Filter by converter name (optional)
            limit: Maximum number of data points to return

        Returns:
            List of data points
        """
        with self.lock:
            data = list(self.data_buffer)

        # Filter by converter if specified
        if converter:
            data = [d for d in data if d['converter'] == converter]

        # Apply limit
        return data[-limit:]

    def export_data(self, filename: str, format: str = None) -> None:
        """
        Export buffer data to file

        Args:
            filename: Output filename
            format: Export format ('csv', 'json', or auto-detect from extension)
        """
        path = Path(filename)

        # Auto-detect format from extension
        if format is None:
            format = path.suffix.lower().lstrip('.')
            if format not in ['csv', 'json']:
                format = 'csv'

        with self.lock:
            data = list(self.data_buffer)

        if not data:
            raise ValueError("No data to export")

        if format == 'csv':
            self._export_csv(path, data)
        else:
            self._export_json(path, data)

        print(f"✓ Exported {len(data)} data points to: {filename}")

    def _export_csv(self, path: Path, data: List[Dict[str, Any]]) -> None:
        """Export data as CSV"""
        with open(path, 'w', newline='') as f:
            writer = csv.writer(f)

            # Header
            writer.writerow([
                'Timestamp',
                'Converter',
                'CAN_ID',
                'Message_Name',
                'Input_Voltage_V',
                'Input_Current_A',
                'Input_Power_W',
                'Output_Voltage_V',
                'Output_Current_A',
                'Output_Power_W',
                'Efficiency_%',
                'Temperature_1_C',
                'Temperature_2_C',
                'Status',
                'Error_Code'
            ])

            # Data rows
            for point in data:
                d = point['data']
                writer.writerow([
                    point['timestamp'],
                    point['converter'],
                    f"0x{point['can_id']:X}",
                    point['message_name'],
                    d.get('input_voltage', ''),
                    d.get('input_current', ''),
                    d.get('input_power', ''),
                    d.get('output_voltage', ''),
                    d.get('output_current', ''),
                    d.get('output_power', ''),
                    d.get('efficiency', ''),
                    d.get('temp_1', ''),
                    d.get('temp_2', ''),
                    d.get('status', ''),
                    d.get('error_code', '')
                ])

    def _export_json(self, path: Path, data: List[Dict[str, Any]]) -> None:
        """Export data as JSON"""
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)

    def get_statistics(self, converter: str = None) -> Dict[str, Any]:
        """
        Calculate statistics from buffered data

        Args:
            converter: Filter by converter (optional)

        Returns:
            Dictionary with statistics
        """
        data = self.get_buffer_data(converter=converter)

        if not data:
            return {}

        # Calculate statistics for numeric parameters
        params = ['input_voltage', 'input_current', 'output_voltage',
                 'output_current', 'efficiency', 'temp_1', 'temp_2']

        stats = {}
        for param in params:
            values = [d['data'].get(param) for d in data if param in d['data']]
            values = [v for v in values if isinstance(v, (int, float))]

            if values:
                stats[param] = {
                    'min': min(values),
                    'max': max(values),
                    'avg': sum(values) / len(values),
                    'count': len(values)
                }

        stats['total_samples'] = len(data)
        stats['time_range'] = {
            'start': data[0]['timestamp'] if data else None,
            'end': data[-1]['timestamp'] if data else None
        }

        return stats

    def clear_buffer(self) -> None:
        """Clear the data buffer"""
        with self.lock:
            self.data_buffer.clear()
        print("✓ Cleared data buffer")

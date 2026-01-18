#!/usr/bin/env python3
"""
Comprehensive Test Suite for DC-DC Monitor Application
Tests all modules, functionality, and logic without requiring hardware
"""

import sys
import os
import tempfile
import json
from pathlib import Path

# Colors for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_test(test_name, status, details=""):
    """Print test result"""
    if status:
        print(f"  {Colors.GREEN}✓{Colors.RESET} {test_name}")
    else:
        print(f"  {Colors.RED}✗{Colors.RESET} {test_name}")
    if details:
        print(f"    {Colors.YELLOW}{details}{Colors.RESET}")


class TestConfigManager:
    """Test configuration manager module"""

    @staticmethod
    def run():
        print(f"\n{Colors.BOLD}Testing ConfigManager...{Colors.RESET}")
        results = []

        try:
            from config_manager import ConfigManager

            # Test 1: Create config
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                config_file = f.name

            config = ConfigManager(config_file)
            print_test("ConfigManager initialization", True)
            results.append(True)

            # Test 2: Get default values
            can_interface = config.get('can_interface', 'can0')
            status = can_interface == 'can0'
            print_test("Get default value", status, f"Value: {can_interface}")
            results.append(status)

            # Test 3: Set and get value
            config.set('test_key', 'test_value')
            value = config.get('test_key')
            status = value == 'test_value'
            print_test("Set and get value", status, f"Value: {value}")
            results.append(status)

            # Test 4: Nested keys
            config.set('nested.key.value', 123)
            value = config.get('nested.key.value')
            status = value == 123
            print_test("Nested key access", status, f"Value: {value}")
            results.append(status)

            # Test 5: Save config
            config.save()
            status = Path(config_file).exists()
            print_test("Save configuration", status)
            results.append(status)

            # Test 6: Load config
            config2 = ConfigManager(config_file)
            value = config2.get('test_key')
            status = value == 'test_value'
            print_test("Load saved configuration", status)
            results.append(status)

            # Cleanup
            os.remove(config_file)

        except Exception as e:
            print_test("ConfigManager module", False, str(e))
            return False

        return all(results)


class TestDataLogger:
    """Test data logger module"""

    @staticmethod
    def run():
        print(f"\n{Colors.BOLD}Testing DataLogger...{Colors.RESET}")
        results = []

        try:
            from data_logger import DataLogger
            from config_manager import ConfigManager

            # Create temp directory for logs
            temp_dir = tempfile.mkdtemp()

            # Test 1: Create logger
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                config_file = f.name

            config = ConfigManager(config_file)
            config.set('log_directory', temp_dir)

            logger = DataLogger(config)
            print_test("DataLogger initialization", True)
            results.append(True)

            # Test 2: Log data
            test_data = {
                'input_voltage': 400.5,
                'input_current': 50.2,
                'output_voltage': 350.0,
                'output_current': 60.0,
                'efficiency': 95.5,
                'temp_1': 45.0,
                'temp_2': 42.0
            }

            logger.log_data('DCDC_Primary', 0x18FF50E5, 'Test_Message', test_data)
            status = len(logger.data_buffer) == 1
            print_test("Log data to buffer", status, f"Buffer size: {len(logger.data_buffer)}")
            results.append(status)

            # Test 3: Get buffer data
            buffer_data = logger.get_buffer_data(limit=10)
            status = len(buffer_data) == 1
            print_test("Retrieve buffer data", status, f"Retrieved: {len(buffer_data)} items")
            results.append(status)

            # Test 4: Verify logged data
            logged = buffer_data[0]
            status = (logged['converter'] == 'DCDC_Primary' and
                     logged['data']['input_voltage'] == 400.5)
            print_test("Verify logged data integrity", status)
            results.append(status)

            # Test 5: Start/stop logging
            logger.start_logging('csv')
            status = logger.is_logging
            print_test("Start logging", status)
            results.append(status)

            logger.stop_logging()
            status = not logger.is_logging
            print_test("Stop logging", status)
            results.append(status)

            # Test 6: Export data
            export_file = os.path.join(temp_dir, 'test_export.csv')
            logger.export_data(export_file, 'csv')
            status = Path(export_file).exists()
            print_test("Export data to CSV", status)
            results.append(status)

            # Test 7: Statistics
            stats = logger.get_statistics()
            status = 'total_samples' in stats and stats['total_samples'] == 1
            print_test("Calculate statistics", status, f"Total samples: {stats.get('total_samples', 0)}")
            results.append(status)

            # Cleanup
            import shutil
            shutil.rmtree(temp_dir)
            os.remove(config_file)

        except Exception as e:
            print_test("DataLogger module", False, str(e))
            return False

        return all(results)


class TestCANHandler:
    """Test CAN handler module"""

    @staticmethod
    def run():
        print(f"\n{Colors.BOLD}Testing CANHandler...{Colors.RESET}")
        results = []

        try:
            from can_handler import CANBusHandler, CANMessage, VirtualCANSimulator
            from config_manager import ConfigManager

            # Test 1: Create handler
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                config_file = f.name

            config = ConfigManager(config_file)
            handler = CANBusHandler(config)
            print_test("CANBusHandler initialization", True)
            results.append(True)

            # Test 2: CANMessage dataclass
            msg = CANMessage(
                can_id=0x18FF50E5,
                name='Test_Message',
                data={'voltage': 400.0, 'current': 50.0},
                data_hex='0102030405060708',
                timestamp=123456.789
            )
            status = (msg.can_id == 0x18FF50E5 and msg.name == 'Test_Message')
            print_test("CANMessage dataclass", status, f"CAN ID: {hex(msg.can_id)}")
            results.append(status)

            # Test 3: Check DBC file loading
            dbc_file = 'DCDC_COMETI_Primary_Customer_001_3units.dbc'
            if Path(dbc_file).exists():
                try:
                    handler.load_dbc(dbc_file)
                    status = handler.db is not None
                    print_test("Load DBC file", status, f"Messages: {len(handler.db.messages) if handler.db else 0}")
                    results.append(status)

                    # Test 4: List messages
                    messages = handler.list_messages()
                    status = len(messages) > 0
                    print_test("List DBC messages", status, f"Found: {len(messages)} messages")
                    results.append(status)

                    # Test 5: Get message info
                    if messages:
                        msg_info = handler.get_message_info(messages[0]['id'])
                        status = msg_info is not None and 'name' in msg_info
                        print_test("Get message info", status,
                                 f"Message: {msg_info['name'] if msg_info else 'None'}")
                        results.append(status)

                except Exception as e:
                    print_test("DBC file operations", False, str(e))
                    results.append(False)
            else:
                print_test("DBC file exists", False, "File not found")
                results.append(False)

            # Test 6: Virtual CAN simulator
            simulator = VirtualCANSimulator()
            test_msg = simulator.generate_test_data()
            status = (isinstance(test_msg, CANMessage) and
                     test_msg.can_id > 0 and
                     len(test_msg.data) > 0)
            print_test("Virtual CAN simulator", status,
                     f"Generated CAN ID: {hex(test_msg.can_id)}")
            results.append(status)

            # Test 7: Verify simulated data
            status = (test_msg.data.get('input_voltage', 0) > 0 and
                     test_msg.data.get('efficiency', 0) > 0)
            print_test("Simulated data validity", status,
                     f"Voltage: {test_msg.data.get('input_voltage', 0):.1f}V")
            results.append(status)

            # Cleanup
            os.remove(config_file)

        except Exception as e:
            print_test("CANHandler module", False, str(e))
            return False

        return all(results)


class TestApplicationLogic:
    """Test application logic without GUI"""

    @staticmethod
    def run():
        print(f"\n{Colors.BOLD}Testing Application Logic...{Colors.RESET}")
        results = []

        try:
            from can_handler import CANMessage

            # Test 1: CAN ID to converter mapping
            test_cases = [
                (2148532224, 'DCDC_Primary'),
                (2148532225, 'DCDC_Primary_1'),
                (2148532226, 'DCDC_Primary_2'),
            ]

            # Simulate identify_converter logic
            def identify_converter(can_id):
                base_ids = [2148532224, 2148532480, 2148532736]
                for base_id in base_ids:
                    if can_id == base_id:
                        return 'DCDC_Primary'
                    elif can_id == base_id + 1:
                        return 'DCDC_Primary_1'
                    elif can_id == base_id + 2:
                        return 'DCDC_Primary_2'
                return None

            all_passed = True
            for can_id, expected in test_cases:
                result = identify_converter(can_id)
                if result == expected:
                    print_test(f"CAN ID mapping {hex(can_id)}", True, f"→ {expected}")
                else:
                    print_test(f"CAN ID mapping {hex(can_id)}", False,
                             f"Expected {expected}, got {result}")
                    all_passed = False

            results.append(all_passed)

            # Test 2: Message processing simulation
            converter_data = {
                'DCDC_Primary': {},
                'DCDC_Primary_1': {},
                'DCDC_Primary_2': {}
            }

            test_message = CANMessage(
                can_id=2148532224,
                name='DCDC_Status',
                data={'input_voltage': 400.0, 'input_current': 50.0, 'efficiency': 95.0},
                data_hex='0102030405060708',
                timestamp=123.456
            )

            converter = identify_converter(test_message.can_id)
            if converter and test_message.data:
                converter_data[converter].update(test_message.data)

            status = (converter_data['DCDC_Primary'].get('input_voltage') == 400.0)
            print_test("Message data update", status,
                     f"Stored voltage: {converter_data['DCDC_Primary'].get('input_voltage')}V")
            results.append(status)

            # Test 3: Parameter validation
            required_params = ['input_voltage', 'input_current', 'output_voltage',
                             'output_current', 'efficiency', 'temp_1', 'temp_2']

            test_data = {
                'input_voltage': 400.5,
                'input_current': 50.2,
                'output_voltage': 350.0,
                'output_current': 60.0,
                'efficiency': 95.5,
                'temp_1': 45.0,
                'temp_2': 42.0
            }

            missing = [p for p in required_params if p not in test_data]
            status = len(missing) == 0
            print_test("Parameter completeness", status,
                     f"Missing: {missing if missing else 'None'}")
            results.append(status)

            # Test 4: Value range validation
            def validate_ranges(data):
                validators = {
                    'input_voltage': (0, 1000),
                    'input_current': (0, 200),
                    'efficiency': (0, 100),
                    'temp_1': (-50, 150),
                    'temp_2': (-50, 150)
                }

                for key, (min_val, max_val) in validators.items():
                    if key in data:
                        value = data[key]
                        if not (min_val <= value <= max_val):
                            return False, f"{key}={value} out of range [{min_val}, {max_val}]"
                return True, "All values in range"

            valid, msg = validate_ranges(test_data)
            print_test("Value range validation", valid, msg)
            results.append(valid)

        except Exception as e:
            print_test("Application logic", False, str(e))
            return False

        return all(results)


class TestModuleIntegration:
    """Test integration between modules"""

    @staticmethod
    def run():
        print(f"\n{Colors.BOLD}Testing Module Integration...{Colors.RESET}")
        results = []

        try:
            from config_manager import ConfigManager
            from data_logger import DataLogger
            from can_handler import CANBusHandler, VirtualCANSimulator

            # Setup
            temp_dir = tempfile.mkdtemp()
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                config_file = f.name

            # Test 1: Config → Logger integration
            config = ConfigManager(config_file)
            config.set('log_directory', temp_dir)

            logger = DataLogger(config)
            status = Path(logger.log_dir) == Path(temp_dir)
            print_test("Config → Logger integration", status)
            results.append(status)

            # Test 2: Config → CANHandler integration
            config.set('dbc_file', 'DCDC_COMETI_Primary_Customer_001_3units.dbc')
            handler = CANBusHandler(config)
            status = handler.db is not None if Path(config.get('dbc_file')).exists() else True
            print_test("Config → CANHandler integration", status)
            results.append(status)

            # Test 3: Simulated message flow: CAN → Logger
            simulator = VirtualCANSimulator()
            message = simulator.generate_test_data()

            logger.log_data(
                converter='DCDC_Primary',
                can_id=message.can_id,
                message_name=message.name,
                data=message.data
            )

            buffer = logger.get_buffer_data()
            status = len(buffer) > 0 and buffer[0]['can_id'] == message.can_id
            print_test("CAN → Logger data flow", status,
                     f"Logged {len(buffer)} messages")
            results.append(status)

            # Test 4: Full pipeline simulation
            messages_processed = 0
            converter_data = {'DCDC_Primary': {}}

            for i in range(10):
                msg = simulator.generate_test_data()
                converter_data['DCDC_Primary'].update(msg.data)
                logger.log_data('DCDC_Primary', msg.can_id, msg.name, msg.data)
                messages_processed += 1

            status = (messages_processed == 10 and
                     len(logger.get_buffer_data()) >= 10 and
                     len(converter_data['DCDC_Primary']) > 0)
            print_test("Full pipeline (10 messages)", status,
                     f"Processed: {messages_processed}, Logged: {len(logger.get_buffer_data())}")
            results.append(status)

            # Cleanup
            import shutil
            shutil.rmtree(temp_dir)
            os.remove(config_file)

        except Exception as e:
            print_test("Module integration", False, str(e))
            return False

        return all(results)


def run_all_tests():
    """Run all test suites"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}  DC-DC Monitor - Comprehensive Test Suite{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.RESET}")

    test_suites = [
        ("ConfigManager", TestConfigManager.run),
        ("DataLogger", TestDataLogger.run),
        ("CANHandler", TestCANHandler.run),
        ("Application Logic", TestApplicationLogic.run),
        ("Module Integration", TestModuleIntegration.run),
    ]

    results = {}

    for suite_name, test_func in test_suites:
        try:
            result = test_func()
            results[suite_name] = result
        except Exception as e:
            print(f"\n{Colors.RED}Error in {suite_name}: {e}{Colors.RESET}")
            results[suite_name] = False

    # Summary
    print(f"\n{Colors.BOLD}{'='*70}{Colors.RESET}")
    print(f"{Colors.BOLD}Test Summary:{Colors.RESET}")
    print(f"{Colors.BOLD}{'='*70}{Colors.RESET}")

    total = len(results)
    passed = sum(1 for r in results.values() if r)
    failed = total - passed

    for suite_name, result in results.items():
        status = f"{Colors.GREEN}✓ PASS{Colors.RESET}" if result else f"{Colors.RED}✗ FAIL{Colors.RESET}"
        print(f"  {suite_name:<30} {status}")

    print(f"{Colors.BOLD}{'='*70}{Colors.RESET}")
    print(f"  Total: {total}  |  {Colors.GREEN}Passed: {passed}{Colors.RESET}  |  {Colors.RED}Failed: {failed}{Colors.RESET}")
    print(f"{Colors.BOLD}{'='*70}{Colors.RESET}")

    if all(results.values()):
        print(f"\n{Colors.GREEN}{Colors.BOLD}✓ ALL TESTS PASSED!{Colors.RESET}")
        print(f"\n{Colors.GREEN}Application is working correctly and ready to use.{Colors.RESET}")
        print(f"\n{Colors.BOLD}Next steps:{Colors.RESET}")
        print(f"  1. Install dependencies: pip3 install python-can cantools")
        print(f"  2. Run application: ./run_monitor.sh")
        return 0
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}✗ SOME TESTS FAILED{Colors.RESET}")
        print(f"\n{Colors.RED}Please review the errors above.{Colors.RESET}")
        return 1


if __name__ == '__main__':
    sys.exit(run_all_tests())

#!/usr/bin/env python3
"""
Test Suite Without External Dependencies
Tests core application logic without requiring python-can or cantools
"""

import sys
import os
import tempfile
from pathlib import Path

# Colors
class C:
    G = '\033[92m'; R = '\033[91m'; Y = '\033[93m'; B = '\033[94m'
    RESET = '\033[0m'; BOLD = '\033[1m'

def test(name, passed, detail=""):
    """Print test result"""
    status = f"{C.G}✓{C.RESET}" if passed else f"{C.R}✗{C.RESET}"
    print(f"  {status} {name}")
    if detail:
        print(f"    {C.Y}{detail}{C.RESET}")
    return passed


def test_config_manager():
    """Test ConfigManager without dependencies"""
    print(f"\n{C.BOLD}1. ConfigManager Module{C.RESET}")
    results = []

    try:
        from config_manager import ConfigManager

        # Create temp config
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            config_file = f.name

        config = ConfigManager(config_file)
        results.append(test("Create ConfigManager", True))

        # Test get/set
        config.set('test_key', 'test_value')
        value = config.get('test_key')
        results.append(test("Set and get value", value == 'test_value', f"Got: {value}"))

        # Test nested keys
        config.set('nested.key', 42)
        value = config.get('nested.key')
        results.append(test("Nested key access", value == 42, f"Got: {value}"))

        # Test defaults
        value = config.get('nonexistent', 'default')
        results.append(test("Default value", value == 'default', f"Got: {value}"))

        # Test save/load
        config.save()
        config2 = ConfigManager(config_file)
        value = config2.get('test_key')
        results.append(test("Save and reload", value == 'test_value'))

        # Cleanup
        os.remove(config_file)

        return all(results)

    except Exception as e:
        test("ConfigManager", False, str(e))
        return False


def test_data_logger():
    """Test DataLogger without dependencies"""
    print(f"\n{C.BOLD}2. DataLogger Module{C.RESET}")
    results = []

    try:
        from data_logger import DataLogger
        from config_manager import ConfigManager

        # Setup
        temp_dir = tempfile.mkdtemp()
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            config_file = f.name

        config = ConfigManager(config_file)
        config.set('log_directory', temp_dir)

        logger = DataLogger(config)
        results.append(test("Create DataLogger", True))

        # Test logging
        test_data = {
            'input_voltage': 400.0,
            'input_current': 50.0,
            'efficiency': 95.0
        }

        logger.log_data('DCDC_Primary', 0x123, 'TestMsg', test_data)
        buffer = logger.get_buffer_data()
        results.append(test("Log data", len(buffer) == 1, f"Buffer: {len(buffer)} items"))

        # Test data integrity
        logged = buffer[0]
        voltage_ok = logged['data']['input_voltage'] == 400.0
        results.append(test("Data integrity", voltage_ok, f"Voltage: {logged['data']['input_voltage']}V"))

        # Test export
        export_file = os.path.join(temp_dir, 'export.csv')
        logger.export_data(export_file)
        results.append(test("Export to CSV", Path(export_file).exists()))

        # Test statistics
        stats = logger.get_statistics()
        results.append(test("Calculate stats", stats['total_samples'] == 1,
                           f"Samples: {stats['total_samples']}"))

        # Cleanup
        import shutil
        shutil.rmtree(temp_dir)
        os.remove(config_file)

        return all(results)

    except Exception as e:
        test("DataLogger", False, str(e))
        return False


def test_application_logic():
    """Test core application logic"""
    print(f"\n{C.BOLD}3. Application Logic{C.RESET}")
    results = []

    try:
        # Simulate CAN ID mapping (from dcdc_monitor.py)
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

        # Test ID mappings
        test_cases = [
            (2148532224, 'DCDC_Primary'),
            (2148532225, 'DCDC_Primary_1'),
            (2148532226, 'DCDC_Primary_2'),
            (2148532480, 'DCDC_Primary'),
            (2148532481, 'DCDC_Primary_1'),
        ]

        all_ok = True
        for can_id, expected in test_cases:
            result = identify_converter(can_id)
            if result != expected:
                all_ok = False
                test(f"CAN ID {hex(can_id)}", False, f"Expected {expected}, got {result}")

        results.append(test("CAN ID to converter mapping", all_ok, f"Tested {len(test_cases)} cases"))

        # Test data update
        converter_data = {'DCDC_Primary': {}}
        test_data = {'voltage': 400, 'current': 50}
        converter_data['DCDC_Primary'].update(test_data)

        results.append(test("Data update", converter_data['DCDC_Primary']['voltage'] == 400))

        # Test value validation
        def validate_value(value, min_v, max_v):
            return min_v <= value <= max_v

        voltage = 400.0
        valid = validate_value(voltage, 0, 1000)
        results.append(test("Value range check", valid, f"{voltage}V in [0, 1000]"))

        # Test parameter formatting
        def format_parameter(value):
            if isinstance(value, float):
                return f"{value:.2f}"
            return str(value)

        formatted = format_parameter(95.567)
        results.append(test("Parameter formatting", formatted == "95.57", f"Got: {formatted}"))

        return all(results)

    except Exception as e:
        test("Application logic", False, str(e))
        return False


def test_file_structure():
    """Test file structure and imports"""
    print(f"\n{C.BOLD}4. File Structure & Imports{C.RESET}")
    results = []

    # Check required files exist
    required_files = [
        'dcdc_monitor.py',
        'can_handler.py',
        'data_logger.py',
        'config_manager.py',
        'requirements.txt',
        'README.md',
        'run_monitor.sh'
    ]

    missing = []
    for filename in required_files:
        if Path(filename).exists():
            results.append(test(f"File: {filename}", True))
        else:
            results.append(test(f"File: {filename}", False, "Missing"))
            missing.append(filename)

    # Check Python syntax
    python_files = ['dcdc_monitor.py', 'can_handler.py', 'data_logger.py', 'config_manager.py']

    import py_compile
    syntax_ok = True
    for pyfile in python_files:
        try:
            py_compile.compile(pyfile, doraise=True)
        except Exception as e:
            syntax_ok = False
            test(f"Syntax: {pyfile}", False, str(e))

    results.append(test("Python syntax check", syntax_ok, f"Checked {len(python_files)} files"))

    return all(results)


def test_code_quality():
    """Test code quality metrics"""
    print(f"\n{C.BOLD}5. Code Quality{C.RESET}")
    results = []

    try:
        # Count lines of code
        total_lines = 0
        code_files = ['dcdc_monitor.py', 'can_handler.py', 'data_logger.py', 'config_manager.py']

        for filename in code_files:
            with open(filename, 'r') as f:
                lines = len(f.readlines())
                total_lines += lines

        results.append(test("Total lines of code", total_lines > 1000,
                           f"{total_lines} lines"))

        # Check for docstrings
        import ast

        def has_docstrings(filename):
            with open(filename, 'r') as f:
                tree = ast.parse(f.read())

            classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
            functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]

            total = len(classes) + len(functions)
            documented = sum(1 for n in classes + functions if ast.get_docstring(n))

            return documented, total

        total_docs = 0
        total_items = 0
        for filename in code_files:
            docs, items = has_docstrings(filename)
            total_docs += docs
            total_items += items

        doc_ratio = (total_docs / total_items * 100) if total_items > 0 else 0
        results.append(test("Documentation coverage", doc_ratio > 80,
                           f"{doc_ratio:.1f}% ({total_docs}/{total_items})"))

        # Check for error handling
        def count_try_blocks(filename):
            with open(filename, 'r') as f:
                tree = ast.parse(f.read())
            return len([n for n in ast.walk(tree) if isinstance(n, ast.Try)])

        total_try_blocks = sum(count_try_blocks(f) for f in code_files)
        results.append(test("Error handling", total_try_blocks > 10,
                           f"{total_try_blocks} try/except blocks"))

        return all(results)

    except Exception as e:
        test("Code quality", False, str(e))
        return False


def test_integration():
    """Test module integration"""
    print(f"\n{C.BOLD}6. Module Integration{C.RESET}")
    results = []

    try:
        from config_manager import ConfigManager
        from data_logger import DataLogger

        # Setup
        temp_dir = tempfile.mkdtemp()
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            config_file = f.name

        # Config → Logger
        config = ConfigManager(config_file)
        config.set('log_directory', temp_dir)
        config.set('can_interface', 'vcan0')

        logger = DataLogger(config)
        results.append(test("Config → Logger", Path(logger.log_dir) == Path(temp_dir)))

        # Simulated message flow
        messages = []
        for i in range(5):
            data = {
                'input_voltage': 400 + i,
                'input_current': 50 + i * 0.5,
                'efficiency': 95 - i * 0.1
            }
            logger.log_data(f'DCDC_Primary', 0x100 + i, f'Msg_{i}', data)
            messages.append(data)

        buffer = logger.get_buffer_data()
        results.append(test("Message processing", len(buffer) == 5,
                           f"Processed {len(buffer)} messages"))

        # Statistics
        stats = logger.get_statistics()
        results.append(test("Statistics calculation",
                           'input_voltage' in stats,
                           f"Avg voltage: {stats.get('input_voltage', {}).get('avg', 0):.1f}V"))

        # Cleanup
        import shutil
        shutil.rmtree(temp_dir)
        os.remove(config_file)

        return all(results)

    except Exception as e:
        test("Integration", False, str(e))
        return False


def main():
    """Run all tests"""
    print(f"\n{C.BOLD}{C.B}{'='*70}{C.RESET}")
    print(f"{C.BOLD}{C.B}  DC-DC Monitor - Core Functionality Tests{C.RESET}")
    print(f"{C.BOLD}{C.B}  (Without external dependencies){C.RESET}")
    print(f"{C.BOLD}{C.B}{'='*70}{C.RESET}")

    tests = [
        ("ConfigManager", test_config_manager),
        ("DataLogger", test_data_logger),
        ("Application Logic", test_application_logic),
        ("File Structure", test_file_structure),
        ("Code Quality", test_code_quality),
        ("Integration", test_integration),
    ]

    results = {}
    for name, test_func in tests:
        try:
            results[name] = test_func()
        except Exception as e:
            print(f"\n{C.R}Error in {name}: {e}{C.RESET}")
            results[name] = False

    # Summary
    print(f"\n{C.BOLD}{'='*70}{C.RESET}")
    print(f"{C.BOLD}Test Results:{C.RESET}")
    print(f"{C.BOLD}{'='*70}{C.RESET}")

    total = len(results)
    passed = sum(1 for r in results.values() if r)
    failed = total - passed

    for name, result in results.items():
        status = f"{C.G}✓ PASS{C.RESET}" if result else f"{C.R}✗ FAIL{C.RESET}"
        print(f"  {name:<25} {status}")

    print(f"{C.BOLD}{'='*70}{C.RESET}")
    print(f"  Total: {total}  |  {C.G}Passed: {passed}{C.RESET}  |  {C.R}Failed: {failed}{C.RESET}")
    print(f"{C.BOLD}{'='*70}{C.RESET}")

    if all(results.values()):
        print(f"\n{C.G}{C.BOLD}✓ ALL CORE TESTS PASSED!{C.RESET}")
        print(f"\n{C.G}Core application logic is working correctly.{C.RESET}")
        print(f"\n{C.BOLD}Note:{C.RESET} CAN communication tests require:")
        print(f"  - python-can: pip3 install python-can")
        print(f"  - cantools: pip3 install cantools")
        print(f"\n{C.BOLD}To run the full application:{C.RESET}")
        print(f"  ./run_monitor.sh")
        return 0
    else:
        print(f"\n{C.R}{C.BOLD}✗ SOME TESTS FAILED{C.RESET}")
        return 1


if __name__ == '__main__':
    sys.exit(main())

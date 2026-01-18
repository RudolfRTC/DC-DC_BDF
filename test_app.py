#!/usr/bin/env python3
"""
Test script to verify DC-DC Monitor application
Tests basic functionality without requiring CAN hardware
"""

import sys
import os

def test_imports():
    """Test if all required modules can be imported"""
    print("Testing imports...")

    try:
        import tkinter as tk
        print("  ✓ tkinter")
    except ImportError as e:
        print(f"  ✗ tkinter: {e}")
        return False

    try:
        import can
        print("  ✓ python-can")
    except ImportError as e:
        print(f"  ✗ python-can: {e}")
        print("    Install with: pip3 install python-can")
        return False

    try:
        import cantools
        print("  ✓ cantools")
    except ImportError as e:
        print(f"  ✗ cantools: {e}")
        print("    Install with: pip3 install cantools")
        return False

    return True


def test_modules():
    """Test if application modules load correctly"""
    print("\nTesting application modules...")

    try:
        from config_manager import ConfigManager
        config = ConfigManager('test_config.json')
        print("  ✓ config_manager")
    except Exception as e:
        print(f"  ✗ config_manager: {e}")
        return False

    try:
        from can_handler import CANBusHandler, CANMessage
        handler = CANBusHandler(config)
        print("  ✓ can_handler")
    except Exception as e:
        print(f"  ✗ can_handler: {e}")
        return False

    try:
        from data_logger import DataLogger
        logger = DataLogger(config)
        print("  ✓ data_logger")
    except Exception as e:
        print(f"  ✗ data_logger: {e}")
        return False

    # Cleanup test config
    if os.path.exists('test_config.json'):
        os.remove('test_config.json')

    return True


def test_dbc_file():
    """Test if DBC file exists and is readable"""
    print("\nTesting DBC files...")

    files = [
        'DCDC_COMETI_Primary_Customer_001.dbc',
        'DCDC_COMETI_Primary_Customer_001_3units.dbc'
    ]

    found = False
    for filename in files:
        if os.path.exists(filename):
            print(f"  ✓ {filename}")
            found = True

            # Try to load it
            try:
                import cantools
                db = cantools.database.load_file(filename)
                print(f"    Messages: {len(db.messages)}")
                print(f"    Nodes: {len(db.nodes)}")
            except Exception as e:
                print(f"    ✗ Failed to parse: {e}")
        else:
            print(f"  ⚠ {filename} (not found)")

    return found


def test_gui_creation():
    """Test if GUI can be created (headless test)"""
    print("\nTesting GUI creation...")

    try:
        import tkinter as tk

        # Check if display is available
        try:
            root = tk.Tk()
            root.withdraw()  # Hide window
            print("  ✓ tkinter window creation")
            root.destroy()
            return True
        except tk.TclError:
            print("  ⚠ No display available (headless mode)")
            print("    GUI will not work in headless environment")
            return True  # Not a critical error

    except Exception as e:
        print(f"  ✗ GUI creation failed: {e}")
        return False


def run_all_tests():
    """Run all tests"""
    print("=" * 60)
    print("DC-DC Monitor - Application Test Suite")
    print("=" * 60)

    results = []

    # Run tests
    results.append(("Imports", test_imports()))
    results.append(("Modules", test_modules()))
    results.append(("DBC Files", test_dbc_file()))
    results.append(("GUI", test_gui_creation()))

    # Summary
    print("\n" + "=" * 60)
    print("Test Summary:")
    print("=" * 60)

    all_passed = True
    for test_name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"  {test_name:<20} {status}")
        if not passed:
            all_passed = False

    print("=" * 60)

    if all_passed:
        print("\n✓ All tests passed! Application is ready to run.")
        print("\nTo start the application:")
        print("  ./run_monitor.sh")
        print("  OR")
        print("  python3 dcdc_monitor.py")
        return 0
    else:
        print("\n✗ Some tests failed. Please fix the issues above.")
        return 1


if __name__ == '__main__':
    sys.exit(run_all_tests())

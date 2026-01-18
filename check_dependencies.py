#!/usr/bin/env python3
"""
Dependency checker and installer helper
"""

import sys
import subprocess

def check_dependency(module_name, package_name=None):
    """Check if a Python module is available"""
    if package_name is None:
        package_name = module_name

    try:
        __import__(module_name)
        return True, f"✓ {module_name}"
    except ImportError:
        return False, f"✗ {module_name} (install: pip3 install {package_name})"

def main():
    """Check all dependencies"""
    print("=" * 70)
    print("DC-DC Monitor - Dependency Check")
    print("=" * 70)

    dependencies = [
        ('tkinter', 'python3-tk'),  # Special case - system package
        ('can', 'python-can'),
        ('cantools', 'cantools'),
    ]

    missing = []
    installed = []

    for module, package in dependencies:
        available, msg = check_dependency(module, package)
        print(msg)

        if available:
            installed.append(module)
        else:
            missing.append((module, package))

    print("=" * 70)

    if not missing:
        print("\n✓ All dependencies are installed!")
        print("\nYou can run the application:")
        print("  ./run_monitor.sh")
        print("  OR")
        print("  python3 dcdc_monitor.py")
        return 0
    else:
        print(f"\n✗ Missing {len(missing)} dependencies:")
        print()

        # Installation instructions
        pip_packages = [pkg for mod, pkg in missing if pkg not in ['python3-tk']]
        apt_packages = [pkg for mod, pkg in missing if pkg == 'python3-tk']

        if apt_packages:
            print("Install system packages (Ubuntu/Debian):")
            print(f"  sudo apt-get install {' '.join(apt_packages)}")
            print()

        if pip_packages:
            print("Install Python packages:")
            print(f"  pip3 install {' '.join(pip_packages)}")
            print()
            print("Or install all at once:")
            print(f"  pip3 install -r requirements.txt")
            print()

        print("=" * 70)
        print("\nAlternative: Run in DEMO mode without hardware:")
        print("  python3 dcdc_monitor_demo.py")
        print()

        return 1

if __name__ == '__main__':
    sys.exit(main())

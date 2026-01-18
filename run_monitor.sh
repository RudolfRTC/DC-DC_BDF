#!/bin/bash
# DC-DC Converter Monitor Launcher Script

echo "╔════════════════════════════════════════════════╗"
echo "║   DC-DC Converter Monitor - TAME-POWER COMETi ║"
echo "╚════════════════════════════════════════════════╝"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed"
    echo "   Please install Python 3.7 or higher"
    exit 1
fi

echo "✓ Python 3 found: $(python3 --version)"
echo ""

# Check dependencies
echo "Checking dependencies..."
python3 check_dependencies.py
DEPS_STATUS=$?

if [ $DEPS_STATUS -ne 0 ]; then
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    read -p "Do you want to run in DEMO mode? (y/n): " -n 1 -r
    echo ""

    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo ""
        echo "Starting DEMO mode..."
        echo ""
        python3 dcdc_monitor_demo.py
    else
        echo ""
        echo "Please install dependencies first:"
        echo "  sudo apt-get install python3-tk"
        echo "  pip3 install python-can cantools"
        echo ""
        echo "Or run manually:"
        echo "  python3 dcdc_monitor_demo.py  (demo mode)"
        exit 1
    fi
else
    echo ""
    # Check if CAN interface is available (optional)
    if command -v ip &> /dev/null; then
        echo "Available CAN interfaces:"
        ip link show | grep can || echo "  (No CAN interfaces found - will use virtual mode)"
        echo ""
    fi

    # Launch full application
    echo "Starting DC-DC Monitor (full version)..."
    echo ""
    python3 dcdc_monitor.py
fi

echo ""
echo "Application closed."

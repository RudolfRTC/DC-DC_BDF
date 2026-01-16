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

# Check if dependencies are installed
echo ""
echo "Checking dependencies..."

if ! python3 -c "import can" 2>/dev/null; then
    echo "⚠ python-can not installed"
    echo "  Installing dependencies..."
    pip3 install -r requirements.txt
fi

if ! python3 -c "import cantools" 2>/dev/null; then
    echo "⚠ cantools not installed"
    echo "  Installing dependencies..."
    pip3 install -r requirements.txt
fi

echo "✓ All dependencies satisfied"
echo ""

# Check if CAN interface is available (optional)
if command -v ip &> /dev/null; then
    echo "Available CAN interfaces:"
    ip link show | grep can || echo "  (No CAN interfaces found - will use virtual mode)"
    echo ""
fi

# Launch application
echo "Starting DC-DC Monitor..."
echo ""
python3 dcdc_monitor.py

echo ""
echo "Application closed."

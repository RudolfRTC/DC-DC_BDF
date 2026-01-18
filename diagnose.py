#!/usr/bin/env python3
"""
Interactive diagnostic script - finds out what's wrong
"""

import sys
import os
import subprocess
import time

def print_header(text):
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70)

def test_cli_monitor():
    """Test CLI monitor"""
    print_header("TEST 1: CLI Monitor (brez odvisnosti)")
    print("\nStarting CLI monitor for 3 seconds...")
    print("(Če vidite podatke za Converter 1, 2, 3 - DELUJE!)\n")

    try:
        proc = subprocess.Popen(
            ['python3', 'dcdc_monitor_cli.py'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        time.sleep(3)
        proc.terminate()
        stdout, stderr = proc.communicate(timeout=2)

        if "Converter 1" in stdout:
            print("✅ CLI MONITOR DELUJE!")
            print("   Prikazal je podatke za pretvornike.")
            return True
        else:
            print("❌ CLI monitor NE prikazuje podatkov")
            print(f"Output: {stdout[:200]}")
            if stderr:
                print(f"Errors: {stderr[:200]}")
            return False

    except Exception as e:
        print(f"❌ Napaka pri zagonu: {e}")
        return False

def test_gui_demo():
    """Test GUI demo"""
    print_header("TEST 2: GUI Demo (potrebuje tkinter)")

    try:
        result = subprocess.run(
            ['python3', '-c', 'import tkinter'],
            capture_output=True,
            timeout=2
        )

        if result.returncode == 0:
            print("✅ tkinter je nameščen")
            print("\nGUI demo LAHKO deluje, ampak ne morem testirati brez zaslona.")
            print("\nČe želite GUI, zaženite:")
            print("  python3 dcdc_monitor_demo.py")
            return True
        else:
            print("❌ tkinter NI nameščen")
            print("\nNamestite z:")
            print("  sudo apt-get install python3-tk")
            return False

    except Exception as e:
        print(f"❌ Napaka: {e}")
        return False

def test_full_version():
    """Test full version dependencies"""
    print_header("TEST 3: Polna verzija (potrebuje vse odvisnosti)")

    deps = {
        'tkinter': 'python3-tk (sudo apt-get install python3-tk)',
        'can': 'python-can (pip3 install python-can)',
        'cantools': 'cantools (pip3 install cantools)'
    }

    missing = []
    installed = []

    for module, install_cmd in deps.items():
        try:
            __import__(module)
            installed.append(module)
            print(f"✅ {module}")
        except ImportError:
            missing.append((module, install_cmd))
            print(f"❌ {module} - {install_cmd}")

    if not missing:
        print("\n✅ VSE odvisnosti nameščene!")
        print("\nPolna verzija lahko deluje. Zaženite:")
        print("  ./run_monitor.sh")
        return True
    else:
        print(f"\n❌ Manjka {len(missing)} odvisnosti")
        print("\nZa polno verzijo namestite:")
        for mod, cmd in missing:
            print(f"  {cmd}")
        return False

def ask_user_question():
    """Ask user what they expect"""
    print_header("KAJ PRIČAKUJETE?")

    print("\n1. Command-line prikaz (terminal) - DELUJE TAKOJ")
    print("2. Grafični vmesnik (GUI okno) - potrebuje tkinter")
    print("3. Realne CAN podatke - potrebuje CAN hardware + odvisnosti")
    print("4. Drugo")

    choice = input("\nVnesite številko (1-4): ").strip()

    print()
    if choice == "1":
        print("✅ CLI verzija DELUJE!")
        print("\nZaženite:")
        print("  python3 dcdc_monitor_cli.py")
        print("\nPritisnite Ctrl+C za izhod.")

    elif choice == "2":
        print("GUI verzija potrebuje tkinter.")
        print("\nNamestite tkinter:")
        print("  sudo apt-get install python3-tk")
        print("\nPotem zaženite:")
        print("  python3 dcdc_monitor_demo.py")

    elif choice == "3":
        print("Za realne CAN podatke potrebujete:")
        print("  1. CAN vmesnik (can0 ali USB-CAN adapter)")
        print("  2. Odvisnosti: pip3 install python-can cantools")
        print("  3. sudo apt-get install python3-tk")
        print("\nPotem zaženite:")
        print("  ./run_monitor.sh")

    else:
        print("Prosim opišite kaj želite da aplikacija dela:")
        description = input("> ")
        print(f"\nHvala. Aplikacija trenutno:")
        print("  - CLI verzija: prikazuje simulirane podatke v terminalu")
        print("  - GUI demo: prikazuje simulirane podatke v grafičnem oknu")
        print("  - Polna verzija: prikazuje realne CAN podatke")

def main():
    """Run all tests"""
    print("╔══════════════════════════════════════════════════════════════════════╗")
    print("║             DC-DC Monitor - Diagnostični test                        ║")
    print("║           Ugotovimo kaj deluje in kaj ne                             ║")
    print("╚══════════════════════════════════════════════════════════════════════╝")

    results = []

    # Test 1: CLI
    results.append(("CLI Monitor", test_cli_monitor()))

    # Test 2: GUI Demo
    results.append(("GUI Demo", test_gui_demo()))

    # Test 3: Full version
    results.append(("Polna verzija", test_full_version()))

    # Summary
    print_header("POVZETEK")

    for name, result in results:
        status = "✅ DELUJE" if result else "❌ Potrebuje namestitev"
        print(f"  {name:<20} {status}")

    # Ask what user wants
    ask_user_question()

    print("\n" + "="*70)
    print("Konec diagnostike")
    print("="*70 + "\n")

if __name__ == '__main__':
    main()

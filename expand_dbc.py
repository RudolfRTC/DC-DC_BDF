#!/usr/bin/env python3
"""
Script to expand DBC file to support 3 DC-DC converters
- DCDC_Primary (ID offset +0) - original
- DCDC_Primary_1 (ID offset +1)
- DCDC_Primary_2 (ID offset +2)
"""

def read_dbc(filename):
    """Read the original DBC file"""
    with open(filename, 'r') as f:
        return f.readlines()

def write_dbc(filename, lines):
    """Write the new DBC file"""
    with open(filename, 'w') as f:
        f.writelines(lines)

def parse_messages(lines):
    """Parse all messages with their signals"""
    messages = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith('BO_ '):
            parts = line.split()
            can_id = int(parts[1])
            msg_name = parts[2].rstrip(':')
            dlc = parts[3]
            sender = parts[4].strip()

            # Collect signals
            signals = []
            i += 1
            while i < len(lines) and lines[i].startswith(' SG_'):
                signals.append(lines[i])
                i += 1

            messages.append({
                'can_id': can_id,
                'name': msg_name,
                'dlc': dlc,
                'sender': sender,
                'signals': signals,
                'line': line
            })
            continue
        i += 1
    return messages

def expand_dbc_for_multiple_units(input_file, output_file, num_units=3):
    """
    Expand DBC file to support multiple DC-DC units

    Args:
        input_file: Original DBC file path
        output_file: Output DBC file path
        num_units: Number of DC-DC units (default 3)
    """
    lines = read_dbc(input_file)
    messages = parse_messages(lines)
    new_lines = []

    # Process line by line
    i = 0
    while i < len(lines):
        line = lines[i]

        # Copy version and namespace sections as-is
        if line.startswith('VERSION') or line.startswith('NS_') or line.startswith('BS_:'):
            new_lines.append(line)
            i += 1
            continue

        # Handle BU_ (Bus Units) - add multiple DCDC units
        if line.startswith('BU_:'):
            new_lines.append('BU_: SUPERVISER DCDC_Primary DCDC_Primary_1 DCDC_Primary_2\n')
            i += 1
            continue

        # Handle BO_ (Messages) - duplicate for each DCDC unit
        if line.startswith('BO_ '):
            parts = line.split()
            can_id = int(parts[1])
            msg_name = parts[2].rstrip(':')
            dlc = parts[3]
            sender = parts[4].strip()

            # Find message in parsed messages
            msg_data = None
            for msg in messages:
                if msg['can_id'] == can_id:
                    msg_data = msg
                    break

            # Check if this message involves DCDC
            if 'DCDC_Primary' in sender or 'DCDC' in msg_name:
                # Generate for all units
                for unit_id in range(num_units):
                    new_can_id = can_id + unit_id
                    unit_suffix = f'_{unit_id}' if unit_id > 0 else ''
                    new_msg_name = msg_name + unit_suffix
                    new_sender = sender.replace('DCDC_Primary', f'DCDC_Primary{unit_suffix}' if unit_id > 0 else 'DCDC_Primary')

                    # Write message definition
                    new_lines.append(f'BO_ {new_can_id} {new_msg_name}: {dlc} {new_sender}\n')

                    # Write signals
                    if msg_data and msg_data['signals']:
                        for sig_line in msg_data['signals']:
                            # Update signal line to reference correct receiver
                            new_sig_line = sig_line
                            if 'DCDC_Primary' in sig_line and unit_id > 0:
                                new_sig_line = sig_line.replace('DCDC_Primary', f'DCDC_Primary_{unit_id}')
                            new_lines.append(new_sig_line)

                    new_lines.append('\n')

                # Skip original signals
                i += 1
                while i < len(lines) and lines[i].startswith(' SG_'):
                    i += 1
                continue
            else:
                # Keep original message (from SUPERVISER)
                new_lines.append(line)
                i += 1
                # Copy signals
                while i < len(lines) and lines[i].startswith(' SG_'):
                    new_lines.append(lines[i])
                    i += 1
                continue

        # Handle CM_ (Comments) - duplicate for each unit
        if line.startswith('CM_ BO_ '):
            parts = line.split(None, 3)
            can_id = int(parts[2])
            comment = parts[3] if len(parts) > 3 else '""'

            # Check if this is a DCDC message
            original_can_id = can_id
            if can_id >= 2148532224 and can_id <= 2305818624:  # Range of DCDC messages
                for unit_id in range(num_units):
                    new_can_id = original_can_id + unit_id
                    new_lines.append(f'CM_ BO_ {new_can_id} {comment}')
                i += 1
                continue

        # Handle CM_ SG_ (Signal Comments) - duplicate for each unit
        if line.startswith('CM_ SG_ '):
            parts = line.split(None, 4)
            can_id = int(parts[2])
            sig_name = parts[3]
            comment = parts[4] if len(parts) > 4 else '""'

            # Check if this is a DCDC message
            if can_id >= 2148532224 and can_id <= 2305818624:  # Range of DCDC messages
                for unit_id in range(num_units):
                    new_can_id = can_id + unit_id
                    new_lines.append(f'CM_ SG_ {new_can_id} {sig_name} {comment}')
                i += 1
                continue

        # Handle CM_ BU_ (Node Comments) - add for new units
        if line.startswith('CM_ BU_ DCDC_Primary '):
            comment = line.split(None, 3)[3]
            new_lines.append(line)  # Original
            new_lines.append(f'CM_ BU_ DCDC_Primary_1 "DCDC_Converter Primary_1 CAN interface";\n')
            new_lines.append(f'CM_ BU_ DCDC_Primary_2 "DCDC_Converter Primary_2 CAN interface";\n')
            i += 1
            continue

        # Handle BA_ (Attributes) - duplicate for each unit
        if line.startswith('BA_ "NmStationAddress" BU_ DCDC_Primary'):
            new_lines.append(line)  # Original with address 0
            new_lines.append('BA_ "NmStationAddress" BU_ DCDC_Primary_1 1;\n')
            new_lines.append('BA_ "NmStationAddress" BU_ DCDC_Primary_2 2;\n')
            i += 1
            continue

        if line.startswith('BA_ ') and 'BO_ ' in line:
            parts = line.split()
            # Find the CAN ID in the line
            for idx, part in enumerate(parts):
                if part == 'BO_' and idx + 1 < len(parts):
                    try:
                        can_id = int(parts[idx + 1])
                        # Check if this is a DCDC message
                        if can_id >= 2148532224 and can_id <= 2305818624:
                            attr_name = parts[1]
                            # Generate for all units
                            for unit_id in range(num_units):
                                new_can_id = can_id + unit_id
                                new_line = line.replace(f'BO_ {can_id}', f'BO_ {new_can_id}')
                                new_lines.append(new_line)
                            i += 1
                            break
                    except ValueError:
                        pass
            else:
                # Not a DCDC message attribute, keep as-is
                new_lines.append(line)
                i += 1
            continue

        # Handle VAL_ (Value Tables) - duplicate for each unit
        if line.startswith('VAL_ '):
            parts = line.split(None, 2)
            if len(parts) >= 2:
                try:
                    can_id = int(parts[1])
                    # Check if this is a DCDC message
                    if can_id >= 2148532224 and can_id <= 2305818624:
                        rest = parts[2]
                        for unit_id in range(num_units):
                            new_can_id = can_id + unit_id
                            new_lines.append(f'VAL_ {new_can_id} {rest}')
                        i += 1
                        continue
                except ValueError:
                    pass

        # Default: copy line as-is
        new_lines.append(line)
        i += 1

    # Write output
    write_dbc(output_file, new_lines)
    print(f"✓ Expanded DBC file created: {output_file}")
    print(f"  - Original units: 1 (DCDC_Primary)")
    print(f"  - New units: {num_units} (DCDC_Primary, DCDC_Primary_1, DCDC_Primary_2)")

if __name__ == '__main__':
    input_file = 'DCDC_COMETI_Primary_Customer_001.dbc'
    output_file = 'DCDC_COMETI_Primary_Customer_001_3units.dbc'

    expand_dbc_for_multiple_units(input_file, output_file, num_units=3)

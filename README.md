# DC-DC Converter CAN Control

Python kontrolni sistem za upravljanje DC-DC pretvornikov preko CAN bus komunikacije.

## 📁 Datoteke v projektu

- `DCDC_COMETI_Primary_Customer_001.dbc` - Originalna DBC datoteka (1 enota)
- `DCDC_COMETI_Primary_Customer_001_3units.dbc` - Razširjena DBC datoteka (3 enote)
- `expand_dbc.py` - Skript za generiranje multi-unit DBC datotek
- `dcdc_controller.py` - Python knjižnica za kontrolo DC-DC pretvornika
- `dcdc_gui.py` - Grafični vmesnik za kontrolo
- `requirements.txt` - Python dependencies

## 🚀 Namestitev

### 1. Namesti Python odvisnosti

```bash
pip install -r requirements.txt
```

### 2. Namesti python-tk (če ni že nameščen)

```bash
# Ubuntu/Debian
sudo apt-get install python3-tk

# Fedora/RHEL
sudo dnf install python3-tkinter
```

### 3. Setup CAN interface

#### Za testiranje z virtualnim CAN (vcan0):

```bash
# Naloži vcan modul
sudo modprobe vcan

# Ustvari virtualni CAN interface
sudo ip link add dev vcan0 type vcan
sudo ip link set up vcan0
```

#### Za pravi CAN interface (can0):

```bash
# Nastavi CAN interface na 500 kbit/s
sudo ip link set can0 type can bitrate 500000
sudo ip link set up can0
```

## 📖 Uporaba

### Grafični vmesnik (GUI)

```bash
python3 dcdc_gui.py
```

**Parametri v kodi, ki jih lahko spremeniš:**
- `can_interface` - CAN vmesnik ('can0', 'vcan0', itd.)
- `dcdc_id` - ID DC-DC enote (0, 1, ali 2)

### Python knjižnica (CLI)

```python
from dcdc_controller import DCDCController, ControlType, ConverterMode

# Inicializacija
controller = DCDCController(
    dbc_file='DCDC_COMETI_Primary_Customer_001_3units.dbc',
    can_interface='can0',
    dcdc_id=0  # 0, 1, ali 2
)

# Zagon pretvornika
controller.start_converter(
    setpoint=24.0,              # 24V
    control_type=ControlType.V_BUS2,
    converter_mode=ConverterMode.BUS1_TO_BUS2,
    current_limit=200.0         # 200A
)

# Branje meritev
controller.receive_messages(timeout=1.0)
controller.print_measurements()
controller.print_status()

# Ustavitev pretvornika
controller.stop_converter()

# Zapri povezavo
controller.close()
```

## 🎮 Funkcije GUI-ja

### Measurements (Meritve)
- **Voltage**: vBus1, vBus2 (V)
- **Current**: iBus1, iBus2 (A)
- **Power**: pBus1, pBus2 (W)

### Temperatures (Temperature)
- Max Transformer
- Max MOSFET PSFB
- Max MOSFET Boost
- Max Self Boost
- Max MOSFET Secondary
- Max Cooling
- Ambient

### Status
- **Software Mode**: STANDBY, RUNNING, itd.
- **Regulation Type**: vBus1, vBus2, iBus1, itd.
- **Regulation Mode**: Bus1ToBus2, Bus2ToBus1, Bidirectional
- **Setpoint**: Trenutna vrednost setpoint-a
- **Current Limit**: Trenutna omejitev toka

### Control (Kontrole)
- **Control Type**: Izberi tip regulacije (vBus1, vBus2, iBus1, iBus2, pBus1, pBus2, vBus1ILim, vBus2ILim)
- **Control Mode**: Izberi smer pretvorbe (Bus1ToBus2, Bus2ToBus1, Bidirectional)
- **Setpoint**: Nastavi željeno vrednost
- **Current Limit**: Nastavi omejitev toka (A)

### Gumbi
- **Start Converter**: Zaženi pretvornik z navedenimi parametri
- **Stop Converter**: Ustavi pretvornik
- **Update Setpoint**: Posodobi setpoint med delovanjem
- **Reset Errors**: Ponastavi napake

### Errors & Warnings
- **Critical Errors**: Kritične napake (rdeča)
- **Functional Errors**: Funkcionalne napake (rumena)
- **Warnings**: Opozorila (modra)

## 🔧 API Reference

### DCDCController

#### Metode:

##### `start_converter(setpoint, control_type, converter_mode, current_limit)`
Zažene pretvornik z navedenimi parametri.

**Parametri:**
- `setpoint` (float): Željena vrednost (napetost, tok, ali moč)
- `control_type` (ControlType): Tip regulacije
- `converter_mode` (ConverterMode): Način pretvorbe
- `current_limit` (float): Omejitev toka v A

##### `stop_converter()`
Ustavi pretvornik.

##### `set_mode(converter_mode, control_type)`
Nastavi način delovanja in tip regulacije.

##### `set_setpoint(setpoint, current_limit)`
Posodobi setpoint in omejitev toka med delovanjem.

##### `reset_errors()`
Ponastavi vse napake.

##### `receive_messages(timeout)`
Prejme in dekodira CAN sporočila.

##### `get_measurements()`
Vrne slovar vseh meritev.

##### `get_status()`
Vrne status pretvornika.

##### `print_measurements()`
Izpiše meritve v konzolo.

##### `print_status()`
Izpiše status v konzolo.

### Enumeracije

#### ConverterMode
- `NOT_SET = 0`
- `BUS1_TO_BUS2 = 1`
- `BUS2_TO_BUS1 = 2`
- `BIDIRECTIONAL = 3`

#### ControlType
- `NOT_SET = 0`
- `V_BUS2 = 1` - Napetostna regulacija Bus2
- `V_BUS1 = 2` - Napetostna regulacija Bus1
- `I_BUS2 = 3` - Tokovna regulacija Bus2
- `I_BUS1 = 4` - Tokovna regulacija Bus1
- `P_BUS2 = 5` - Močnostna regulacija Bus2
- `P_BUS1 = 6` - Močnostna regulacija Bus1
- `V_BUS2_ILIM = 7` - Napetostna regulacija Bus2 z omejitev toka
- `V_BUS1_ILIM = 8` - Napetostna regulacija Bus1 z omejitev toka

#### SoftwareMode
- `EMERGENCY = 0`
- `STANDBY = 1`
- `RUNNING = 2`
- `POWERDOWN = 3`
- `SETTINGS = 4`
- `MAINTENANCE = 5`

## 🔍 Testiranje

### Setup virtualnega CAN za testiranje

```bash
# Setup vcan0
sudo modprobe vcan
sudo ip link add dev vcan0 type vcan
sudo ip link set up vcan0

# Monitor CAN promet
candump vcan0

# Ročno pošiljanje CAN sporočil (za testiranje)
cansend vcan0 87800000#0101C800640000
```

### Preverjanje CAN prometa

```bash
# Prikaži ves CAN promet
candump can0

# Filtriraj samo DCDC sporočila
candump can0,80000000:1FF00000
```

## 📊 CAN Sporočila

### Od SUPERVISER → DCDC

| Sporočilo | CAN ID (hex) | Opis |
|-----------|-------------|------|
| DCDC_ControlRequest | 0x80000000 | Start/stop, setpoint, omejitev toka |
| DCDC_ModeRequest | 0x80800000 | Način delovanja in tip regulacije |
| DCDC_InformationRequest | 0x82800000 | Zahteva za informacije |
| DCDC_ParameterRequest | 0x88000000 | Branje/pisanje parametrov |
| DCDC_ErrorResetRequest | 0x85800000 | Reset napak |
| DCDC_SettingsModeRequest | 0x89800000 | Vstop/izstop iz nastavitvenega načina |

### Od DCDC → SUPERVISER

| Sporočilo | CAN ID (hex) | Frekvenca | Opis |
|-----------|-------------|-----------|------|
| DCDC_CurrentMeasures | 0x83400000 | 20ms | Meritve toka |
| DCDC_VoltageMeasures | 0x84800000 | 20ms | Meritve napetosti |
| DCDC_PowerMeasures | 0x83C00000 | 20ms | Meritve moči |
| DCDC_TemperatureMeasures | 0x84600000 | 20ms | Meritve temperatur |
| DCDC_Errors | 0x82000000 | 20ms | Napake |
| DCDC_Warnings | 0x85400000 | 20ms | Opozorila |
| DCDC_ControlInformation | 0x87800000 | 20ms | Informacije o kontroli |
| DCDC_RegulationInformation | 0x87000000 | 20ms | Informacije o regulaciji |

**Opomba**: Za DC-DC enote 1 in 2, CAN ID-ji so +1 in +2 od prikazanih vrednosti.

## 🛠️ Razširitev DBC datoteke

Za generiranje DBC datoteke z več enotami:

```bash
python3 expand_dbc.py
```

To bo ustvarilo `DCDC_COMETI_Primary_Customer_001_3units.dbc` z 3 DC-DC enotami.

## 📝 Licenca

To je dokumentacijski in kontrolni sistem za DC-DC pretvornik TAME-POWER COMETi.

## 👤 Avtor

Ustvarjeno s Claude Code za projekt DC-DC_BDF

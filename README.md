# DC-DC Converter Monitor

Profesionalna aplikacija za spremljanje in nadzor **TAME-POWER COMETi** DC-DC pretvornikov v realnem času preko CAN vodila.

![Python Version](https://img.shields.io/badge/python-3.7%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

## 🚀 Funkcionalnosti

### ✅ Glavne funkcije:
- **Grafični vmesnik (GUI)** - Intuitivna uporaba z večimi zavihki
- **Spremljanje v realnem času** - Prikaz podatkov za 3 DC-DC pretvornike
- **CAN vodilo komunikacija** - Podpora za socketcan (Linux)
- **Beleženje podatkov** - Samodejno shranjevanje v CSV/JSON format
- **Vizualizacija** - Grafi in preglednice
- **Izvoz podatkov** - Izvoz v različne formate
- **Upravljanje s konfiguracijo** - Prilagodljive nastavitve
- **DBC podpora** - Samodejno dekodiranje CAN sporočil

### 📊 Spremljani parametri:
- Vhodna napetost, tok in moč
- Izhodna napetost, tok in moč
- Izkoristek (%)
- Temperature (2 senzorja)
- Status sistema
- Kode napak
- Način delovanja

### 🔧 Podprti pretvorniki:
- DCDC_Primary (osnovna enota)
- DCDC_Primary_1 (enota 1)
- DCDC_Primary_2 (enota 2)

---

## 📋 Sistemske zahteve

### Minimalne zahteve:
- **OS**: Linux (Ubuntu 20.04+, Debian 11+, Raspberry Pi OS)
- **Python**: 3.7 ali višja verzija
- **RAM**: 512 MB
- **Disk**: 100 MB prostora

### Priporočljivo:
- **OS**: Linux s CAN podporo
- **Python**: 3.9+
- **RAM**: 2 GB+
- **CAN vmesnik**: USB-CAN adapter ali vgrajen CAN

---

## 🛠️ Namestitev

### 1. Kloniranje repozitorija

```bash
git clone <repository-url>
cd DC-DC_BDF
```

### 2. Namestitev Python odvisnosti

```bash
pip3 install -r requirements.txt
```

#### Odvisnosti:
- `python-can` - CAN vodilo komunikacija
- `cantools` - Dekodiranje DBC datotek
- `tkinter` - GUI (običajno že vključen v Python)

### 3. Nastavitev CAN vmesnika (Linux)

#### Za fizični CAN vmesnik:

```bash
# Nastavitev CAN0 na 500 kbps
sudo ip link set can0 type can bitrate 500000
sudo ip link set can0 up

# Preveri status
ip link show can0
```

#### Za virtualni CAN (testiranje brez strojne opreme):

```bash
# Naloži vcan modul
sudo modprobe vcan

# Ustvari virtualni CAN vmesnik
sudo ip link add dev vcan0 type vcan
sudo ip link set up vcan0

# Preveri
ip link show vcan0
```

---

## 🎯 Uporaba

### Hiter začetek

#### 1. Uporaba launcher skripta (priporočeno):

```bash
./run_monitor.sh
```

#### 2. Direktno poganjanje:

```bash
python3 dcdc_monitor.py
```

### Osnovni koraki:

1. **Zagon aplikacije** - Odpre se grafični vmesnik
2. **Izbira CAN vmesnika** - Izberi `can0`, `can1` ali `vcan0`
3. **Začetek spremljanja** - Klikni "▶ Start Monitoring"
4. **Spremljanje podatkov** - Poglej zavihke z različnimi pogledi
5. **Beleženje** - Meni Tools → Start Logging
6. **Izvoz** - Meni File → Export Data

### Zavihki v aplikaciji:

#### 📊 Real-time Monitoring
- Trenutne vrednosti vseh parametrov
- Zgodovinski log CAN sporočil
- Prikaz za izbrani pretvornik

#### 📈 Data Visualization
- Grafi napetosti, toka, moči
- Izkoristek preko časa
- Lahko dodaš matplotlib za napredne grafe

#### 🔍 All Converters
- Hkraten prikaz vseh 3 pretvornikov
- Primerjava parametrov
- Status pregled

#### ⚙️ Configuration
- Nastavitve CAN vmesnika
- Pot do DBC datoteke
- Direktorij za logiranje
- Shrani konfigurацijo

---

## 📁 Struktura projekta

```
DC-DC_BDF/
├── dcdc_monitor.py              # Glavna aplikacija z GUI
├── can_handler.py               # CAN vodilo komunikacija
├── data_logger.py               # Beleženje in izvoz podatkov
├── config_manager.py            # Upravljanje s konfiguracijo
├── expand_dbc.py                # Orodje za razširjanje DBC datotek
├── requirements.txt             # Python odvisnosti
├── run_monitor.sh               # Launcher skript
├── config.json                  # Konfiguracijska datoteka (avtomatsko ustvarjena)
├── logs/                        # Direktorij za log datoteke (avtomatsko ustvarjen)
├── README.md                    # Ta dokumentacija
├── DCDC_COMETI_Primary_Customer_001.dbc           # Originalna DBC datoteka
├── DCDC_COMETI_Primary_Customer_001_3units.dbc    # Razširjena DBC za 3 enote
└── PDF dokumentacija            # Priročniki in datasheets
```

---

## 🔌 CAN Vmesniki

### Podprti vmesniki:

1. **SocketCAN (Linux)**
   - Najboljša izbira za Linux sisteme
   - Direktna integracija v jedro
   - Podpora za večino USB-CAN adapterjev

2. **Virtual CAN**
   - Za testiranje brez strojne opreme
   - Simulacija CAN komunikacije

### Priporočeni USB-CAN adapterji:
- PEAK PCAN-USB
- Kvaser Leaf Light
- CANable / canable.io
- USB2CAN

---

## 📝 Primeri uporabe

### 1. Testiranje z virtualnim CAN vmesnikom

```bash
# Terminal 1: Zaženi monitor
./run_monitor.sh

# Terminal 2: Pošlji testna CAN sporočila
cansend vcan0 18FF50E5#0102030405060708
```

### 2. Spremljanje realnih pretvornikov

```bash
# Nastavi CAN vmesnik
sudo ip link set can0 type can bitrate 500000
sudo ip link set can0 up

# Zaženi monitor
./run_monitor.sh

# Izberi can0 in klikni Start Monitoring
```

### 3. Izvoz podatkov za analizo

```python
# V aplikaciji:
# 1. Tools → Start Logging
# 2. Počakaj na zbiranje podatkov (nekaj minut)
# 3. Tools → Stop Logging
# 4. File → Export Data → Izberi ime datoteke
# 5. Uporabi Excel/Python za analizo CSV datoteke
```

---

## ⚙️ Konfiguracija

### config.json struktura:

```json
{
  "can_interface": "can0",
  "can_bitrate": 500000,
  "dbc_file": "DCDC_COMETI_Primary_Customer_001_3units.dbc",
  "log_directory": "./logs",
  "auto_reconnect": true,
  "message_buffer_size": 1000,
  "refresh_rate_ms": 100,
  "converters": {
    "DCDC_Primary": {
      "enabled": true,
      "alias": "Converter 1",
      "color": "#FF6B6B"
    },
    "DCDC_Primary_1": {
      "enabled": true,
      "alias": "Converter 2",
      "color": "#4ECDC4"
    },
    "DCDC_Primary_2": {
      "enabled": true,
      "alias": "Converter 3",
      "color": "#95E1D3"
    }
  },
  "alarms": {
    "overvoltage_threshold": 850,
    "undervoltage_threshold": 150,
    "overcurrent_threshold": 150,
    "overtemperature_threshold": 85,
    "enable_sound": true
  }
}
```

### Prilagoditev nastavitev:

1. **V aplikaciji**: Configuration tab → Spremeni vrednosti → Save Configuration
2. **Ročno**: Uredi `config.json` datoteko

---

## 🐛 Odpravljanje težav

### Težava: "No module named 'can'"

**Rešitev:**
```bash
pip3 install python-can cantools
```

### Težava: "Cannot find CAN interface can0"

**Rešitev:**
```bash
# Preveri vmesnike
ip link show

# Uporabi vcan0 za testiranje
sudo modprobe vcan
sudo ip link add dev vcan0 type vcan
sudo ip link set up vcan0
```

### Težava: "Permission denied" pri dostopu do CAN

**Rešitev:**
```bash
# Dodaj uporabnika v skupino
sudo usermod -a -G dialout $USER
sudo usermod -a -G plugdev $USER

# Ponovno se prijavi
```

### Težava: GUI se ne odpre

**Rešitev:**
```bash
# Preveri tkinter
python3 -c "import tkinter"

# Namesti tkinter (če manjka)
sudo apt-get install python3-tk
```

### Težava: DBC datoteka se ne naloži

**Rešitev:**
- Preveri pot do datoteke v Configuration tab
- Uporabi absolutno pot
- Preveri, da datoteka obstaja: `ls -la *.dbc`

---

## 🔧 Orodja

### expand_dbc.py

Orodje za razširitev DBC datoteke za več pretvornikov.

```bash
# Uporaba
python3 expand_dbc.py

# Rezultat: DCDC_COMETI_Primary_Customer_001_3units.dbc
```

**Funkcionalnost:**
- Prebere osnovno DBC datoteko (1 pretvornik)
- Ustvari razširjeno datoteko (3 pretvorniki)
- Prilagodi CAN ID-je (+0, +1, +2)
- Posodobi vozlišča in komentarje

---

## 📚 Dodatna dokumentacija

V repozitoriju so na voljo:

1. **COMETi UserManual 01.pdf** - Podroben priročnik za uporabo
2. **TAME-POWER Datasheet** - Tehnični podatki pretvornikov
3. **DBC datoteke** - CAN baza sporočil

---

## 🚦 Status in verzije

### Trenutna verzija: 1.0

#### ✅ Implementirano:
- [x] Grafični vmesnik
- [x] CAN komunikacija
- [x] Spremljanje 3 pretvornikov
- [x] Beleženje podatkov
- [x] Izvoz CSV/JSON
- [x] Konfiguracija
- [x] DBC podpora

#### 🔄 V razvoju:
- [ ] Napredni grafi (matplotlib integracija)
- [ ] Alarmi in obvestila
- [ ] Zgodovinski podatki
- [ ] Ethernet/TCP komunikacija
- [ ] Mobilna aplikacija

---

## 💡 Nasveti za uporabo

1. **Prvi zagon**: Uporabi `vcan0` za testiranje brez strojne opreme
2. **Produkcija**: Uporabi `can0` z realnimi pretvorniki
3. **Beleženje**: Vedno vključi logging za kasnejšo analizo
4. **Izvoz**: Izvozi podatke redno za arhiviranje
5. **Backup**: Shrani `config.json` pred spremembami

---

## 🤝 Podpora

Za težave, vprašanja ali predloge:
- Odpri GitHub Issue
- Preveri dokumentacijo
- Poglej primere uporabe

---

## 📄 Licenca

MIT License - prosto za uporabo in prilagoditev

---

## 🎉 Hvala za uporabo!

Če aplikacija deluje pravilno, lahko začnete spremljati svoje DC-DC pretvornike takoj! 🚀

**Pomembno:** Vedno preveri električne povezave in parametre pred uporabo v produkcijskem okolju.

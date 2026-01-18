# DC-DC Monitor - ENOSTAVNA NAVODILA

## ❓ KAJ IMAM?

Imate **3 različne verzije** aplikacije:

### 1️⃣ **CLI Verzija** ✅ DELUJE TAKOJ
```bash
python3 dcdc_monitor_cli.py
```
**Kaj dobite:**
- Prikaz v terminalu (črno okno z besedilom)
- 3 pretvorniki prikazani hkrati
- Posodobitve vsaki 2 sekundi
- **DELUJE brez namestitve!**

**Izgled:**
```
┌─ Converter 1 ────────────────────────────
│  Status: Running
│  INPUT
│    Voltage:   418.2 V
│    Current:    46.8 A
│    Power:     19575 W
│  OUTPUT
│    Voltage:   364.5 V
│    Current:    60.0 A
│    Power:     21865 W
│  EFFICIENCY:   94.7 %
│  TEMPERATURE
│    Sensor 1:     56 °C
│    Sensor 2:     49 °C
└──────────────────────────────────────────────────────
```

---

### 2️⃣ **GUI Demo** ⚠️ Potrebuje tkinter
```bash
python3 dcdc_monitor_demo.py
```
**Kaj dobite:**
- Grafično okno z gumbi in zavihki
- Lepši prikaz podatkov
- Kliki z miško

**Namestitev:**
```bash
sudo apt-get install python3-tk
```

---

### 3️⃣ **Polna Verzija** ⚠️ Potrebuje CAN hardware
```bash
./run_monitor.sh
```
**Kaj dobite:**
- GUI okno
- Realni CAN podatki (ne simulirani!)
- Beleženje v datoteke
- Izvoz CSV

**Namestitev:**
```bash
sudo apt-get install python3-tk
pip3 install python-can cantools
```

---

## 🚀 KAJ ZDAJ DELUJE?

Poženite diagnostiko:
```bash
python3 diagnose.py
```

Pove vam:
- ✅ Kaj deluje
- ❌ Kaj manjka
- 📝 Kako popraviti

---

## 🎯 HITER TEST (30 SEKUND)

```bash
# 1. Zaženi CLI verzijo
python3 dcdc_monitor_cli.py

# 2. Počakaj 5 sekund - vidite 3 pretvornike

# 3. Pritisnite Ctrl+C za izhod
```

**ČE TO DELUJE** = Aplikacija je OK! ✅

**ČE TO NE DELUJE** = Pošljite mi screenshot napake! ❌

---

## 💡 POGOSTA VPRAŠANJA

### Q: "Aplikacija se ugasne sama"
A: To je normalno za CLI verzijo - pritisnite Ctrl+C za izhod.
   Če želite GUI okno, potrebujete namestiti tkinter.

### Q: "Nič ne vidim"
A: CLI verzija prikazuje v terminalu, ne odpre novega okna.
   Za GUI okno uporabite demo verzijo (potrebuje tkinter).

### Q: "Podatki so simulirani?"
A: DA! CLI in Demo verzija uporabljata simulirane podatke.
   Za realne CAN podatke potrebujete polno verzijo + CAN hardware.

### Q: "Kako dobim GUI okno?"
A:
```bash
sudo apt-get install python3-tk
python3 dcdc_monitor_demo.py
```

### Q: "Kako vidim REALNE podatke iz CAN?"
A:
```bash
# 1. Namesti vse
sudo apt-get install python3-tk
pip3 install python-can cantools

# 2. Priključi CAN vmesnik (USB adapter ali onboard)

# 3. Zaženi
./run_monitor.sh
```

---

## 📞 ŠE VEDNO NE DELUJE?

Poženite:
```bash
python3 diagnose.py
```

In mi pošljite celoten output!

---

## ✅ POVZETEK

| Verzija | Odvisnosti | Deluje? | Uporaba |
|---------|-----------|---------|---------|
| CLI | NOBENE | ✅ DA | `python3 dcdc_monitor_cli.py` |
| GUI Demo | tkinter | ⚠️ Manjka | `python3 dcdc_monitor_demo.py` |
| Polna | tkinter + CAN libs | ⚠️ Manjka | `./run_monitor.sh` |

**PRIPOROČILO**: Začnite s CLI verzijo!

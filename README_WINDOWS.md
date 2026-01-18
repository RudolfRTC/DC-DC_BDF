# DC-DC Monitor - WINDOWS NAVODILA

## 🪟 Za Windows uporabnike

Aplikacija je narejena za Linux, ampak **CLI in Demo verzija delujeta tudi na Windows!**

---

## ✅ KAJ DELUJE NA WINDOWS:

### 1️⃣ **CLI Verzija** (Terminal/Command Prompt)
```cmd
python dcdc_monitor_cli.py
```
- ✅ Deluje TAKOJ (brez namestitve)
- ✅ Prikazuje podatke v Command Prompt oknu
- ✅ 3 pretvorniki simulirani
- ✅ Ctrl+C za izhod

### 2️⃣ **GUI Demo** (Grafično okno)
```cmd
python dcdc_monitor_demo.py
```
- ✅ Grafično okno z gumbi
- ✅ Real-time podatki
- ✅ Simulirani CAN sporočila
- ℹ️ tkinter je običajno že vključen v Python za Windows

### 3️⃣ **Polna verzija** ⚠️ Omejeno na Windows
```cmd
python dcdc_monitor.py
```
- ⚠️ CAN komunikacija NE bo delovala brez posebnega driverja
- ⚠️ Potrebuje Windows CAN driver (PCAN, Kvaser, itd.)

---

## 🚀 HITER ZAČETEK (2 minuti)

### Korak 1: Preverite Python

Odprite **Command Prompt** (Win+R → `cmd` → Enter) in vnesite:

```cmd
python --version
```

**Če dobite napako:**
1. Prenesite Python: https://www.python.org/downloads/
2. Pri instalaciji označite "Add Python to PATH"
3. Ponovno zaženite Command Prompt

### Korak 2: Pojdite v mapo projekta

```cmd
cd C:\Users\VašeIme\Downloads\DC-DC_BDF
```
(prilagodite pot kjer ste shranili projekt)

### Korak 3: Zaženite aplikacijo

**Enostavno (priporočeno):**
```cmd
run_monitor.bat
```

**Ali izberite verzijo:**

```cmd
REM CLI verzija (terminal)
python dcdc_monitor_cli.py

REM GUI demo (grafično okno)
python dcdc_monitor_demo.py
```

---

## 📸 KAJ PRIČAKOVATI

### CLI Verzija (Command Prompt):
```
╔═══════════════════════════════════════════════════════╗
║   DC-DC Converter Monitor - COMMAND LINE INTERFACE   ║
╚═══════════════════════════════════════════════════════╝

┌─ Converter 1 ────────────────────────────
│  Status: Running
│  INPUT
│    Voltage:   418.2 V
│    Current:    46.8 A
│    Power:     19575 W
│  OUTPUT
│    Voltage:   364.5 V
│    Current:    60.0 A
└──────────────────────────────────────────────────────
```

### GUI Demo (Grafično okno):
- Okno z zavihki: "Real-time Data", "All Converters"
- Gumbi: "Start Simulation", "Stop"
- Grafi in tabele
- Obarvana sporočila

---

## ⚠️ OMEJITVE NA WINDOWS

### CAN Komunikacija
Windows ne podpira Linux SocketCAN direktno. Za realno CAN komunikacijo potrebujete:

1. **Windows CAN Driver:**
   - PCAN driver (Peak Systems)
   - Kvaser driver
   - Vector CAN driver

2. **Python-can mora biti konfiguriran za Windows:**
   ```cmd
   pip install python-can
   ```

3. **Nastavite interface v config.json:**
   ```json
   {
     "can_interface": "PCAN_USBBUS1",
     "can_bustype": "pcan"
   }
   ```

### Alternativa: Virtualni CAN
Za testiranje brez hardware-a uporabite **Demo Mode** - deluje perfektno!

---

## 🔧 NAMESTITEV ODVISNOSTI (opcijsko)

Če želite polno verzijo:

```cmd
pip install python-can cantools
```

---

## 📋 DIAGNOSTIKA

Preverite kaj deluje:

```cmd
python diagnose.py
```

To vam bo povedalo:
- ✅ Kaj deluje
- ❌ Kaj manjka
- 📝 Kako popraviti

---

## 💡 POGOSTA VPRAŠANJA

### Q: Kako odpreti Command Prompt?
A: Pritisnite `Win + R`, vtipkajte `cmd`, pritisnite Enter.

### Q: Aplikacija se zapre takoj?
A: To je normalno za Command Prompt. Uporabite `run_monitor.bat` ki doda `pause` na koncu.

### Q: Želim GUI okno, ne terminal?
A:
```cmd
python dcdc_monitor_demo.py
```

### Q: Kako dobim REALNE CAN podatke?
A: Potrebujete:
1. CAN vmesnik za Windows (USB adapter)
2.Driverje za Windows
3. Konfiguriran `python-can`

Za začetek uporabite **Demo Mode** ki simulira vse podatke!

---

## 🎯 PRIPOROČILO

Za Windows uporabnike:

1. **Začnite z Demo Mode:**
   ```cmd
   python dcdc_monitor_demo.py
   ```

2. **Če želite terminal:**
   ```cmd
   python dcdc_monitor_cli.py
   ```

3. **Za realne CAN podatke:**
   - Potrebujete CAN hardware + driverje
   - Kontaktirajte proizvajalca CAN adapterja za navodila

---

## ✅ POVZETEK

| Verzija | Windows? | Kako zagnati |
|---------|----------|--------------|
| CLI | ✅ Deluje | `python dcdc_monitor_cli.py` |
| GUI Demo | ✅ Deluje | `python dcdc_monitor_demo.py` |
| Polna | ⚠️ Potrebuje CAN driver | `python dcdc_monitor.py` |

**PRIPOROČILO:** Uporabite GUI Demo verzijo - deluje odlično na Windows!

---

## 🚀 HITRI UKAZI

```cmd
REM Odprite Command Prompt v mapi projekta, potem:

REM 1. CLI verzija
python dcdc_monitor_cli.py

REM 2. GUI Demo (PRIPOROČENO za Windows!)
python dcdc_monitor_demo.py

REM 3. Diagnostika
python diagnose.py

REM 4. Avtomatski launcher
run_monitor.bat
```

---

## 📞 POMOČ

Če nič ne deluje:

1. Preverite Python:
   ```cmd
   python --version
   ```

2. Poženite diagnostiko:
   ```cmd
   python diagnose.py
   ```

3. Poskusite GUI demo:
   ```cmd
   python dcdc_monitor_demo.py
   ```

---

**Windows uporabniki: GUI Demo verzija je najboljša izbira!** ✨

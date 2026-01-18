# 🚀 HITRI ZAČETEK / QUICK START

## 🎯 INSTANT START (30 sekund) - BREZ odvisnosti!

```bash
# Command-line monitor (deluje TAKOJ)
python3 dcdc_monitor_cli.py
```
**✓ Deluje takoj, brez namestitve!**

---

## 🖥️ GUI Demo Mode (1 minuta)

```bash
# Preveri odvisnosti
python3 check_dependencies.py

# GUI demo (potrebuje tkinter)
python3 dcdc_monitor_demo.py
```

---

## 🚀 Polna verzija (5 minut)

### 1️⃣ Namestitev (1 minuta)

```bash
# Namesti odvisnosti
pip3 install python-can cantools
sudo apt-get install python3-tk

# Preveri namestitev
python3 check_dependencies.py
```

### 2️⃣ Nastavitev virtualnega CAN vmesnika (1 minuta)

```bash
# Za testiranje BEZ strojne opreme
sudo modprobe vcan
sudo ip link add dev vcan0 type vcan
sudo ip link set up vcan0
```

### 3️⃣ Zagon aplikacije (1 minuta)

```bash
# Avtomatski launcher (priporoča se)
./run_monitor.sh

# Ali direktno
python3 dcdc_monitor.py
```

### 4️⃣ V aplikaciji:

1. **CAN Interface** → Izberi `vcan0`
2. **Klikni** → `▶ Start Monitoring`
3. **Spremljaj** → Podatke v real-time

---

## 🎯 Za PRODUKCIJO (z realnimi pretvorniki)

### 1️⃣ Nastavi fizični CAN vmesnik

```bash
# Namesto vcan0 uporabi can0
sudo ip link set can0 type can bitrate 500000
sudo ip link set can0 up

# Preveri
ip link show can0
```

### 2️⃣ V aplikaciji izberi `can0`

---

## 🔧 Hitre rešitve težav

### Problem: "No module named 'can'"
```bash
pip3 install --user python-can cantools
```

### Problem: "Permission denied"
```bash
sudo usermod -a -G dialout $USER
# Ponovno se prijavi
```

### Problem: "Cannot find can0"
```bash
# Uporabi vcan0 za testiranje
sudo modprobe vcan
sudo ip link add dev vcan0 type vcan
sudo ip link set up vcan0
```

---

## 📊 Funkcionalnost

✅ **Deluje TAKOJ**:
- Real-time spremljanje
- 3 pretvorniki hkrati
- Grafični vmesnik
- Beleženje podatkov
- Izvoz CSV/JSON

📚 **Več info**: Glej `README.md`

---

## 🎉 TO JE TO!

Aplikacija je pripravljena. Če vidiš GUI okno z zavihki, si uspešno zagnal monitor! 🚀

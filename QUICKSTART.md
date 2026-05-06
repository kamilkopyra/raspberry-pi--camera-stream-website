# 🚀 QUICK START - System Kamer (z logowaniem)

## ⚡ Szybkie Uruchomienie (5 minut)

### 1️⃣ Skopiuj pliki na Raspberry Pi
```bash
# Przez SCP z komputera:
scp -r camera_system/ pi@192.168.1.X:/home/pi/
```

### 2️⃣ Instalacja - AUTOMATYCZNA
```bash
cd camera_system
./install.sh
```

### 3️⃣ Podłącz kamery USB
```bash
# Sprawdź: 
ls /dev/video*
```

### 4️⃣ Uruchom serwer
```bash
python3 app.py
```

### 5️⃣ Otwórz w przeglądarce
```
http://192.168.1.X:5000
```

### 6️⃣ ZALOGUJ SIĘ 🔒
```
Login: admin
Hasło: admin123
```

**GOTOWE!** 🎉

---

## 🔐 WAŻNE - Zmień hasło!

Przed użyciem **ZMIEŃ DOMYŚLNE HASŁO**:

1. Edytuj `app.py`:
```bash
nano app.py
```

2. Znajdź (linia ~17):
```python
users = {
    "admin": generate_password_hash("admin123"),  # ZMIEŃ TO!
}
```

3. Wpisz nowe hasło:
```python
users = {
    "admin": generate_password_hash("TWOJE_MOCNE_HASLO"),
}
```

4. Zapisz (Ctrl+X, Y, Enter) i zrestartuj:
```bash
python3 app.py
```

**Więcej info:** Zobacz `LOGIN.md`

---

## 🎮 Sterowanie

### Mysz/Dotyk:
- Kliknij przyciski na ekranie

### Klawiatura:
- **W/A/S/D** - kamera termowizyjna
- **Strzałki** - kamera cyfrowa
- **SPACJA** - wyśrodkuj obie kamery

---

## 🌐 Dostęp do systemu

### Z Raspberry Pi (lokalnie):
```
http://localhost:5000
Login: admin
Hasło: admin123
```

### Z laptopa/telefonu (ta sama sieć WiFi):
```
http://192.168.1.X:5000
Login: admin
Hasło: admin123
```
*(gdzie X = IP Raspberry Pi, sprawdź: `hostname -I`)*

### Z internetu (spoza sieci):
**NIE ZALECANE BEZ SSL!**

Opcje:
- Port forwarding na routerze (⚠️ niebezpieczne bez HTTPS)
- ngrok: `ngrok http 5000` (bezpieczniejsze)
- VPN: Tailscale/Zerotier (najbezpieczniejsze)

---

## ❌ Rozwiązywanie problemów

### Kamery nie działają
```bash
v4l2-ctl --list-devices
python3 test_system.py
```

### Nie mogę się zalogować
Sprawdź login/hasło w `app.py`:
```python
users = {
    "admin": generate_password_hash("admin123"),  # To jest hasło
}
```

### Brak streamu w przeglądarce
```bash
# Sprawdź logi
python3 app.py
```

### GPIO nie działa
```bash
sudo usermod -a -G gpio pi
sudo reboot
```

---

## ✅ Checklist

- [ ] Pliki skopiowane na Raspberry Pi
- [ ] `./install.sh` wykonany
- [ ] Kamery podłączone (`ls /dev/video*`)
- [ ] **HASŁO ZMIENIONE w app.py**
- [ ] `python3 app.py` uruchomiony
- [ ] Zalogowano przez przeglądarkę
- [ ] Stream wideo działa
- [ ] Przyciski sterowania działają

---

**Gotowe! System zabezpieczony hasłem działa!** 🎉🔒

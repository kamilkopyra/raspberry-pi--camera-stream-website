# 🎥 System Monitoringu Kamer

System do obsługi dwóch kamer (termowizyjna + cyfrowa) z możliwością sterowania przez przeglądarkę.

## 🚀 Funkcje

- ✅ Stream wideo z dwóch kamer jednocześnie (MJPEG)
- ✅ Sterowanie pozycją kamer (lewo/prawo/góra/dół)
- ✅ Interfejs webowy (Flask + HTML/CSS/JS)
- ✅ Obsługa serwomechanizmów przez GPIO (Raspberry Pi)
- ✅ Responsywny design (działa na telefonie i komputerze)
- ✅ Obsługa klawiatury (WASD + strzałki)
- 🔜 Integracja z YOLO do wykrywania ludzi

---

## 📦 Instalacja

### 1. Sklonuj/skopiuj pliki na Raspberry Pi

```bash
cd ~
# Skopiuj folder camera_system na Raspberry Pi
```

### 2. Zainstaluj zależności

```bash
cd camera_system

# Utwórz wirtualne środowisko (opcjonalnie, ale zalecane)
python3 -m venv venv
source venv/bin/activate

# Zainstaluj wymagane biblioteki
pip install -r requirements.txt
```

**Uwaga dla Raspberry Pi:**
```bash
# Jeśli masz problemy z instalacją OpenCV, użyj:
sudo apt-get update
sudo apt-get install python3-opencv python3-flask
```

---

## 🔌 Podłączenie Sprzętu

### Kamery
- Podłącz kamery przez USB
- Sprawdź ID kamer: `ls /dev/video*`
- Domyślnie:
  - Kamera termowizyjna = `/dev/video0`
  - Kamera cyfrowa = `/dev/video1`

### Serwomechanizmy (GPIO)

**Schemat pinów (BCM):**

```
Kamera Termowizyjna:
  - GPIO 17 → Servo poziome (lewo/prawo)
  - GPIO 27 → Servo pionowe (góra/dół)

Kamera Cyfrowa:
  - GPIO 22 → Servo poziome
  - GPIO 23 → Servo pionowe

Zasilanie:
  - 5V → Pin 2 lub 4
  - GND → Pin 6, 9, 14, 20, 25, 30, 34, 39
```

**Schemat podłączenia serwa:**
```
Servo:
  - Czerwony (VCC) → 5V
  - Brązowy/Czarny (GND) → GND
  - Pomarańczowy/Żółty (Signal) → GPIO
```

⚠️ **WAŻNE:** Jeśli używasz mocnych serw, dodaj zewnętrzne zasilanie (nie z Raspberry Pi)!

---

## ▶️ Uruchomienie

### Standardowe uruchomienie

```bash
cd camera_system
python3 app.py
```

### Uruchomienie w tle (jako serwis)

```bash
# 1. Utwórz plik serwisu
sudo nano /etc/systemd/system/camera-system.service
```

Wklej:
```ini
[Unit]
Description=Camera System
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/camera_system
ExecStart=/usr/bin/python3 /home/pi/camera_system/app.py
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# 2. Włącz serwis
sudo systemctl daemon-reload
sudo systemctl enable camera-system.service
sudo systemctl start camera-system.service

# 3. Sprawdź status
sudo systemctl status camera-system.service
```

---

## 🌐 Dostęp do Interfejsu

Po uruchomieniu serwera:

1. **Z Raspberry Pi:**
   ```
   http://localhost:5000
   ```

2. **Z innego urządzenia w tej samej sieci:**
   ```
   http://192.168.1.X:5000
   ```
   (gdzie X to adres IP Raspberry Pi)

### Sprawdzenie IP Raspberry Pi:
```bash
hostname -I
```

---

## 🎮 Sterowanie

### Mysz/Dotyk
- Kliknij przyciski na ekranie

### Klawiatura
- **Kamera termowizyjna:** `W` `A` `S` `D`
- **Kamera cyfrowa:** `↑` `←` `↓` `→`
- **Wyśrodkuj obie:** `SPACJA`

---

## ⚙️ Konfiguracja

### Zmiana ID kamer

Edytuj plik `app.py`:

```python
CAMERA_THERMAL_ID = 0  # Zmień na właściwe ID
CAMERA_DIGITAL_ID = 1  # Zmień na właściwe ID
```

### Zmiana pinów GPIO

Edytuj plik `camera_controller.py`:

```python
CAMERA_SERVOS = {
    'thermal': {
        'horizontal': 17,  # Twój pin
        'vertical': 27     # Twój pin
    },
    'digital': {
        'horizontal': 22,  # Twój pin
        'vertical': 23     # Twój pin
    }
}
```

### Zmiana jakości/rozdzielczości streamu

W pliku `app.py`:

```python
# Rozdzielczość
self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)   # Szerokość
self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)  # Wysokość

# Jakość JPEG (0-100)
cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
```

---

## 🔧 Rozwiązywanie Problemów

### Kamery nie działają

```bash
# Sprawdź dostępne kamery
v4l2-ctl --list-devices

# Sprawdź czy OpenCV widzi kamery
python3 -c "import cv2; print(cv2.VideoCapture(0).isOpened())"
```

### GPIO nie działa

```bash
# Sprawdź uprawnienia
sudo usermod -a -G gpio pi
sudo usermod -a -G video pi

# Restart po dodaniu do grup
sudo reboot
```

### Stream się zawiesi

- Sprawdź czy kamery są dobrze podłączone
- Zmniejsz rozdzielczość/jakość w `app.py`
- Sprawdź logi: `journalctl -u camera-system.service -f`

---

## 📊 Struktura Projektu

```
camera_system/
├── app.py                  # Główny serwer Flask
├── camera_controller.py    # Sterowanie serwami (GPIO)
├── requirements.txt        # Zależności Pythona
├── README.md              # Ten plik
├── templates/
│   └── index.html         # Interfejs WWW
└── static/                # (opcjonalnie pliki CSS/JS)
```

---

## 🎯 TODO / Rozszerzenia

- [ ] Integracja z YOLO (wykrywanie ludzi)
- [ ] Automatyczne śledzenie osób
- [ ] Nagrywanie wideo
- [ ] Zapis zrzutów ekranu
- [ ] Logowanie zdarzeń
- [ ] Uwierzytelnianie użytkowników
- [ ] Streaming przez UDP (zamiast HTTP)
- [ ] Aplikacja mobilna

---

## 📝 Notatki

### Transmisja przez UDP (opcjonalnie)

Jeśli chcesz zamiast HTTP używać UDP:

**Nadawca (Raspberry Pi):**
```python
import socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.sendto(frame_bytes, ('192.168.1.100', 5000))
```

**Odbiorca (laptop):**
```python
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('0.0.0.0', 5000))
data, addr = sock.recvfrom(65535)
```

---

## 🤝 Pomoc

Masz problem? Sprawdź:
1. Logi systemowe: `journalctl -xe`
2. Logi Flaska w konsoli
3. Sprawdź czy kamery działają: `cheese` lub `vlc v4l2:///dev/video0`

---

**Powodzenia! 🚀**

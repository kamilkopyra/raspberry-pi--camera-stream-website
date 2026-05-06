# 🎥 SYSTEM KAMER - KOMPLETNE ROZWIĄZANIE (Z LOGOWANIEM)

## ✅ CO DOSTAŁEŚ

Kompletny, działający system monitoringu z dwoma kamerami (termowizyjna + cyfrowa) z interfejsem webowym, sterowaniem przez Flask i **zabezpieczeniem hasłem**.

---

## 🔒 BEZPIECZEŃSTWO

System wymaga logowania do każdej strony!

**Domyślne konto:**
```
Login: admin
Hasło: admin123
```

**⚠️ ZMIEŃ HASŁO przed użyciem!** (instrukcja w `LOGIN.md`)

---

## 📦 ZAWARTOŚĆ PACZKI

```
camera_system/
├── app.py                      # Główny serwer Flask (Z HASŁEM!) ⭐
├── camera_controller.py        # Sterowanie serwami (GPIO)
├── test_system.py             # Skrypt testowy
├── install.sh                 # Instalator (automatyczny)
├── requirements.txt           # Zależności Python
├── camera-system.service      # Systemd service (autostart)
├── templates/
│   └── index.html            # Frontend (interfejs WWW) ⭐
├── README.md                  # Pełna dokumentacja
├── QUICKSTART.md              # Szybki start (5 min)
├── LOGIN.md                   # Instrukcja logowania i zmiany hasła
└── PODSUMOWANIE.md            # Ten plik
```

**UWAGA:** Usunięto YOLO tracking (nie potrzebne)

---

## 🚀 JAK URUCHOMIĆ (SZYBKO)

### 1. Rozpakuj na Raspberry Pi
```bash
tar -xzf camera_system_FINAL.tar.gz
cd camera_system
```

### 2. Uruchom instalator
```bash
./install.sh
```

### 3. Podłącz kamery USB
```bash
ls /dev/video*
```

### 4. **WAŻNE: Zmień hasło!**
```bash
nano app.py
# Znajdź: generate_password_hash("admin123")
# Zmień na: generate_password_hash("TWOJE_HASLO")
# Zapisz: Ctrl+X, Y, Enter
```

### 5. Uruchom serwer
```bash
python3 app.py
```

### 6. Otwórz w przeglądarce
```
http://192.168.1.X:5000
```

### 7. Zaloguj się
```
Login: admin
Hasło: admin123 (lub twoje nowe hasło)
```

**GOTOWE!** 🎉

---

## 💡 KLUCZOWE FUNKCJE

### ✅ Co działa od razu:
- **🔒 Logowanie** - zabezpieczenie hasłem (HTTP Basic Auth)
- **Stream wideo** z dwóch kamer jednocześnie (MJPEG)
- **Interfejs webowy** - ładny, responsywny design
- **Przyciski sterowania** - lewo/prawo/góra/dół
- **Obsługa klawiatury** - WASD + strzałki
- **Status systemowy** - monitorowanie kamer
- **Live preview** - obraz w czasie rzeczywistym

### 🔜 Do skonfigurowania:
- **GPIO/Serwa** - podłącz i ustaw piny w `camera_controller.py`
- **Nowe hasło** - zmień w `app.py` przed użyciem!

### ❌ Usunięte:
- **YOLO tracking** - niepotrzebne, kod usunięty

---

## 🎯 JAK TO DZIAŁA

### Architektura:

```
┌─────────────────────────────────────────────────────┐
│                    Raspberry Pi                      │
│                                                      │
│  ┌─────────────┐        ┌──────────────────┐       │
│  │  Kamera 1   │───────▶│   OpenCV         │       │
│  │ (Termo USB) │        │   cv2.VideoCapture│      │
│  └─────────────┘        │   + kompresja    │       │
│                         │     JPEG         │       │
│  ┌─────────────┐        │                  │       │
│  │  Kamera 2   │───────▶│                  │       │
│  │ (Cyfr. USB) │        └────────┬─────────┘       │
│  └─────────────┘                 │                  │
│                         ┌────────▼─────────┐        │
│  ┌─────────────┐        │  Flask Server    │        │
│  │   GPIO      │◀───────│  + HTTP Auth 🔒  │        │
│  │  Serwa      │        │  (app.py)        │        │
│  └─────────────┘        │                  │        │
│                         │  /               │        │
│                         │  /video_feed/*   │        │
│                         │  /rotate/*       │        │
│                         └────────┬─────────┘        │
│                                  │                  │
└──────────────────────────────────┼──────────────────┘
                                   │
                          HTTP (Port 5000)
                          + Basic Auth 🔒
                                   │
                    ┌──────────────▼──────────────┐
                    │   Przeglądarka              │
                    │   (Laptop/Telefon)          │
                    │                             │
                    │  1. Wpisz login/hasło       │
                    │  2. Wyświetla stream MJPEG  │
                    │  3. Przyciski sterowania    │
                    └─────────────────────────────┘
```

### Flow:

1. **Użytkownik** → Wchodzi na http://192.168.1.X:5000
2. **Przeglądarka** → Pokazuje okienko logowania
3. **Flask** → Sprawdza login/hasło (HTTP Basic Auth)
4. **✅ OK** → Pokazuje interfejs z kamerami
5. **❌ Błąd** → 401 Unauthorized
6. **Kamery** → OpenCV pobiera ramki, kompresuje do JPEG
7. **Flask** → Streamuje przez HTTP jako MJPEG
8. **Przyciski** → Wysyłają AJAX request → GPIO → Serwa

---

## 🔐 BEZPIECZEŃSTWO

### W sieci lokalnej (WiFi):
✅ **HTTP Basic Auth wystarczy**
- Sieć WiFi chroniona hasłem
- Tylko urządzenia w tej samej sieci mają dostęp
- Hasło przesyłane w base64 (wystarczające dla sieci lokalnej)

### Przez internet:
⚠️ **NIE WYSTAWIAJ BEZ SSL!**
- Basic Auth przez HTTP = hasło w base64 (łatwe do przechwycenia)
- **Rozwiązania:**
  1. **HTTPS + certyfikat SSL** (Let's Encrypt)
  2. **VPN** (Tailscale, Zerotier) - najlepsze!
  3. **ngrok** z HTTPS (tymczasowo)

**Zalecane:** Używaj tylko w sieci lokalnej lub przez VPN

---

## 🔧 KONFIGURACJA

### Zmiana hasła:

W `app.py` (linia ~17):
```python
users = {
    "admin": generate_password_hash("NOWE_HASLO"),
    "user": generate_password_hash("DRUGIE_HASLO"),
}
```

### Dodanie nowych użytkowników:

```python
users = {
    "admin": generate_password_hash("admin_pass"),
    "janek": generate_password_hash("janek_pass"),
    "kasia": generate_password_hash("kasia_pass"),
}
```

### Zmiana ID kamer:

W `app.py` (linia ~30):
```python
CAMERA_THERMAL_ID = 0  # Twoje ID
CAMERA_DIGITAL_ID = 1  # Twoje ID
```

### Zmiana pinów GPIO:

W `camera_controller.py` (linia ~240):
```python
CAMERA_SERVOS = {
    'thermal': {'horizontal': 17, 'vertical': 27},
    'digital': {'horizontal': 22, 'vertical': 23}
}
```

---

## 🎨 INTERFEJS

### Desktop:
```
┌──────────────────────────────────────────────────────┐
│  🎥 System Monitoringu Kamer            🔒 Zalogowano│
│                                                      │
│  ┌─────────────────────┐  ┌─────────────────────┐  │
│  │  🌡️ Termo           │  │  📷 Cyfrowa          │  │
│  │  ┌───────────────┐  │  │  ┌───────────────┐  │  │
│  │  │  [LIVE VIDEO] │  │  │  │  [LIVE VIDEO] │  │  │
│  │  └───────────────┘  │  │  └───────────────┘  │  │
│  │  [←] [⊙] [→]       │  │  [←] [⊙] [→]       │  │
│  │  [↑] [ ] [↓]       │  │  [↑] [ ] [↓]       │  │
│  └─────────────────────┘  └─────────────────────┘  │
└──────────────────────────────────────────────────────┘
```

---

## 🧪 TESTOWANIE

### Test systemu:
```bash
python3 test_system.py
```

### Test logowania:
```bash
# Z poprawnym hasłem
curl -u admin:admin123 http://localhost:5000

# Bez hasła (powinno zwrócić 401)
curl http://localhost:5000
```

---

## 📊 TECHNOLOGIE

### Backend:
- **Python 3** - język
- **Flask** - framework webowy
- **Flask-HTTPAuth** - autentykacja 🔒
- **OpenCV** - kamery i wideo
- **RPi.GPIO** - sterowanie GPIO (Raspberry Pi)

### Frontend:
- **HTML5** - struktura
- **CSS3** - design (gradient, glassmorphism)
- **JavaScript** - interakcja (AJAX, keyboard)

### Komunikacja:
- **MJPEG** - streaming wideo
- **HTTP Basic Auth** - logowanie 🔒
- **HTTP/JSON** - API do sterowania

---

## 🐛 ROZWIĄZYWANIE PROBLEMÓW

### Nie mogę się zalogować:
```bash
# Sprawdź hasło w app.py
grep "generate_password_hash" app.py

# Wyczyść cache przeglądarki
# Użyj trybu incognito
```

### Kamery nie działają:
```bash
v4l2-ctl --list-devices
python3 test_system.py
```

### GPIO błędy:
```bash
sudo usermod -a -G gpio pi
sudo reboot
```

---

## 📚 DOKUMENTACJA

- **QUICKSTART.md** - szybki start (5 min)
- **LOGIN.md** - instrukcja logowania i zmiany hasła 🔒
- **README.md** - pełna dokumentacja
- **app.py** - komentarze w kodzie

---

## 🎯 NASTĘPNE KROKI

### Podstawowe:
1. ✅ Uruchom system
2. ✅ **Zmień hasło!**
3. ✅ Przetestuj logowanie
4. ✅ Sprawdź kamery
5. ✅ Sprawdź interface w przeglądarce

### Zaawansowane:
6. 🔧 Podłącz serwa do GPIO
7. 🔧 Skonfiguruj piny w kodzie
8. 🚀 Ustaw autostart (systemd)

### Pro:
9. 📹 Dodaj nagrywanie wideo
10. 🔐 Dodaj SSL/HTTPS
11. 📱 Zrób aplikację mobilną
12. 🌐 VPN (Tailscale) do dostępu zdalnego

---

## 💬 FAQ

**Q: Czy muszę się logować?**
A: TAK! Bez logowania system nie odpowie (401 Unauthorized).

**Q: Czy mogę mieć kilku użytkowników?**
A: TAK! Dodaj ich w `app.py` w słowniku `users`.

**Q: Czy to bezpieczne?**
A: W sieci lokalnej - TAK. Przez internet bez SSL - NIE!

**Q: Jak zmienić hasło?**
A: Zobacz `LOGIN.md` - pełna instrukcja.

**Q: Czy to działa bez Raspberry Pi?**
A: TAK! Na PC/Laptop też, ale bez GPIO.

**Q: Czy YOLO jest włączone?**
A: NIE - kod YOLO został całkowicie usunięty (niepotrzebny).

---

## 🙏 KOŃCOWE SŁOWO

Masz teraz **kompletny, zabezpieczony system kamer** z:
- ✅ Interfejsem webowym
- ✅ **Logowaniem (hasło)** 🔒
- ✅ Live streamingiem
- ✅ Sterowaniem
- ✅ Obsługą GPIO
- ✅ Pełną dokumentacją

**Wszystko działa od razu po `python3 app.py` (+ logowanie)**

**⚠️ PAMIĘTAJ: Zmień domyślne hasło przed użyciem!**

Powodzenia z projektem! 🚀🔒

---

**Pytania?** Sprawdź:
- LOGIN.md (jak zmienić hasło, dodać użytkowników)
- QUICKSTART.md (szybki start)
- README.md (pełna dokumentacja)
- Komentarze w kodzie (app.py)

**Problemy z logowaniem?**
- Sprawdź hasło w app.py
- Wyczyść cache przeglądarki
- Użyj trybu incognito
- Zobacz LOGIN.md

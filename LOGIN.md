# 🔒 LOGOWANIE DO SYSTEMU

## Domyślne konta:

### Konto administratora:
```
Login: admin
Hasło: admin123
```

### Konto użytkownika:
```
Login: user
Hasło: password
```

---

## ⚠️ ZMIEŃ HASŁA PRZED UŻYCIEM!

### Jak zmienić hasło:

1. Otwórz plik `app.py`

2. Znajdź sekcję (koło linii 17):
```python
users = {
    "admin": generate_password_hash("admin123"),
    "user": generate_password_hash("password")
}
```

3. Zmień hasła:
```python
users = {
    "admin": generate_password_hash("TWOJE_NOWE_HASŁO"),
    "user": generate_password_hash("DRUGIE_HASŁO")
}
```

4. Zapisz i zrestartuj serwer:
```bash
# Zatrzymaj (Ctrl+C)
# Uruchom ponownie
python3 app.py
```

---

## 🔐 Dodawanie nowych użytkowników:

W pliku `app.py`:
```python
users = {
    "admin": generate_password_hash("haslo123"),
    "janek": generate_password_hash("janekhaslo"),
    "asia": generate_password_hash("asiahaslo"),
    # Dodaj kolejnych...
}
```

---

## 🌐 Jak działa logowanie:

1. Wchodzisz na `http://192.168.1.X:5000`
2. Przeglądarka pokaże okienko logowania (HTTP Basic Auth)
3. Wpisujesz login i hasło
4. Jeśli poprawne → widzisz interfejs kamer
5. Jeśli błędne → "401 Unauthorized"

**Ważne:** Przeglądarka zapamiętuje login/hasło na czas sesji!

---

## 🔓 Wylogowanie:

### Chrome/Edge:
- Zamknij wszystkie karty ze stroną
- Albo: Otwórz tryb incognito

### Firefox:
- Ctrl+Shift+Del → Wyczyść ciasteczka
- Albo: Tryb prywatny

### Safari:
- Zamknij okno przeglądarki
- Albo: Tryb prywatny

**Lub po prostu:** `http://wyloguj@192.168.1.X:5000` (czasami działa)

---

## 🛡️ Bezpieczeństwo:

### W sieci lokalnej:
- ✅ Basic Auth wystarczy
- Sieć WiFi jest zabezpieczona hasłem

### Przez internet:
- ⚠️ Basic Auth wysyła hasło w base64 (łatwe do przechwycenia)
- 🔒 Używaj HTTPS (certyfikat SSL)
- 🔒 Lub VPN (Tailscale/Zerotier)

**NIE WYSTAWIAJ PRZEZ HTTP NA INTERNET BEZ SSL!**

---

## 📝 Przykłady użycia:

### Dostęp z przeglądarki:
```
http://192.168.1.50:5000
→ Wpisz: admin / admin123
```

### Dostęp z curl (testowanie):
```bash
curl -u admin:admin123 http://192.168.1.50:5000
```

### Dostęp z Python:
```python
import requests
from requests.auth import HTTPBasicAuth

response = requests.get(
    'http://192.168.1.50:5000',
    auth=HTTPBasicAuth('admin', 'admin123')
)
print(response.text)
```

---

## 🚨 Zapomniałem hasła!

1. Otwórz `app.py`
2. Usuń hash i wpisz nowe hasło:
```python
users = {
    "admin": generate_password_hash("nowe_haslo_123")
}
```
3. Zapisz i zrestartuj serwer

---

## ✅ Sprawdzenie czy działa:

```bash
# Test logowania
curl -u admin:admin123 http://localhost:5000

# Powinno zwrócić HTML strony

# Test bez logowania
curl http://localhost:5000

# Powinno zwrócić: 401 Unauthorized
```

---

**GOTOWE!** 🎉

Teraz system wymaga logowania do każdego endpointa:
- `/` - strona główna
- `/video_feed/thermal` - stream termowizyjny
- `/video_feed/digital` - stream cyfrowy
- `/rotate/*` - sterowanie
- `/center/*` - centrowanie
- `/status` - status

**Bez poprawnego loginu i hasła - nie ma dostępu!** 🔒

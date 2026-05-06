#!/bin/bash

echo "================================"
echo "🎥 Instalacja Systemu Kamer"
echo "================================"
echo ""

# Kolory
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Sprawdź czy jesteś na Raspberry Pi
if [ -f /proc/device-tree/model ]; then
    MODEL=$(cat /proc/device-tree/model)
    echo -e "${GREEN}✓${NC} Wykryto: $MODEL"
else
    echo -e "${YELLOW}⚠${NC} Nie wykryto Raspberry Pi - niektóre funkcje mogą nie działać"
fi

echo ""
echo "📦 Instalacja zależności systemowych..."

# Aktualizacja pakietów
sudo apt-get update

# Instalacja Pythona i bibliotek
sudo apt-get install -y python3 python3-pip python3-opencv

# Instalacja Flask i innych zależności
echo ""
echo "📦 Instalacja bibliotek Pythona..."
pip3 install flask opencv-python numpy

# Sprawdź czy RPi.GPIO jest dostępne (tylko na Raspberry Pi)
if [ -f /proc/device-tree/model ]; then
    echo ""
    echo "📦 Instalacja RPi.GPIO..."
    sudo apt-get install -y python3-rpi.gpio
    pip3 install RPi.GPIO
fi

echo ""
echo "🔍 Sprawdzanie kamer..."

# Lista urządzeń video
if ls /dev/video* 1> /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Znalezione kamery:"
    ls -la /dev/video*
    
    echo ""
    v4l2-ctl --list-devices 2>/dev/null || echo -e "${YELLOW}⚠${NC} v4l2-ctl niedostępny (zainstaluj: sudo apt-get install v4l-utils)"
else
    echo -e "${RED}✗${NC} Nie znaleziono kamer USB"
    echo "   Podłącz kamery i uruchom ponownie"
fi

echo ""
echo "👤 Dodawanie użytkownika do grup..."

# Dodaj użytkownika do grup gpio i video
if groups | grep -q gpio; then
    echo -e "${GREEN}✓${NC} Użytkownik już w grupie gpio"
else
    sudo usermod -a -G gpio $USER
    echo -e "${GREEN}✓${NC} Dodano do grupy gpio"
fi

if groups | grep -q video; then
    echo -e "${GREEN}✓${NC} Użytkownik już w grupie video"
else
    sudo usermod -a -G video $USER
    echo -e "${GREEN}✓${NC} Dodano do grupy video"
fi

echo ""
echo "🔧 Tworzenie pliku konfiguracyjnego..."

# Utwórz plik config.py jeśli nie istnieje
if [ ! -f config.py ]; then
    cat > config.py << 'EOF'
# Konfiguracja systemu kamer

# ID kamer (sprawdź: ls /dev/video*)
CAMERA_THERMAL_ID = 0
CAMERA_DIGITAL_ID = 1

# Piny GPIO (BCM) dla serwomechanizmów
GPIO_THERMAL_HORIZONTAL = 17
GPIO_THERMAL_VERTICAL = 27
GPIO_DIGITAL_HORIZONTAL = 22
GPIO_DIGITAL_VERTICAL = 23

# Ustawienia streamu
STREAM_WIDTH = 640
STREAM_HEIGHT = 480
STREAM_FPS = 30
JPEG_QUALITY = 85

# Serwer Flask
FLASK_HOST = '0.0.0.0'
FLASK_PORT = 5000
FLASK_DEBUG = False
EOF
    echo -e "${GREEN}✓${NC} Utworzono config.py"
else
    echo -e "${YELLOW}⚠${NC} Plik config.py już istnieje - pominięto"
fi

echo ""
echo "================================"
echo -e "${GREEN}✓ Instalacja zakończona!${NC}"
echo "================================"
echo ""
echo "📝 Następne kroki:"
echo ""
echo "1. Podłącz kamery USB"
echo "2. Sprawdź ID kamer:"
echo -e "   ${YELLOW}ls /dev/video*${NC}"
echo ""
echo "3. Dostosuj konfigurację (jeśli potrzeba):"
echo -e "   ${YELLOW}nano config.py${NC}"
echo ""
echo "4. Uruchom serwer:"
echo -e "   ${YELLOW}python3 app.py${NC}"
echo ""
echo "5. Otwórz przeglądarkę:"
echo -e "   ${YELLOW}http://$(hostname -I | awk '{print $1}'):5000${NC}"
echo ""
echo "🎮 Sterowanie klawiaturą:"
echo "   Kamera termowizyjna: W/A/S/D"
echo "   Kamera cyfrowa: strzałki"
echo "   Wyśrodkuj: SPACJA"
echo ""
echo -e "${YELLOW}⚠  UWAGA:${NC} Jeśli dodano do nowych grup, wyloguj się i zaloguj ponownie"
echo -e "           lub uruchom: ${YELLOW}newgrp gpio${NC}"
echo ""

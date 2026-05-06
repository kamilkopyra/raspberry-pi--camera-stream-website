#!/usr/bin/env python3
"""
Skrypt testowy systemu kamer
Sprawdza dostępność kamer, bibliotek i konfiguracji
"""

import sys
import os

print("\n" + "="*50)
print("🔍 TEST SYSTEMU KAMER")
print("="*50 + "\n")

# ===== TEST 1: Biblioteki Python =====
print("📚 Test 1: Sprawdzanie bibliotek Python...")

libraries = {
    'flask': False,
    'cv2': False,
    'numpy': False,
    'RPi.GPIO': False
}

for lib in libraries:
    try:
        __import__(lib.replace('.', '_') if '.' in lib else lib)
        libraries[lib] = True
        print(f"  ✓ {lib:<15} - OK")
    except ImportError:
        print(f"  ✗ {lib:<15} - BRAK")

print()

# ===== TEST 2: Kamery USB =====
print("📷 Test 2: Sprawdzanie kamer USB...")

import subprocess
try:
    result = subprocess.run(['ls', '/dev/video*'], 
                          capture_output=True, text=True, shell=True)
    if result.returncode == 0 and result.stdout:
        cameras = result.stdout.strip().split('\n')
        print(f"  ✓ Znaleziono {len(cameras)} urządzeń video:")
        for cam in cameras:
            print(f"    - {cam}")
    else:
        print("  ✗ Nie znaleziono kamer USB")
        print("    Sprawdź: ls /dev/video*")
except Exception as e:
    print(f"  ✗ Błąd: {e}")

print()

# ===== TEST 3: OpenCV - test kamery =====
print("🎥 Test 3: Test OpenCV - próba otwarcia kamery...")

if libraries['cv2']:
    import cv2
    
    for cam_id in [0, 1]:
        cap = cv2.VideoCapture(cam_id)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                h, w = frame.shape[:2]
                print(f"  ✓ Kamera {cam_id}: OK (rozdzielczość: {w}x{h})")
            else:
                print(f"  ⚠ Kamera {cam_id}: Otwarta ale brak obrazu")
            cap.release()
        else:
            print(f"  ✗ Kamera {cam_id}: Nie można otworzyć")
else:
    print("  ⚠ OpenCV niedostępny - pomiń test")

print()

# ===== TEST 4: GPIO (tylko Raspberry Pi) =====
print("🔌 Test 4: Sprawdzanie GPIO...")

if libraries['RPi.GPIO']:
    try:
        import RPi.GPIO as GPIO
        GPIO.setmode(GPIO.BCM)
        print("  ✓ GPIO dostępne")
        GPIO.cleanup()
    except Exception as e:
        print(f"  ✗ Błąd GPIO: {e}")
else:
    print("  ⚠ RPi.GPIO niedostępny (normalnie na PC/Laptop)")

print()

# ===== TEST 5: Struktura plików =====
print("📁 Test 5: Sprawdzanie struktury projektu...")

files_to_check = [
    'app.py',
    'camera_controller.py',
    'yolo_tracker.py',
    'requirements.txt',
    'README.md',
    'templates/index.html'
]

for file in files_to_check:
    if os.path.exists(file):
        print(f"  ✓ {file:<30} - OK")
    else:
        print(f"  ✗ {file:<30} - BRAK")

print()

# ===== TEST 6: Konfiguracja sieci =====
print("🌐 Test 6: Konfiguracja sieciowa...")

try:
    result = subprocess.run(['hostname', '-I'], 
                          capture_output=True, text=True)
    if result.returncode == 0:
        ips = result.stdout.strip().split()
        print(f"  ✓ Adres IP: {ips[0] if ips else 'brak'}")
        if ips:
            print(f"    Dostęp do strony: http://{ips[0]}:5000")
    else:
        print("  ⚠ Nie można pobrać adresu IP")
except Exception as e:
    print(f"  ⚠ {e}")

print()

# ===== PODSUMOWANIE =====
print("="*50)
print("📊 PODSUMOWANIE")
print("="*50)

critical_ok = libraries['flask'] and libraries['cv2'] and libraries['numpy']

if critical_ok:
    print("\n✅ System GOTOWY do uruchomienia!")
    print("\nKomenda do uruchomienia:")
    print("  python3 app.py")
    print("\nNastępnie otwórz w przeglądarce:")
    try:
        result = subprocess.run(['hostname', '-I'], capture_output=True, text=True)
        if result.returncode == 0:
            ips = result.stdout.strip().split()
            if ips:
                print(f"  http://{ips[0]}:5000")
    except:
        pass
    print("  http://localhost:5000")
else:
    print("\n⚠️  System NIE jest gotowy")
    print("\nBrakujące komponenty:")
    
    if not libraries['flask']:
        print("  - Flask: pip install flask")
    if not libraries['cv2']:
        print("  - OpenCV: pip install opencv-python")
    if not libraries['numpy']:
        print("  - NumPy: pip install numpy")
    
    print("\nUruchom:")
    print("  pip install -r requirements.txt")

print("\n" + "="*50 + "\n")

# ===== OPCJONALNY TEST LIVE =====
if critical_ok and '--live' in sys.argv:
    print("\n🎬 Uruchamiam test LIVE kamery (naciśnij 'q' aby zakończyć)...\n")
    import cv2
    import time
    
    cap = cv2.VideoCapture(0)
    
    if cap.isOpened():
        print("✓ Kamera otwarta, pokazuję obraz...")
        start_time = time.time()
        frame_count = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            frame_count += 1
            elapsed = time.time() - start_time
            fps = frame_count / elapsed if elapsed > 0 else 0
            
            # Dodaj informacje na ekranie
            cv2.putText(frame, f"FPS: {fps:.1f}", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(frame, "Test systemu kamer", (10, 70),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            cv2.imshow('Test Kamery', frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        cap.release()
        cv2.destroyAllWindows()
        print(f"\n✓ Test zakończony. Średnie FPS: {fps:.1f}")
    else:
        print("✗ Nie można otworzyć kamery")

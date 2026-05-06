#!/usr/bin/env python3
"""
System obsługi dwóch kamer (termowizyjna + cyfrowa) z sterowaniem przez Flask
Z PODSTAWOWĄ AUTENTYKACJĄ (login/hasło)
"""

from flask import Flask, Response, render_template, request, jsonify
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
import cv2
import threading
import time

app = Flask(__name__)
auth = HTTPBasicAuth()

# ============= KONFIGURACJA UŻYTKOWNIKÓW =============
# ZMIEŃ LOGIN I HASŁO TUTAJ!
users = {
    "admin": generate_password_hash("admin123"),  # Login: admin, Hasło: admin123
    "user": generate_password_hash("password")     # Login: user, Hasło: password
}

@auth.verify_password
def verify_password(username, password):
    if username in users and check_password_hash(users.get(username), password):
        return username
    return None

# Konfiguracja kamer
CAMERA_THERMAL_ID = 0  # ID kamery termowizyjnej
CAMERA_DIGITAL_ID = 0  # ID kamery cyfrowej

# Globalne obiekty kamer
cameras = {
    'thermal': None,
    'digital': None
}

# Lock dla bezpiecznego dostępu do kamer
camera_locks = {
    'thermal': threading.Lock(),
    'digital': threading.Lock()
}

# Pozycje kamer (kąty w stopniach)
camera_positions = {
    'thermal': 90,  # Pozycja środkowa
    'digital': 90
}


class CameraStream:
    """Klasa do obsługi streamu z kamery"""
    
    def __init__(self, camera_id, name):
        self.camera_id = camera_id
        self.name = name
        self.camera = None
        self.is_running = False
        
    def initialize(self):
        """Inicjalizacja kamery"""
        try:
            self.camera = cv2.VideoCapture(self.camera_id)
            # Ustawienia kamery
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.camera.set(cv2.CAP_PROP_FPS, 30)
            self.is_running = True
            print(f"[OK] Kamera {self.name} zainicjalizowana (ID: {self.camera_id})")
            return True
        except Exception as e:
            print(f"[ERROR] Nie można zainicjalizować kamery {self.name}: {e}")
            return False
    
    def get_frame(self):
        """Pobiera pojedynczą klatkę z kamery"""
        if not self.camera or not self.is_running:
            return None
        
        success, frame = self.camera.read()
        if not success:
            return None
        
        # Dodaj napis z nazwą kamery
        cv2.putText(frame, f"{self.name.upper()}", (10, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        # Dodaj timestamp
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        cv2.putText(frame, timestamp, (10, frame.shape[0] - 10), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        return frame
    
    def release(self):
        """Zwalnia zasoby kamery"""
        if self.camera:
            self.camera.release()
            self.is_running = False
            print(f"[OK] Kamera {self.name} zwolniona")


def generate_frames(camera_type):
    """
    Generator ramek dla Flask Response
    camera_type: 'thermal' lub 'digital'
    """
    camera_stream = cameras.get(camera_type)
    
    if not camera_stream or not camera_stream.is_running:
        # Zwróć pustą ramkę jeśli kamera nie działa
        blank_frame = create_blank_frame(f"Kamera {camera_type} niedostępna")
        _, buffer = cv2.imencode('.jpg', blank_frame)
        frame_bytes = buffer.tobytes()
        while True:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            time.sleep(0.1)
        return
    
    while True:
        with camera_locks[camera_type]:
            frame = camera_stream.get_frame()
        
        if frame is None:
            # Jeśli nie udało się pobrać ramki, wyślij pustą
            blank_frame = create_blank_frame(f"Brak obrazu z kamery {camera_type}")
            _, buffer = cv2.imencode('.jpg', blank_frame)
        else:
            # Kompresja do JPEG
            _, buffer = cv2.imencode('.jpg', frame, 
                                    [cv2.IMWRITE_JPEG_QUALITY, 85])
        
        frame_bytes = buffer.tobytes()
        
        # Zwróć ramkę w formacie MJPEG
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        
        # Małe opóźnienie aby nie przeciążać CPU
        time.sleep(0.03)  # ~30 FPS


def create_blank_frame(text):
    """Tworzy pustą czarną ramkę z tekstem"""
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    cv2.putText(frame, text, (50, 240), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    return frame


# Import numpy dla blank frame
import numpy as np


# ============= ROUTING =============

@app.route('/')
@auth.login_required
def index():
    """Strona główna z interfejsem - wymaga logowania"""
    return render_template('index.html')


@app.route('/video_feed/<camera_type>')
@auth.login_required
def video_feed(camera_type):
    """
    Endpoint streamujący wideo - wymaga logowania
    camera_type: 'thermal' lub 'digital'
    """
    if camera_type not in ['thermal', 'digital']:
        return "Invalid camera type", 400
    
    return Response(generate_frames(camera_type),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/rotate/<camera_type>/<direction>')
@auth.login_required
def rotate(camera_type, direction):
    """
    Obrót kamery - wymaga logowania
    camera_type: 'thermal' lub 'digital'
    direction: 'left', 'right', 'up', 'down'
    """
    if camera_type not in ['thermal', 'digital']:
        return jsonify({'error': 'Invalid camera type'}), 400
    
    if direction not in ['left', 'right', 'up', 'down']:
        return jsonify({'error': 'Invalid direction'}), 400
    
    # Pobierz aktualną pozycję
    current_pos = camera_positions[camera_type]
    
    # Oblicz nową pozycję (krok 10 stopni)
    step = 10
    if direction == 'left':
        new_pos = max(0, current_pos - step)
    elif direction == 'right':
        new_pos = min(180, current_pos + step)
    elif direction == 'up':
        new_pos = max(0, current_pos - step)
    elif direction == 'down':
        new_pos = min(180, current_pos + step)
    
    # Zapisz nową pozycję
    camera_positions[camera_type] = new_pos
    
    # TODO: Tutaj dodaj kod do sterowania serwami/silnikami
    # Przykład: sterowanie przez GPIO na Raspberry Pi
    # set_servo_angle(camera_type, new_pos)
    
    print(f"[ROTATE] {camera_type} -> {direction} (pozycja: {new_pos}°)")
    
    return jsonify({
        'status': 'ok',
        'camera': camera_type,
        'direction': direction,
        'position': new_pos
    })


@app.route('/center/<camera_type>')
@auth.login_required
def center_camera(camera_type):
    """Wycentruj kamerę (pozycja 90°) - wymaga logowania"""
    if camera_type not in ['thermal', 'digital']:
        return jsonify({'error': 'Invalid camera type'}), 400
    
    camera_positions[camera_type] = 90
    
    # TODO: Sterowanie serwem
    # set_servo_angle(camera_type, 90)
    
    print(f"[CENTER] {camera_type} wycentrowana")
    
    return jsonify({
        'status': 'ok',
        'camera': camera_type,
        'position': 90
    })


@app.route('/status')
@auth.login_required
def status():
    """Status systemu - wymaga logowania"""
    return jsonify({
        'cameras': {
            'thermal': {
                'active': cameras['thermal'].is_running if cameras['thermal'] else False,
                'position': camera_positions['thermal']
            },
            'digital': {
                'active': cameras['digital'].is_running if cameras['digital'] else False,
                'position': camera_positions['digital']
            }
        }
    })


# ============= INICJALIZACJA =============

def initialize_cameras():
    """Inicjalizuje wszystkie kamery przy starcie"""
    print("\n=== Inicjalizacja Systemu Kamer ===\n")
    
    # Inicjalizacja kamery termowizyjnej
    cameras['thermal'] = CameraStream(CAMERA_THERMAL_ID, 'Thermal')
    cameras['thermal'].initialize()
    
    # Inicjalizacja kamery cyfrowej
    cameras['digital'] = CameraStream(CAMERA_DIGITAL_ID, 'Digital')
    cameras['digital'].initialize()
    
    print("\n=== Inicjalizacja zakończona ===\n")


def cleanup():
    """Sprzątanie przy zamykaniu aplikacji"""
    print("\n=== Zamykanie systemu ===\n")
    for camera in cameras.values():
        if camera:
            camera.release()
    cv2.destroyAllWindows()


# ============= MAIN =============

if __name__ == '__main__':
    try:
        # Inicjalizuj kamery
        initialize_cameras()
        
        # Uruchom serwer Flask
        print("\n🚀 Serwer uruchomiony!")
        print("📷 Otwórz przeglądarkę i wejdź na:")
        print("   http://localhost:5000")
        print("   lub")
        print("   http://192.168.1.X:5000 (z innego urządzenia)\n")
        
        app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Przerwano przez użytkownika (Ctrl+C)")
    finally:
        cleanup()

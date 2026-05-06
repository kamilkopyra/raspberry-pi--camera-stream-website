#!/usr/bin/env python3
"""
System 2 kamer: CSI (Picamera2) + USB Grabber (OpenCV)
Sterowanie serwami SCServo - UŻYWA BIBLIOTEKI I LOGIKI ANTONIEGO
"""

from flask import Flask, Response, render_template, jsonify
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
from picamera2 import Picamera2
from picamera2.encoders import JpegEncoder
from picamera2.outputs import FileOutput
import cv2
import io
import threading
import time
import sys
import numpy as np

# Import BIBLIOTEKI ANTONIEGO
sys.path.insert(0, './SCServo_raspbi/SCServo_Python')
try:
    import SCServo_Linux as SCServo
    SCSERVO_AVAILABLE = True
    print("[OK] SCServo_Linux imported")
except ImportError as e:
    SCSERVO_AVAILABLE = False
    print(f"[WARNING] SCServo_Linux not available: {e}")

app = Flask(__name__)
auth = HTTPBasicAuth()

# ============= KONFIGURACJA (Z KODU C++ ANTONIEGO) =============

users = {
    "admin": generate_password_hash("admin123"),
}

@auth.verify_password
def verify_password(username, password):
    if username in users and check_password_hash(users.get(username), password):
        return username
    return None

# Kamera grabber (termowizyjna)
GRABBER_CAMERA_ID = 1  # <-- SPRAWDŹ v4l2-ctl --list-devices

# Konfiguracja ID serw (Z KODU C++ ANTONIEGO)
ID_X = 2  # Servo X (poziom)
ID_Y = 1  # Servo Y (pion)

# Krok obrotu w stopniach (Z KODU C++ ANTONIEGO)
KROK = 1.0

# Aktualne pozycje w stopniach - zaczynamy od środka (Z KODU C++)
posX = 0.0
posY = 0.0

# Limity (Z KODU C++ - w funkcji aktualizujSerwa są sprawdzane)
# W pętli głównej C++:
# if (posX < -90) posX = -90;
# if (posX > 90)  posX = 90;
# if (posY < -72) posY = -72;
# if (posY > 30)  posY = 30;

# Handler serw
sms_sts = None

# ============= FUNKCJA deg2sig (Z KODU C++ ANTONIEGO) =============

def deg2sig(stopnie, servo_id):
    """
    Konwersja stopni na sygnał serwa
    DOKŁADNA KOPIA z kodu C++ Antoniego
    """
    if servo_id == 1:
        return int(round(540 + (stopnie * (1023.0 / 300.0))))
    elif servo_id == 2:
        return int(round(475 + (stopnie * (1023.0 / 300.0))))
    return 512

# ============= FUNKCJA aktualizujSerwa (Z KODU C++ ANTONIEGO) =============

def aktualizujSerwa():
    """
    Aktualizacja pozycji serw
    DOKŁADNA KOPIA logiki z C++ Antoniego
    """
    if sms_sts:
        try:
            sms_sts.WritePos(ID_X, deg2sig(posX, ID_X), 0, 1500)
            sms_sts.WritePos(ID_Y, deg2sig(posY, ID_Y), 0, 1500)
            print(f"Pozycja -> X: {posX:.1f} | Y: {posY:.1f}")
        except Exception as e:
            print(f"[ERROR] Servo update failed: {e}")
    else:
        print(f"[SIMULATION] X: {posX:.1f} | Y: {posY:.1f}")

# ============= INICJALIZACJA KAMER =============

# Kamera CSI (cyfrowa)
print("[INIT] Inicjalizacja kamery CSI...")
picam = Picamera2()
config = picam.create_video_configuration(main={"size": (640, 480)})
picam.configure(config)

class StreamingOutput(io.BufferedIOBase):
    def __init__(self):
        self.frame = None
        self.condition = threading.Condition()

    def write(self, buf):
        with self.condition:
            self.frame = buf
            self.condition.notify_all()

output_csi = StreamingOutput()
picam.start_recording(JpegEncoder(), FileOutput(output_csi))
print("[OK] Kamera CSI gotowa")

# Kamera USB (termowizyjna - przez grabber)
print(f"[INIT] Inicjalizacja kamery USB (grabber ID: {GRABBER_CAMERA_ID})...")
cap_usb = cv2.VideoCapture(GRABBER_CAMERA_ID)
if cap_usb.isOpened():
    cap_usb.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap_usb.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    print("[OK] Kamera USB gotowa")
else:
    print("[WARNING] Kamera USB niedostepna")

# Inicjalizacja serw (UŻYWA BIBLIOTEKI ANTONIEGO)
if SCSERVO_AVAILABLE:
    try:
        # DOKŁADNIE JAK W JEGO PRZYKŁADACH
        sms_sts = SCServo.sms_sts("/dev/ttyAMA0", 115200)
        if sms_sts:
            print("[OK] SCServo port otwarty (115200 baud)")
            # Ustawienie początkowe (środek)
            aktualizujSerwa()
            time.sleep(0.5)
        else:
            print("[ERROR] Nie udalo sie otworzyc portu /dev/ttyAMA0")
    except Exception as e:
        print(f"[ERROR] SCServo init failed: {e}")
        sms_sts = None

# ============= GENERATORY STRUMIENI =============

def generate_csi():
    """Generator ramek z kamery CSI"""
    while True:
        with output_csi.condition:
            output_csi.condition.wait()
            frame = output_csi.frame
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

def generate_usb():
    """Generator ramek z kamery USB (grabber)"""
    while True:
        ret, frame = cap_usb.read()
        if not ret:
            frame = np.zeros((480, 640, 3), dtype=np.uint8)
            cv2.putText(frame, "Kamera niedostepna", (150, 240),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
        time.sleep(0.03)

# ============= ROUTING =============

@app.route('/')
@auth.login_required
def index():
    return render_template('index_basic.html')

@app.route('/video_feed/digital')
@auth.login_required
def video_feed_digital():
    return Response(generate_csi(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/video_feed/thermal')
@auth.login_required
def video_feed_thermal():
    return Response(generate_usb(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/rotate/<direction>')
@auth.login_required
def rotate(direction):
    """
    Sterowanie serwami - LOGIKA Z KODU C++ ANTONIEGO
    case 'w': posY += KROK; break;
    case 's': posY -= KROK; break;
    case 'a': posX -= KROK; break;
    case 'd': posX += KROK; break;
    """
    global posX, posY
    
    if direction == 'left':     # A
        posX -= KROK
    elif direction == 'right':  # D
        posX += KROK
    elif direction == 'up':     # W
        posY += KROK
    elif direction == 'down':   # S
        posY -= KROK
    else:
        return jsonify({'error': 'Invalid direction'}), 400
    
    # Nałóż ograniczenia (Z KODU C++)
    if posX < -90:
        posX = -90
    if posX > 90:
        posX = 90
    if posY < -72:
        posY = -72
    if posY > 30:
        posY = 30
    
    # Aktualizuj serwa
    aktualizujSerwa()
    
    return jsonify({
        'status': 'ok',
        'direction': direction,
        'position': {'x': posX, 'y': posY}
    })

@app.route('/center')
@auth.login_required
def center():
    """
    Wyśrodkuj serwa - LOGIKA Z KODU C++
    case ' ': posX = 0; posY = 0; break;
    """
    global posX, posY
    
    posX = 0.0
    posY = 0.0
    aktualizujSerwa()
    
    return jsonify({
        'status': 'ok',
        'position': {'x': posX, 'y': posY}
    })

# ============= MAIN =============

if __name__ == '__main__':
    try:
        print("\n" + "="*50)
        print("System kamer uruchomiony")
        print("URL: http://172.20.10.11:5000")
        print("Login: admin | Haslo: admin123")
        print("="*50 + "\n")
        
        app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
        
    except KeyboardInterrupt:
        print("\n\nZatrzymano")
    finally:
        picam.stop_recording()
        picam.close()
        cap_usb.release()
        if sms_sts:
            sms_sts.end()

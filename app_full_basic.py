#!/usr/bin/env python3
"""
System 2 kamer: CSI (Picamera2) + USB Grabber (OpenCV)

"""

from flask import Flask, Response, render_template, jsonify
from picamera2 import Picamera2
from picamera2.encoders import JpegEncoder
from picamera2.outputs import FileOutput
import cv2
import io
import threading
import time
import numpy as np
from flask import request
import subprocess


app = Flask(__name__)

@app.route('/move') # Usunęliśmy <key> z adresu
def move():
    # Pobieramy wartość 'key' z parametrów URL (?key=w)
    key = request.args.get('key')
    
    if key:
        print(f"Otrzymano klawisz: {key}")
        # Wywołujemy binarkę C++
        subprocess.run(["sudo", "./servo_exec", key])
        return "OK", 200
    
    return "Brak klawisza", 400


# Kamera grabber (termowizyjna)
GRABBER_CAMERA_ID = 0  # <-- SPRAWDŹ v4l2-ctl --list-devices


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

def index():
    return render_template('index_basic.html')

@app.route('/video_feed/digital')

def video_feed_digital():
    return Response(generate_csi(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/video_feed/thermal')

def video_feed_thermal():
    return Response(generate_usb(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


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

#!/usr/bin/env python3
"""
System kamery CSI z Picamera2 + Flask + logowaniem
"""

from flask import Flask, Response, render_template, jsonify
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
from picamera2 import Picamera2
from picamera2.encoders import JpegEncoder
from picamera2.outputs import FileOutput
import io
import threading
import time

app = Flask(__name__)
auth = HTTPBasicAuth()

# LOGOWANIE - ZMIEŃ HASŁO!
users = {
    "admin": generate_password_hash("admin123"),
}

@auth.verify_password
def verify_password(username, password):
    if username in users and check_password_hash(users.get(username), password):
        return username
    return None

# Inicjalizacja kamery CSI
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

output = StreamingOutput()
picam.start_recording(JpegEncoder(), FileOutput(output))

def generate_frames():
    """Generator ramek MJPEG"""
    while True:
        with output.condition:
            output.condition.wait()
            frame = output.frame
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
@auth.login_required
def index():
    return render_template('index_simple.html')

@app.route('/video_feed')
@auth.login_required
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    try:
        print("\n🚀 Serwer uruchomiony!")
        print("📷 http://172.20.10.11:5000")
        print("Login: admin | Hasło: admin123\n")
        
        app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
    except KeyboardInterrupt:
        print("\n\n⚠️ Zatrzymano")
    finally:
        picam.stop_recording()
        picam.close()

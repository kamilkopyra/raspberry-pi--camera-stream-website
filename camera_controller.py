#!/usr/bin/env python3
"""
Moduł sterowania serwami/silnikami do obracania kamer
Używa GPIO na Raspberry Pi (pigpio lub RPi.GPIO)
"""

import time

# Flaga - czy jesteś na Raspberry Pi
try:
    import RPi.GPIO as GPIO
    IS_RASPBERRY_PI = True
    print("[OK] Wykryto Raspberry Pi - GPIO dostępne")
except ImportError:
    IS_RASPBERRY_PI = False
    print("[INFO] Nie wykryto Raspberry Pi - używam trybu symulacji")


class ServoController:
    """
    Kontroler serwomechanizmów do obracania kamer
    """
    
    def __init__(self, pin_horizontal, pin_vertical=None):
        """
        Args:
            pin_horizontal: Pin GPIO dla ruchu poziomego (lewo/prawo)
            pin_vertical: Pin GPIO dla ruchu pionowego (góra/dół) - opcjonalnie
        """
        self.pin_horizontal = pin_horizontal
        self.pin_vertical = pin_vertical
        self.current_angle_h = 90  # Pozycja startowa (środek)
        self.current_angle_v = 90  # Pozycja startowa (środek)
        
        if IS_RASPBERRY_PI:
            self._setup_gpio()
        else:
            print(f"[SYMULACJA] Servo na pinach: H={pin_horizontal}, V={pin_vertical}")
    
    def _setup_gpio(self):
        """Konfiguracja GPIO dla serwomechanizmów"""
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin_horizontal, GPIO.OUT)
        
        # PWM dla serwa (częstotliwość 50Hz - standard dla serwomechanizmów)
        self.pwm_h = GPIO.PWM(self.pin_horizontal, 50)
        self.pwm_h.start(0)
        
        if self.pin_vertical:
            GPIO.setup(self.pin_vertical, GPIO.OUT)
            self.pwm_v = GPIO.PWM(self.pin_vertical, 50)
            self.pwm_v.start(0)
        
        print(f"[OK] GPIO skonfigurowane dla serw")
    
    def _angle_to_duty_cycle(self, angle):
        """
        Konwersja kąta (0-180°) na duty cycle dla PWM
        
        Większość serwomechanizmów:
        - 0° = 2.5% duty cycle
        - 90° = 7.5% duty cycle  
        - 180° = 12.5% duty cycle
        """
        # Mapowanie 0-180° na 2.5-12.5%
        duty = 2.5 + (angle / 180.0) * 10.0
        return duty
    
    def set_horizontal_angle(self, angle):
        """
        Ustaw kąt poziomy (lewo/prawo)
        
        Args:
            angle: Kąt w stopniach (0-180, gdzie 90 = środek)
        """
        # Ogranicz zakres
        angle = max(0, min(180, angle))
        
        if IS_RASPBERRY_PI:
            duty = self._angle_to_duty_cycle(angle)
            self.pwm_h.ChangeDutyCycle(duty)
            time.sleep(0.3)  # Poczekaj na ustawienie
            self.pwm_h.ChangeDutyCycle(0)  # Wyłącz PWM aby servo nie wibrował
        else:
            print(f"[SYMULACJA] Obrót poziomy: {angle}°")
        
        self.current_angle_h = angle
        return angle
    
    def set_vertical_angle(self, angle):
        """
        Ustaw kąt pionowy (góra/dół)
        
        Args:
            angle: Kąt w stopniach (0-180, gdzie 90 = środek)
        """
        if not self.pin_vertical:
            print("[WARNING] Brak pinu dla ruchu pionowego")
            return self.current_angle_v
        
        # Ogranicz zakres
        angle = max(0, min(180, angle))
        
        if IS_RASPBERRY_PI:
            duty = self._angle_to_duty_cycle(angle)
            self.pwm_v.ChangeDutyCycle(duty)
            time.sleep(0.3)
            self.pwm_v.ChangeDutyCycle(0)
        else:
            print(f"[SYMULACJA] Obrót pionowy: {angle}°")
        
        self.current_angle_v = angle
        return angle
    
    def move(self, direction, step=10):
        """
        Przesuń serwomechanizm w określonym kierunku
        
        Args:
            direction: 'left', 'right', 'up', 'down'
            step: Wielkość kroku w stopniach (domyślnie 10)
        """
        if direction == 'left':
            new_angle = max(0, self.current_angle_h - step)
            return self.set_horizontal_angle(new_angle)
        
        elif direction == 'right':
            new_angle = min(180, self.current_angle_h + step)
            return self.set_horizontal_angle(new_angle)
        
        elif direction == 'up':
            new_angle = max(0, self.current_angle_v - step)
            return self.set_vertical_angle(new_angle)
        
        elif direction == 'down':
            new_angle = min(180, self.current_angle_v + step)
            return self.set_vertical_angle(new_angle)
        
        else:
            print(f"[ERROR] Nieznany kierunek: {direction}")
            return None
    
    def center(self):
        """Wycentruj oba serwa (90°)"""
        self.set_horizontal_angle(90)
        if self.pin_vertical:
            self.set_vertical_angle(90)
        print("[OK] Serwomechanizmy wycentrowane")
    
    def cleanup(self):
        """Sprzątanie GPIO"""
        if IS_RASPBERRY_PI:
            self.pwm_h.stop()
            if hasattr(self, 'pwm_v'):
                self.pwm_v.stop()
            GPIO.cleanup()
            print("[OK] GPIO wyczyszczone")


# ============= PRZYKŁAD UŻYCIA =============

if __name__ == '__main__':
    print("\n=== Test Serwomechanizmów ===\n")
    
    # Przykładowe piny GPIO (BCM)
    # Dostosuj do swojego podłączenia!
    SERVO_THERMAL_H = 17   # GPIO 17 dla kamery termowizyjnej (poziom)
    SERVO_THERMAL_V = 27   # GPIO 27 dla kamery termowizyjnej (pion)
    SERVO_DIGITAL_H = 22   # GPIO 22 dla kamery cyfrowej (poziom)
    SERVO_DIGITAL_V = 23   # GPIO 23 dla kamery cyfrowej (pion)
    
    try:
        # Stwórz kontrolery
        thermal_servo = ServoController(SERVO_THERMAL_H, SERVO_THERMAL_V)
        digital_servo = ServoController(SERVO_DIGITAL_H, SERVO_DIGITAL_V)
        
        print("\nTest 1: Centrowanie...")
        thermal_servo.center()
        digital_servo.center()
        time.sleep(1)
        
        print("\nTest 2: Obrót w lewo...")
        thermal_servo.move('left', step=30)
        time.sleep(1)
        
        print("\nTest 3: Obrót w prawo...")
        thermal_servo.move('right', step=30)
        time.sleep(1)
        
        print("\nTest 4: Powrót do centrum...")
        thermal_servo.center()
        digital_servo.center()
        
        print("\n✅ Test zakończony")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Przerwano")
    
    finally:
        if IS_RASPBERRY_PI:
            thermal_servo.cleanup()
            digital_servo.cleanup()


# ============= KONFIGURACJA DLA FLASK APP =============

# Piny GPIO dla kamer (dostosuj do swojego układu!)
CAMERA_SERVOS = {
    'thermal': {
        'horizontal': 17,  # GPIO 17
        'vertical': 27     # GPIO 27
    },
    'digital': {
        'horizontal': 22,  # GPIO 22
        'vertical': 23     # GPIO 23
    }
}

def get_servo_controller(camera_type):
    """
    Zwraca kontroler serwa dla danej kamery
    
    Args:
        camera_type: 'thermal' lub 'digital'
    
    Returns:
        ServoController instance
    """
    if camera_type not in CAMERA_SERVOS:
        raise ValueError(f"Nieznany typ kamery: {camera_type}")
    
    pins = CAMERA_SERVOS[camera_type]
    return ServoController(
        pin_horizontal=pins['horizontal'],
        pin_vertical=pins.get('vertical')
    )

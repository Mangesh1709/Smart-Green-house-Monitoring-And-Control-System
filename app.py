import cv2
import RPi.GPIO as GPIO
import time
import Adafruit_DHT
from flask import Flask, render_template, Response, request

app = Flask(__name__)

# Set up GPIO pins
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Define pin numbers
dht_pin = 4
ldr_pin = 18
soil_pin = 17
led_pin = 21
fan_pin = 20
pump_pin = 16

# Set up DHT11 pin as input and LED, fan, and pump pins as output
GPIO.setup(dht_pin, GPIO.IN)
GPIO.setup(ldr_pin, GPIO.IN)
GPIO.setup(soil_pin, GPIO.IN)
GPIO.setup(led_pin, GPIO.OUT)
GPIO.setup(fan_pin, GPIO.OUT)
GPIO.setup(pump_pin, GPIO.OUT)

# Define a function to read data from the DHT11 sensor
def read_dht():
    humidity, temperature = Adafruit_DHT.read_retry(Adafruit_DHT.DHT11, dht_pin)
    return humidity, temperature

# Define a function to read data from the soil moisture sensor
def read_soil():
    soil_value = GPIO.input(soil_pin)
    return soil_value

# Define a function to read data from the LDR sensor
def read_ldr():
    ldr_value = GPIO.input(ldr_pin)
    return ldr_value

# Define a function to control the LED light
def control_led(state):
    GPIO.output(led_pin, state)

# Define a function to control the exhaust fan
def control_fan(state):
    GPIO.output(fan_pin, state)

# Define a function to control the motor pump
def control_pump(state):
    GPIO.output(pump_pin, state)

# Define a function to capture the video stream from the webcam
def capture_video():
    cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        # Encode the frame as JPEG
        ret, jpeg = cv2.imencode('.jpg', frame)
        # Convert the JPEG image to bytes
        image_bytes = jpeg.tobytes()
        # Yield the bytes as a response
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + image_bytes + b'\r\n')
    cap.release()

# Define a route to display the sensor values and provide buttons to control the actuators
@app.route('/')
def index():
    humidity, temperature = read_dht()
    soil_value = read_soil()
    ldr_value = read_ldr()

    # Control LED based on LDR sensor data
    if ldr_value < 500:  # Adjust the threshold value as per your requirement
        control_led(GPIO.HIGH)  # Turn on the LED
    else:
        control_led(GPIO.LOW)  # Turn off the LED

    # Control fan based on DHT11 sensor data
    if temperature > 30:  # Adjust the threshold value as per your requirement
        control_fan(GPIO.HIGH)  # Turn on the fan
    else:
        control_fan(GPIO.LOW)  # Turn off the fan

    # Control pump based on soil moisture sensor data
    if soil_value < 300:  # Adjust the threshold value as per your requirement
        control_pump(GPIO.HIGH)  # Turn on the pump
    else:
        control_pump(GPIO.LOW)  # Turn off the pump

    template_data = {
        'humidity': humidity,
        'temperature': temperature,
        'soil_value': soil_value,
'ldr_value': ldr_value,
}
return render_template('index.html', **template_data)
@app.route('/video_feed')
def video_feed():
    return Response(capture_video(),
mimetype='multipart/x-mixed-replace; boundary=frame')
@app.route('/led/<state>')
def led(state):
        if state == 'on':
            control_led(GPIO.HIGH)
        else:
            control_led(GPIO.LOW)
    return state
@app.route('/fan/<state>')
def fan(state):
        if state == 'on':
            control_fan(GPIO.HIGH)
        else:
            control_fan(GPIO.LOW)
    return state
@app.route('/pump/<state>')
def pump(state):
        if state == 'on':
            control_pump(GPIO.HIGH)
        else:
            control_pump(GPIO.LOW)
    return state
if name == 'main':
    app.run(debug=True, host='0.0.0.0')
       

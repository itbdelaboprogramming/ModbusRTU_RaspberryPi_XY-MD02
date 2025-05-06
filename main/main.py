import threading
from time import sleep, time
from datetime import datetime
import tkinter as tk
import mysql.connector
from paho.mqtt import client as mqttclient
import random
import signal
import sys

# -----------------------
# Sensor Setup (Assuming your sensor API)
# -----------------------
from lib.XYMD02 import serial_driver

# Initialize sensor
sensor1 = serial_driver.XYMD02(
    address=1,
    port='/dev/serial0',
    baudrate=9600
)

def get_data_sensor(sensor):
    """
    Reads sensor parameters and measurement data.
    Adjust according to your API's functions.
    """
    # Assuming sensor.get_data() returns a tuple: (temperature, humidity)
    # and sensor.get_parameter() returns (device_address, baudrate, temperature_correction, humidity_correction)
    [device_address, baudrate, temperature_correction, humidity_correction] = sensor.get_parameter()
    # Minor sleep to ensure data consistency; adjust as needed.
    sleep(0.001)
    [temperature, humidity] = sensor.get_data()
    data = {
        'device_address': device_address,
        'baudrate': baudrate,
        'temperature_correction': temperature_correction,
        'humidity_correction': humidity_correction,
        'temperature': temperature,
        'humidity': humidity
    }
    return data

# -----------------------
# MQTT Setup
# -----------------------
broker = input("Enter your broker IP: ")
port = 1883
topic = "raspberry/data_sensor"
client_id = f'publish-{random.randint(0, 1000)}'

mqtt_client = mqttclient.Client(mqttclient.CallbackAPIVersion.VERSION2)

def connect_mqtt():
    def on_connect(client, userdata, flags, rc, properties):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n" % rc)
    mqtt_client.on_connect = on_connect
    mqtt_client.connect(broker, port)
    mqtt_client.loop_start()

def publish_mqtt(data):
    msg = str(data)
    result = mqtt_client.publish(topic, msg)
    status = result[0]
    if status == 0:
        print(f"Published {msg} to topic {topic}")
    else:
        print(f"Failed to send message to topic {topic}")

# -----------------------
# MySQL Database Setup
# -----------------------
host = 'localhost'
user = 'root'
password = 'Plmokn098'
database = 'sensordb'

def init_db():
    # Create database if not exists.
    db = mysql.connector.connect(host=host, user=user, password=password)
    cur = db.cursor()
    cur.execute('CREATE DATABASE IF NOT EXISTS sensordb;')
    db.close()
    
    db = mysql.connector.connect(host=host, user=user, password=password, database=database)
    cur = db.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS sensor (
            id INT AUTO_INCREMENT PRIMARY KEY,
            device_name VARCHAR(20),
            device_address INT,
            baudrate INT,
            temperature_correction FLOAT,
            humidity_correction FLOAT
        );
    ''')
    cur.execute('''
        CREATE TABLE IF NOT EXISTS sensor_data (
            id INT AUTO_INCREMENT PRIMARY KEY,
            sensor_id INT,
            timestamp TIMESTAMP,
            temperature FLOAT,
            humidity FLOAT,
            FOREIGN KEY (sensor_id) REFERENCES sensor(id)
        );
    ''')
    db.commit()
    db.close()

def store_parameter(sensor, device_name):
    db = mysql.connector.connect(host=host, user=user, password=password, database=database)
    cur = db.cursor()
    params = sensor.get_parameter()  # Expecting (device_address, baudrate, temperature_correction, humidity_correction)
    sql = '''
        INSERT INTO sensor(device_name, device_address, baudrate, temperature_correction, humidity_correction)
        SELECT %s, %s, %s, %s, %s FROM DUAL
        WHERE NOT EXISTS (SELECT 1 FROM sensor WHERE device_name = %s)
    '''
    cur.execute(sql, (device_name, params[0], params[1], params[2], params[3], device_name))
    db.commit()
    db.close()
    print(f"Parameters for {device_name} inserted")

def store_data(sensor, device_name):
    db = mysql.connector.connect(host=host, user=user, password=password, database=database)
    cur = db.cursor()
    
    # Get sensor id from sensor table
    cur.execute('SELECT id FROM sensor WHERE device_name = %s', (device_name,))
    result = cur.fetchone()
    if result is None:
        print(f"No sensor found with name {device_name}")
        db.close()
        return
    sensor_id = result[0]
    
    # Insert sensor data
    d = get_data_sensor(sensor)
    timestamp = datetime.now()
    cur.execute('INSERT INTO sensor_data(sensor_id, timestamp, temperature, humidity) VALUES (%s, %s, %s, %s)',
                (sensor_id, timestamp, d['temperature'], d['humidity']))
    db.commit()
    db.close()
    print("Sensor data stored at", timestamp.strftime("%Y-%m-%d %H:%M:%S"))

# -----------------------
# Tkinter GUI Setup (GUI must run in main thread)
# -----------------------
root = tk.Tk()
root.title("Sensor Monitor")

# Define StringVars for the dynamic labels
gui_text = {
    'timestamp': tk.StringVar(),
    'temperature': tk.StringVar(),
    'humidity': tk.StringVar(),
}

# Create a frame for our 2-column layout
frame = tk.Frame(root)
frame.pack(padx=20, pady=20)

# Define the left-side (static labels) and right-side (dynamic values)
labels_left = {
    'timestamp': 'Timestamp:',
    'temperature': 'Temperature:',
    'humidity': 'Humidity:'
}

# Arrange labels in a grid (two columns)
row_keys = list(labels_left.keys())
for i, key in enumerate(row_keys):
    # Static label on left column
    tk.Label(frame, text=labels_left[key], font=("Arial", 14), width=12, anchor='w').grid(row=i, column=0, sticky='w', pady=4)
    # Dynamic value label on right column
    tk.Label(frame, textvariable=gui_text[key], font=("Arial", 14), width=25, anchor='w').grid(row=i, column=1, sticky='w', pady=4)

def update_gui():
    """Update the GUI every second."""
    try:
        d = get_data_sensor(sensor1)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        gui_text['timestamp'].set(timestamp)
        gui_text['temperature'].set(f"{d['temperature']:.2f} °C")
        gui_text['humidity'].set(f"{d['humidity']:.2f} %")
    except Exception as e:
        gui_text['timestamp'].set("Error")
        gui_text['temperature'].set("Error")
        gui_text['humidity'].set("Error")
        print("GUI update error:", e)
    # Schedule the function to run again after 1000 ms (1 second)
    root.after(1000, update_gui)

# -----------------------
# Background thread for MQTT & DB (Every 5 seconds)
# -----------------------
def background_data_loop():
    while True:
        try:
            # Store data to database
            store_data(sensor1, 'sensor1')
            # Get fresh data and publish via MQTT
            d = get_data_sensor(sensor1)
            d['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            publish_mqtt(d)
        except Exception as e:
            print("Background data loop error:", e)
        sleep(5)

# -----------------------
# Signal Handler for Graceful Exit
# -----------------------
def handler(signum, frame):
    print("Ctrl-c was pressed. Exiting gracefully.")
    mqtt_client.loop_stop()
    sys.exit(0)

signal.signal(signal.SIGINT, handler)

# -----------------------
# Main Execution
# -----------------------
if __name__ == '__main__':
    # Initialize database and sensor parameters
    init_db()
    store_parameter(sensor1, 'sensor1')
    
    # Connect to MQTT
    connect_mqtt()
    
    # Start the GUI updater (runs in main thread with after())
    update_gui()
    
    # Start the background thread for MQTT/database operations (as daemon)
    bg_thread = threading.Thread(target=background_data_loop, daemon=True)
    bg_thread.start()
    
    # Run the Tkinter main loop
    root.mainloop()


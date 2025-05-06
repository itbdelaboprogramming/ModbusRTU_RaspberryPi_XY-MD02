from lib.XYMD02 import serial_driver
from paho.mqtt import client as mqttclient
from datetime import datetime
from time import sleep
import tkinter as tk
import mysql.connector
import threading
import os
import signal
import sys
import random
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from collections import deque

# Initialize sensor
sensor1 = serial_driver.XYMD02(
    address=1,
    port='/dev/serial0',
    baudrate=9600
)

data = {}

def get_data_sensor(sensor):
    [device_address, baudrate, temperature_correction, humidity_correction] = sensor.get_parameter()
    sleep(0.001)
    [temperature, humidity] = sensor.get_data()
    sleep(0.001)
            
    data = {
        'device_address': device_address,
        'baudrate': baudrate,
        'temperature_correction': temperature_correction,
        'humidity_correction': humidity_correction,
        'temperature': temperature,
        'humidity': humidity
    }
    return data

#MQTT
# mqtt properties
broker = input("Enter your broker IP: ")
port = 1883
topic = "raspberry/data_sensor"
# Generate a Client ID with the publish prefix.
client_id = f'publish-{random.randint(0, 1000)}'
# username = 'emqx'
# password = ''

mqtt_client = mqttclient.Client(mqttclient.CallbackAPIVersion.VERSION2)

def connect_mqtt():
	def on_connect(client, userdata, flags, rc, properties):
		if rc == 0:
			print("Connected to MQTT Broker!")
		else:
			print("Failed to connect, return code %d\n", rc)
	
	# mqtt_client.username_pw_set(username, password)
	mqtt_client.on_connect = on_connect
	mqtt_client.connect(broker, port)
    
def publish(client, msg):
	result = client.publish(topic, msg)
	status = result[0]
	if status == 0:
		print(f"Send `{msg}` to topic `{topic}`\n")
	else:
		print(f"Failed to send message to topic {topic}\n")


# -----------------------
# Tkinter GUI Setup (GUI must run in main thread)
# -----------------------
root = tk.Tk()
root.title("Sensor Data Display")

# Text creation
text = {
    'address': tk.StringVar(),
    'baudrate': tk.StringVar(),
    'timestamp': tk.StringVar(),
    'temperature': tk.StringVar(),
    'humidity': tk.StringVar(),
}

max_points = 30  # number of points to show on the graph
temp_data = deque([0.0]*max_points, maxlen=max_points)
humid_data = deque([0.0]*max_points, maxlen=max_points)
timestamps = deque([""]*max_points, maxlen=max_points)

# Initialize value
text['address'].set(f": {sensor1.get_address()}")
text['baudrate'].set(f": {sensor1.get_baudrate()}")

# Frame creation
frame = tk.Frame(root)
frame.pack(padx=20, pady=20)

# Create Matplotlib figure
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(5, 4), dpi=100)
fig.tight_layout(pad=3.0)
ax1.set_title("Temperature (\u00b0C)")
ax2.set_title("Humidity (%)")
ax1.set_ylim(0, 50)
ax2.set_ylim(0, 100)

# Embed in Tkinter
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack(padx=20, pady=10)

rows = ['address', 'baudrate', 'timestamp', 'temperature', 'humidity']
labels_left = {
    'address': 'Device ID',
    'baudrate': 'Baudrate',
    'timestamp': 'Timestamp',
    'temperature': 'Temperature',
    'humidity': 'Humidity'
}

for i, key in enumerate(rows):
    label_name = tk.Label(frame, text=labels_left[key], font=("Arial", 14), anchor="w", width=12)
    label_value = tk.Label(frame, textvariable=text[key], font=("Arial", 14), anchor="w", width=25)

    label_name.grid(row=i, column=0, sticky="w", pady=4)
    label_value.grid(row=i, column=1, sticky="w", pady=4)

#DATABASE
# initialize database
host = 'localhost'
user = 'root'
password = 'Plmokn098'
database = 'sensordb'

def init_db():
	sensordb = mysql.connector.connect(
		host=host,
		user=user,
		password=password,
	)

	cursor = sensordb.cursor()
	cursor.execute('CREATE DATABASE IF NOT EXISTS sensordb;')
	
	sensordb = mysql.connector.connect(
		host=host,
		user=user,
		password=password,
		database=database
	)
	
	cursor = sensordb.cursor()	
	cursor.execute('''		
		CREATE TABLE IF NOT EXISTS sensor(
			id INT AUTO_INCREMENT PRIMARY KEY,
			device_name VARCHAR(20),
			device_address INT,			
			baudrate INT,
			temperature_correction FLOAT,
			humidity_correction FLOAT
		);
	''')
	
	cursor.execute('''
		CREATE TABLE IF NOT EXISTS sensor_data(
			id INT AUTO_INCREMENT PRIMARY KEY,
			sensor_id INT,
			timestamp TIMESTAMP,
			temperature FLOAT,
			humidity FLOAT,
			FOREIGN KEY (sensor_id) REFERENCES sensor(id)
		);
	''')


def store_parameter(data, device_name):
    sensordb = mysql.connector.connect(host=host, user=user, password=password, database=database)
    cursor = sensordb.cursor()

    sql = ('''
        INSERT INTO sensor(device_name, device_address, baudrate, temperature_correction, humidity_correction)
        SELECT %s, %s, %s, %s, %s
        FROM DUAL
        WHERE NOT EXISTS(
            SELECT 1 FROM sensor WHERE device_name = %s 
        )
    ''')
    value = (device_name, data['device_address'], data['baudrate'], data['temperature_correction'], data['humidity_correction'], device_name)

    cursor.execute(sql, value)
    sensordb.commit()
    print(f"{device_name}'s parameter inserted")

def store_data(data, device_name):
    sensordb = mysql.connector.connect(host=host, user=user, password=password, database=database)
    cursor = sensordb.cursor()

    # Get device_id
    select_sql = 'SELECT id FROM sensor WHERE device_name = %s'
    cursor.execute(select_sql, (device_name,))
    result = cursor.fetchall()
    if result is None:
        print(f"No device found with name {device_name}")
        return
    sensor_id = result[0][0]

    insert_sql = ('''
        INSERT INTO sensor_data(sensor_id, timestamp, temperature, humidity)
        VALUES(%s, %s, %s, %s)
    ''')
    timestamp = datetime.now()
    value = (sensor_id, timestamp, data['temperature'], data['humidity'])

    cursor.execute(insert_sql, value)
    sensordb.commit()
    print("Data inserted")


# Update data sensor every second
def update_gui():
    try:
        global data
        timestamp = data['timestamp']
        temperature = data['temperature']
        humidity = data['humidity']
        temperature_correction = data['temperature_correction']
        humidity_correction = data['humidity_correction']

        text['timestamp'].set(f": {timestamp}")
        text['temperature'].set(f": {temperature:.2f} \u00B1 {temperature_correction:.2f} \u00b0C")
        text['humidity'].set(f": {humidity:.2f} \u00B1 {humidity_correction:.2f} %")
        
        # Append new data
        temp_data.append(temperature)
        humid_data.append(humidity)
        timestamps.append(datetime.now().strftime("%H:%M:%S"))

        # Clear and re-plot
        ax1.clear()
        ax2.clear()
        ax1.plot(list(timestamps), list(temp_data), color='red', label='Temperature')
        ax2.plot(list(timestamps), list(humid_data), color='blue', label='Humidity')
        ax1.set_ylim(20, 40)
        ax2.set_ylim(40, 90)
        ax1.set_title("Temperature (\u00b0C)")
        ax2.set_title("Humidity (%)")
        
        n = 10  # show every 5th label
        # For Temperature plot
        ax1.set_xticks(range(len(timestamps)))
        ax1.set_xticklabels([label if i % n == 0 else "" for i, label in enumerate(timestamps)], rotation=45)
        # For Humidity plot
        ax2.set_xticks(range(len(timestamps)))
        ax2.set_xticklabels([label if i % n == 0 else "" for i, label in enumerate(timestamps)], rotation=45)
        
        ax1.tick_params(axis='x', rotation=45)
        ax2.tick_params(axis='x', rotation=45)

        canvas.draw()

    except Exception as e:
        text['timestamp'].set(f": Error")
        text['temperature'].set(f": Error")
        text['humidity'].set(f": Error")
        print(f"Error reading sensor: {e}")

    # recall after 1000 ms
    root.after(1000, update_gui)

# -----------------------
# Background thread for MQTT & DB (Every 5 seconds)
# -----------------------
def mqtt_database_loop():
    while True:
        try:
            global data
            # Store data to database
            store_data(data, 'sensor1')
            # Get fresh data and publish via MQTT
            publish(mqtt_client, str(data))
        except Exception as e:
            print("Background data loop error:", e)
        sleep(5)
    
def get_data():
    global data
    data = get_data_sensor(sensor1)
    store_parameter(data, 'sensor1')

    while True:
        try:
            data = get_data_sensor(sensor1)
            data['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    
        except Exception as e:
            print("Background data loop error:", e)
        
        sleep(1)

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
        
    # Connect to MQTT
    connect_mqtt()
    
    # Start the GUI updater (runs in main thread with after())
    update_gui()
    
    # Start the background thread for data acquisition (as daemon)
    data_thread = threading.Thread(target=get_data, daemon=True)
    data_thread.start()
    
    # Start the background thread for MQTT/database operations (as daemon)
    bg_thread = threading.Thread(target=mqtt_database_loop, daemon=True)
    bg_thread.start()

    # Run the Tkinter main loop
    root.mainloop()




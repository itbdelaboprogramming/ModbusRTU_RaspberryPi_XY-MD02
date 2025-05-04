from lib.XYMD02 import serial_driver
from time import sleep
from datetime import datetime
import mysql.connector
from paho.mqtt import client as mqttclient
import os
import signal
import sys
import random

# inititalize sensor
sensor1 = serial_driver.XYMD02(
	address=1, 
	port='/dev/serial0', 
	baudrate=9600
)

# intitialize data sensor
data_sensor = {}

# mqtt properties
broker = '192.168.1.100'
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

# get parameter and data from sensor
def get_data_sensor(sensor):
	[device_address, baudrate, temperature_correction, humidity_correction] = sensor.get_parameter()
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
	
def store_parameter(sensor, device_name):
	sensordb = mysql.connector.connect(
		host=host,
		user=user,
		password=password,
		database=database
	)
	cursor = sensordb.cursor()	

	sql = ('''
		INSERT INTO sensor(device_name, device_address, baudrate, temperature_correction, humidity_correction)
		SELECT %s, %s, %s, %s, %s
		FROM DUAL
		WHERE NOT EXISTS(
			SELECT 1 FROM sensor WHERE device_name = %s 
		)
	''')
	data = get_data_sensor(sensor1)
	value = (device_name, data['device_address'], data['baudrate'], data['temperature_correction'], data['humidity_correction'], device_name)
	
	cursor.execute(sql, value)
	sensordb.commit()
	print(f"{device_name}'s parameter inserted")
	
def store_data(sensor, device_name):
	sensordb = mysql.connector.connect(
		host=host,
		user=user,
		password=password,
		database=database
	)
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
	data = get_data_sensor(sensor1)
	value = (sensor_id, timestamp, data['temperature'], data['humidity'])
	
	cursor.execute(insert_sql, value)
	sensordb.commit()
	print("Data inserted")

def handler(signum, frame):
	print("Ctrl-c was pressed.")
	mqtt_client.loop_stop()
	exit(1)
	
# main
if __name__ == '__main__':
	init_db()
	
	# setup mqtt client
	connect_mqtt()
	mqtt_client.loop_start()

	# handle signal interrupt
	signal.signal(signal.SIGINT, handler)

	store_parameter(sensor1, 'sensor1')
	
	while True:
		store_data(sensor1, 'sensor1')
		data = get_data_sensor(sensor1)
		data['timestamp'] = datetime.now()
		data_msg = str(data)
		publish(mqtt_client, data_msg)
		sleep(5)
	
	sys.exit(main(sys.argv))

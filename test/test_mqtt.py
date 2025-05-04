from lib.XYMD02 import serial_driver
from datetime import datetime
from time import sleep
from datetime import datetime
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

def handler(signum, frame):
	print("Ctrl-c was pressed.")
	mqtt_client.loop_stop()
	exit(1)

# main
if __name__ == '__main__':
	# setup mqtt client
	connect_mqtt()
	mqtt_client.loop_start()
	
	# handle signal interrupt
	signal.signal(signal.SIGINT, handler)
	
	while True:
		data = get_data_sensor(sensor1)
		data['timestamp'] = datetime.now()
		data_msg = str(data)
		publish(mqtt_client, data_msg)
		
		sleep(5)

	sys.exit(main(sys.argv))

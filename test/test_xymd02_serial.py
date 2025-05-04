from lib.XYMD02 import serial_driver
from time import sleep

sensor1 = serial_driver.XYMD02(
	address=1, 
	port='/dev/serial0', 
	baudrate=9600
)

if __name__ == '__main__':
	address = sensor1.get_address()
	baudrate = sensor1.get_baudrate()
	
	print(f"Address: {address}\tBaudrate: {baudrate}\n")
	
	iter = 0
	while True:
		if iter % 2 == 0:
			print("Using print function of class")
			sensor1.print_temperature()
			sensor1.print_humidity()
			
		if iter % 2 == 1:
			print("Get data then print manually")
			temperature = sensor1.get_temperature()
			sleep(0.01)
			humidity = sensor1.get_humidity()
			sleep(0.01)
			temperature_correction = sensor1.get_temperature_correction()
			humidity_correction = sensor1.get_humidity_correction()
			
			print(f"Temperature: {temperature} \u00B1 {temperature_correction} \u00b0C")
			print(f"Humidity: {humidity} \u00B1 {humidity_correction} %")

		print()
		sleep(1)
		iter += 1

from lib.XYMD02 import pymodbus_driver, minimalmodbus_driver, serial_driver
from time import sleep, perf_counter

# pymodbus
sensor1 = pymodbus_driver.XYMD02(
	address=1, 
	port='/dev/serial0', 
	baudrate=9600,
)

# minimalmodbus
sensor2 = minimalmodbus_driver.XYMD02(
	address=1, 
	port='/dev/serial0', 
	baudrate=9600,
)

# serial
sensor3 = serial_driver.XYMD02(
	address=1, 
	port='/dev/serial0', 
	baudrate=9600,
)

prev_time = 0

if __name__ == '__main__':
	print(f"TEST1: One Time Data Retrieval")
	print("---pymodbus---")
	prev_time = perf_counter()
	temperature = sensor1.get_temperature()
	humidity = sensor1.get_humidity()
	delta_time = perf_counter() - prev_time
	print(f"time: {delta_time:.4f} s\n")

	print("---minimalmodbus---")
	prev_time = perf_counter()
	temperature = sensor2.get_temperature()
	humidity = sensor2.get_humidity()
	delta_time = perf_counter() - prev_time
	print(f"time: {delta_time:.4f} s\n")

	print("---serial---")
	prev_time = perf_counter()
	temperature = sensor3.get_temperature()
	sleep(0.001)
	humidity = sensor3.get_humidity()
	delta_time = perf_counter() - prev_time
	print(f"time: {delta_time:.4f} s\n")
	
	
	
	print(f"\n\nTEST2: Multiple Data Retrieval")
	iter = 200
	print("---pymodbus---")
	prev_time = perf_counter()
	for i in range(iter):
		temperature = sensor1.get_temperature()
		humidity = sensor1.get_humidity()
	delta_time = perf_counter() - prev_time
	print(f"time: {delta_time:.4f} s")
	print(f"average time: {delta_time/iter:.4f} s\n")

	print("---minimalmodbus---")
	prev_time = perf_counter()
	for i in range(iter):
		temperature = sensor2.get_temperature()
		humidity = sensor2.get_humidity()
	delta_time = perf_counter() - prev_time
	print(f"time: {delta_time:.4f} s")
	print(f"average time: {delta_time/iter:.4f} s\n")

	print("---serial---")
	prev_time = perf_counter()
	for i in range(iter):
		temperature = sensor3.get_temperature()
		sleep(0.001)
		humidity = sensor3.get_humidity()
		sleep(0.001)
	delta_time = perf_counter() - prev_time
	print(f"time: {delta_time:.4f} s")
	print(f"average time: {delta_time/iter:.4f} s\n")

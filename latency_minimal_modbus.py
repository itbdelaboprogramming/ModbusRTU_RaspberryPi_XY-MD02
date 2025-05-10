import minimalmodbus
import time

xymd02 = minimalmodbus.Instrument("/dev/ttyS0",1)
xymd02.serial.baudrate = 9600
xymd02.mode = minimalmodbus.MODE_RTU
xymd02.serial.timeout = 3
xymd02.serial.parity = minimalmodbus.serial.PARITY_NONE
xymd02.serial.stopbits = 1
xymd02.serial.bytesize = 8

def temp_sens():
	start_time = time.time()
	temp = xymd02.read_register(1,1, functioncode=4)
	end_time = time.time()
	latency = (end_time - start_time) * 1000
	print(f"Latency: {latency:.2f} ms")
	time.sleep(5)

while True:
	temp_sens()

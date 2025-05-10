import minimalmodbus
import time

def xymd02_min():
	xymd02 = minimalmodbus.Instrument("/dev/ttyS0",1)
	xymd02.serial.baudrate = 9600
	xymd02.mode = minimalmodbus.MODE_RTU
	xymd02.serial.timeout = 3
	xymd02.serial.parity = minimalmodbus.serial.PARITY_NONE
	xymd02.serial.stopbits = 1
	xymd02.serial.bytesize = 8
	temp = xymd02.read_register(1,1, functioncode=4)
	humi = xymd02.read_register(2,1,functioncode =4)
	print(f"Temp: {temp}C | Humidity: {humi}%")
	time.sleep(2)

while True:
	xymd02_min()

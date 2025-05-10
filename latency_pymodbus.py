from pymodbus.client import ModbusSerialClient
import time

def run_xydm02():
	client = ModbusSerialClient(
		method="rtu",
		port="/dev/serial0",       # atau "/dev/ttyS0" "/dev/serial0"
		baudrate=9600,     
		bytesize=8,        
		stopbits=1,        
		parity="N",        
		timeout=3          
	)
	if client.connect():
		try:
			slave_id = 1  
			register_address_temp = 0x0001
			count = 1
			start_time = time.time()
			response = (client.read_input_registers(register_address_temp, count, slave=slave_id)).registers[0]/10
			end_time = time.time()
			latency = (end_time - start_time) * 1000
			print(f"Latency: {latency:.2f} ms")
		finally:
			client.close()
	else:
		print("Gagal boy.")
	time.sleep(5)

# Jalankan fungsi
while True: 
	run_xydm02()


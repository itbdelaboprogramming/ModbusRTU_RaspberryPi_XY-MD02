import serial
import time

# Define Parameter Modbus 
slave_id = 1
func_code = 4
reg_addr_temp = 1
reg_addr_hum = 2
count = 1

# Generate CRC
def gen_modbus_crc(data):
    crc = 0xFFFF
    for byte in data:
        crc ^= byte
        # cek LSB
        for x in range (8):
            lsb = crc & 0x001
            if lsb != 0:
                crc >>= 1
                crc ^= 0xA001
            else :
                crc >>= 1
    return crc.to_bytes(2,byteorder='little')

# Define struktur data modbus untuk humi
assign_req2 = bytearray()
assign_req2.append(slave_id)
assign_req2.append(func_code)
assign_req2 += reg_addr_hum.to_bytes(2,'big')
assign_req2 += count.to_bytes(2,'big')
assign_req2 += gen_modbus_crc(assign_req2)

def humi_serial():
	ser_com_humi = serial.Serial('/dev/ttyS0', baudrate=9600,timeout=3)
	ser_com_humi.write(assign_req2)
	start_time = time.time()
	time.sleep(0.1)
	resp_ser_humi = ser_com_humi.read(9) # harusnya 9 karna slave id (1) function (1) count(1) data (4) crc (2)

	# Cek CRC
	if (len(resp_ser_humi) >= 7):
		real_crc_humi = resp_ser_humi[-2:]
		th_crc_humi = gen_modbus_crc(resp_ser_humi[:-2])
		if real_crc_humi == th_crc_humi:
			reg_val_high_humi = resp_ser_humi[3]
			reg_val_low_humi = resp_ser_humi[4]
			actual_humidity = (reg_val_high_humi << 8) + reg_val_low_humi
			end_time = time.time()
			latency = (end_time - start_time) * 1000
			print(f"Latency: {latency:.2f} ms")
		else :
			print("CRC Humidity != CRC Calculated")
	else :
		print("Data modbus humidity not valid")
	ser_com_humi.close()
	
while True:
	humi_serial()

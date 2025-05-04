import serial

class XYMD02():
	def __init__(
		self, 
		address: int, 
		port: str, 
		baudrate: int, 
		bytesize: int = 8, 
		parity: str = 'N', 
		stopbits: int = 1
	) -> None:
		
		self.address = address
		self.baudrate = baudrate
		self.serial = serial.Serial(port, baudrate=baudrate, bytesize=bytesize, parity=parity, stopbits=stopbits)
		self.temperature_correction = 0
		self.humidity_correction = 0
		
		self.__get_param()
		
	def get_parameter(self):
		return [self.address, self.baudrate, self.temperature_correction, self.humidity_correction]
		
	def get_data(self):
		data = self.__get_data(self.address, 0x04, 0x0001, 0x0002)
		temperature = data[0] / 10
		humidity = data[1] / 10
		return [temperature, humidity]

	def get_address(self):
		return self.address
		
	def get_baudrate(self):
		return self.baudrate
			
	def get_temperature_correction(self):
		return self.temperature_correction
			
	def get_humidity_correction(self):
		return self.humidity_correction
		
	def get_temperature(self):
		data = self.__get_data(self.address, 0x04, 0x0001, 0x0001)
		temperature = data[0] / 10
		return temperature
		
	def get_humidity(self):
		data = self.__get_data(self.address, 0x04, 0x0002, 0x0001)
		humidity = data[0] / 10
		return humidity

	def print_temperature(self):
		temperature = self.get_temperature()
		print(f"Temperature: {temperature} \u00B1 {self.temperature_correction} \u00b0C")

	def print_humidity(self):
		humidity = self.get_humidity()
		print(f"Humidity: {humidity} \u00B1 {self.humidity_correction} %")

	def __get_param(self):
		data = self.__get_data(self.address, 0x03, 0x0101, 0x04)
		self.address = data[0]
		self.baudrate = data[1]
		self.temp_correction = data[2]
		self.humidity_correction = data[3]

	def __get_data(self, slave_id, function_code, start_address, quantity):
		request = self.__modbus_request(slave_id, function_code, start_address, quantity)
		self.serial.write(request)
		response = self.serial.read(5 + 2*quantity)
		
		response_address = 3
		data = []
		
		for i in range(quantity):
			# reading 2 bytes for each data
			data.append(self.__bytes_to_uint16(response[response_address], response[response_address+1]))
			response_address += 2
		
		return data

	def __modbus_request(self, slave_id, function_code, start_address, quantity):
		self.frame = bytearray()
		self.frame.append(slave_id)
		self.frame.append(function_code)
		self.frame.append((start_address >> 8) & 0xFF)
		self.frame.append(start_address & 0xFF)
		self.frame.append((quantity >> 8) & 0xFF)
		self.frame.append(quantity & 0xFF)
		
		crc = self.__calculate_crc16(self.frame)
		self.frame.append(crc & 0xFF)			# CRC Low byte
		self.frame.append((crc >> 8) & 0xFF)		# CRC High byte
		
		return self.frame

	def __calculate_crc16(self, data):
		crc = 0xFFFF
		for pos in data:
			crc ^= pos
			for _ in range(8):
				if (crc & 0x0001):
					crc >>= 1
					crc ^= 0xA001
				else:
					crc >>= 1
		return crc

	def __bytes_to_uint16(self, msb, lsb):
		return (msb << 8) | lsb	

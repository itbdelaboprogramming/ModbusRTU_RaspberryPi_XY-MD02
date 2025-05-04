#!/usr/bin/env python3
import minimalmodbus

class XYMD02(minimalmodbus.Instrument):
	def __init__(
		self, 
		address: int, 
		port: str, 
		baudrate: int, 
		bytesize: int = 8, 
		parity: str = 'N', 
		stopbits: int = 1
	) -> None:

		super().__init__(port, address)
		
		# serial.port
		self.serial.baudrate = baudrate
		self.serial.bytesize = bytesize
		self.serial.parity = parity
		self.serial.stopbits = stopbits

		# address
		self.mode = minimalmodbus.MODE_RTU
		self.clear_buffers_before_each_transaction = True
		
		# data correction
		self.temperature_correction = 0
		self.humidity_correction = 0
		
		self.__get_param()

	def get_parameter(self):
		return [self.address, self.baudrate, self.temperature_correction, self.humidity_correction]
		
	def get_data(self):
		data = self.read_registers(1, 2, functioncode=4)		
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
		result = self.read_register(1, functioncode=4)
		temperature = result / 10
		return temperature
	
	def get_humidity(self):
		result = self.read_register(2, functioncode=4)
		humidity = result / 10
		return humidity

	def print_temperature(self):
		temperature = self.get_temperature()
		print(f"Temperature: {temperature} \u00B1 {self.temperature_correction} \u00b0C")

	def print_humidity(self):
		humidity = self.get_humidity()
		print(f"Humidity: {humidity} \u00B1 {self.humidity_correction} %")

	def __get_param(self):
		[address, baudrate, temp_correction, humid_correction] = self.read_registers(257, 4, functioncode=3)
		
		self.address = address
		self.baudrate = baudrate
		self.temperature_correction = temp_correction
		self.humidity_correction = humid_correction

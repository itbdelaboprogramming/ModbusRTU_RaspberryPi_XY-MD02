#!/usr/bin/env python3
from pymodbus.client import ModbusSerialClient

class XYMD02(ModbusSerialClient):
	def __init__(
		self, 
		address: int, 
		port: str, 
		baudrate: int, 
		bytesize: int = 8, 
		parity: str = 'N', 
		stopbits: int = 1
	) -> None:
		
		super().__init__(port=port, baudrate=baudrate,
						 bytesize=bytesize, parity=parity, stopbits=stopbits, timeout=1)
		self.address = address
		self.temperature_correction = 0
		self.humidity_correction = 0

		if not self.connect():
			raise ConnectionError("Failed to connect to device.")
		
		self.__get_param()
		self.connect()
				
	def __get_param(self):
		result = self.read_holding_registers(257, count=4, slave=self.address)
		if not result.isError():
			self.address = result.registers[0]
			self.baudrate = result.registers[1]
			self.temperature_correction = result.registers[2]
			self.humidity_correction = result.registers[3]

	def get_address(self):
		return self.address
		
	def get_baudrate(self):
		return self.baudrate
			
	def get_temperature_correction(self):
		return self.temperature_correction
			
	def get_humidity_correction(self):
		return self.humidity_correction
		
	def get_temperature(self):
		result = self.read_input_registers(1, slave=self.address)
		if not result.isError():
			return result.registers[0]/10
		else:
			print("Can't read temperature. Error:", result)
			
	def get_humidity(self):
		result = self.read_input_registers(2, slave=self.address)
		if not result.isError():
			return result.registers[0]/10
		else:
			print("Can't read humidity. Error:", result)

	def print_temperature(self):
		temperature = self.get_temperature()
		print(f"Temperature: {temperature} \u00B1 {self.temperature_correction} \u00b0C")

	def print_humidity(self):
		humidity = self.get_humidity()
		print(f"Humidity: {humidity} \u00B1 {self.humidity_correction} %")

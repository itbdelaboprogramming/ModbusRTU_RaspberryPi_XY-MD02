from pymodbus.client import ModbusSerialClient

def run_xydm02():
    # Konfigurasi parameter sesuai dengan tabel
    client = ModbusSerialClient(
        method="rtu",
        port="/dev/serial0",       # atau "/dev/ttyS0" "/dev/serial0"
        baudrate=9600,     
        bytesize=8,        
        stopbits=1,        
        parity="N",        
        timeout=3          
    )
    while (True):
      if client.connect():
          try:
              slave_id = 1  
              register_address_temp = 0x0001
              register_address_hum = 0x0002 
              count = 1

              response = client.read_input_registers(register_address_temp, count, slave=slave_id)
              response2 = client.read_input_registers(register_address_hum, count, slave=slave_id)
              if response.isError():
                  print(f"Error membaca data: {response}")
              else:
                  temp = response.registers[0] / 10.0
              if response2.isError():
                  print(f"Error membaca data: {response2}")
              else:
                  humidity = response2.registers[0] / 10.0
          finally:
              client.close()
      else:
          print("Gagal boy.")
      print(f"Temp: {temp}C | Humidity: | {humidity}%")
      time.sleep(2)
    
# Jalankan fungsi
run_xydm02()


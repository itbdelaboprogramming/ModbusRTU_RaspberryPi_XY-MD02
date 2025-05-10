import serial
import time

# Konfigurasi port serial (sesuaikan dengan port yang digunakan)
ser = serial.Serial(
    port="/dev/ttyS0",  
    baudrate=9600,
    bytesize=serial.EIGHTBITS,
    parity=serial.PARITY_EVEN,
    stopbits=serial.STOPBITS_ONE,
    timeout=3
)

# Fungsi untuk menghitung CRC16 Modbus
def CRC16(data):
    crc = 0xFFFF
    for pos in data:
        crc ^= pos
        for i in range(8):
            if crc & 1:
                crc >>= 1
                crc ^= 0xA001
            else:
                crc >>= 1
    return [crc & 0xFF, (crc >> 8) & 0xFF]

# Fungsi untuk membaca register dari XY-MD02
def read_register(slave_id, start_address, num_registers):
    """ Membaca data dari XY-MD02 menggunakan Modbus RTU """
    # Format Modbus Request: [Slave ID, Function Code, Start Address Hi, Start Address Lo, Num Registers Hi, Num Registers Lo, CRC Lo, CRC Hi]
    request = [slave_id, 0x04, start_address >> 8, start_address & 0xFF, num_registers >> 8, num_registers & 0xFF]
    crc = CRC16(request)
    request += crc  # Tambahkan CRC ke akhir request

    # Kirim request ke XY-MD02
    ser.write(bytes(request))
    time.sleep(0.1)

    # Baca respon dari XY-MD02
    response = ser.read(5 + 2 * num_registers)  # Slave ID, Function Code, Byte Count, Data..., CRC

    # Validasi CRC
    if len(response) >= 5 + 2 * num_registers:
        received_crc = [response[-2], response[-1]]
        calculated_crc = CRC16(response[:-2])

        if received_crc == calculated_crc:
            # Konversi data ke nilai integer (16-bit register)
            values = []
            for i in range(num_registers):
                values.append((response[3 + 2 * i] << 8) + response[4 + 2 * i])
            return values
        else:
            print("CRC Error!")
            return None
    else:
        print("No response or incorrect response length.")
        return None

# Call Function
slave_id = 1  
start_address = 0x0001  
num_registers = 1  

data = read_register(slave_id, start_address, num_registers)
if data:
    print(f"Data dari XY-MD02: {data}")

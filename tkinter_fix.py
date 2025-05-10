from pymodbus.client import ModbusSerialClient
import time
from datetime import datetime, date, timedelta
from tkinter import *
import pytz

global slave_id, date, baudrate, temp, humidity, disp_time
# Inisialisasi variabel
slave_id = 1
device_address = 1  
baudrate = 9600  
today = "2025-03-28"  
disp_time = "00:00:00"
temp = 0.0
humidity = 0.0

def run_xydm02():
    # Konfigurasi parameter sesuai dengan tabel
    client = ModbusSerialClient(
        method="rtu",
        port="/dev/ttyS0",       # atau "/dev/ttyS0" "/dev/serial0"
        baudrate=9600,     
        bytesize=8,        
        stopbits=1,        
        parity="N",        
        timeout=3          
    )
    
    # Data Tanggal
    today = date.today()
    
    # Data Jam
    loc_area = pytz.timezone('Asia/Jakarta')
    curr_time = datetime.now(pytz.utc).astimezone(loc_area)
    disp_time = curr_time.strftime('%H:%M:%S')
    
    if client.connect():
        try: 
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
    label_show_temp.config(text = temp)
    label_show_humidity.config(text = humidity)
    label_show_time.config(text = disp_time)
    label_show_date.config(text = today)
    root.after(3000,run_xydm02)
  

# Initiate
root = Tk()
root.geometry("500x500+500+500")
root.configure(bg ='white')

# Configure column row
root.rowconfigure([0,1,2,3,4,5,6,7,8,9], weight = 1)
root.columnconfigure([0,1,2],weight = 1)

# Buat Label
label_awal = Label(text = "XY-MD02 ACCESS", bg = "#ced6e0", font=("Arial", 20, "bold"))
label_mod_par = Label(text = "MODBUS PARAMETER")
label_dev_addr = Label(text = "Device Address ", justify="left")
label_show_dev_addr = Label(text = slave_id)
label_baudrate = Label(text = "Baudrate ", justify="left")
label_show_baudrate = Label(text = baudrate)

label_time_param = Label(text = "TIME PARAMETER")
label_date = Label(text = "Date ")
label_show_date = Label(text = today)
label_time = Label(text = "Time ")
label_show_time = Label(text = disp_time)

label_mon_res = Label(text = "MONITORING RESULT")
label_temp = Label(text = "Temperature (\u00B0C)")
label_show_temp = Label(text = temp)
label_acc_temp = Label(text = "\u00B10.5\u00B0C")
label_humidity = Label(text = "Humidity (%)")
label_show_humidity = Label(text = humidity)
label_acc_humidity = Label(text = "\u00B13%")

# Configure Susunan
label_awal.grid(row = 0, column=0,columnspan=3, sticky = "wens")

label_mod_par.grid(row = 1, column=0,columnspan=3, sticky = "we")
label_dev_addr.grid(row = 2, column = 0,sticky = "wens")
label_show_dev_addr.grid(row =2, column = 1,columnspan =2,sticky = "wens")
label_baudrate.grid(row = 3, column=0,sticky = "wens")
label_show_baudrate.grid(row =3, column = 1,columnspan =2,sticky = "wens")


label_time_param.grid(row = 4, column=0,columnspan=3, sticky = "we")
label_date.grid(row = 5, column = 0,sticky = "wens")
label_show_date.grid(row =5, column = 1,columnspan =2,sticky = "wens")
label_time.grid(row = 6, column=0,sticky = "wens")
label_show_time.grid(row =6, column = 1,columnspan =2,sticky = "wens")


label_mon_res.grid(row = 7, column=0,columnspan=3, sticky = "we")
label_temp.grid(row= 8, column = 0,sticky = "wens")
label_show_temp.grid(row=8,column=1,sticky = "wens")
label_acc_temp.grid(row=8,column=2,sticky = "wens")
label_humidity.grid(row= 9, column = 0,sticky = "wens")
label_show_humidity.grid(row=9,column=1,sticky = "wens")
label_acc_humidity.grid(row=9,column=2,sticky = "wens")

# Jalankan fungsi
run_xydm02()

root.mainloop()

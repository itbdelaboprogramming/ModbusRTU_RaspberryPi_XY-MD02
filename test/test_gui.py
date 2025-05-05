from lib.XYMD02 import serial_driver
from datetime import datetime
from time import sleep
import tkinter as tk

root = tk.Tk()
root.title("Sensor Data Display")

# Initialize sensor
sensor1 = serial_driver.XYMD02(
    address=1,
    port='/dev/serial0',
    baudrate=9600
)

# Text creation
text = {
    'address': tk.StringVar(),
    'baudrate': tk.StringVar(),
    'timestamp': tk.StringVar(),
    'temperature': tk.StringVar(),
    'humidity': tk.StringVar(),
}

# Initialize value
text['address'].set(f": {sensor1.get_address()}")
text['baudrate'].set(f": {sensor1.get_baudrate()}")

# Frame creation
frame = tk.Frame(root)
frame.pack(padx=20, pady=20)

rows = ['address', 'baudrate', 'timestamp', 'temperature', 'humidity']
labels_left = {
    'address': 'Device ID:',
    'baudrate': 'Baudrate:',
    'timestamp': 'Timestamp:',
    'temperature': 'Temperature:',
    'humidity': 'Humidity:'
}

for i, key in enumerate(rows):
    label_name = tk.Label(frame, text=labels_left[key], font=("Arial", 14), anchor="w", width=12)
    label_value = tk.Label(frame, textvariable=text[key], font=("Arial", 14), anchor="w", width=25)

    label_name.grid(row=i, column=0, sticky="w", pady=4)
    label_value.grid(row=i, column=1, sticky="w", pady=4)

# Update data sensor every second
def update_sensor_data():
    try:        
        temperature = sensor1.get_temperature()
        sleep(0.001)
        temp_corr = sensor1.get_temperature_correction()
        sleep(0.001)
        humidity = sensor1.get_humidity()
        sleep(0.001)
        hum_corr = sensor1.get_humidity_correction()
        
        text['temperature'].set(f": {temperature:.2f} \u00B1 {temp_corr:.2f} \u00b0C")
        text['humidity'].set(f": {humidity:.2f} \u00B1 {hum_corr:.2f} %")
        text['timestamp'].set(f": {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    except Exception as e:
        text['temperature'].set(f"Temperature: Error")
        text['humidity'].set(f"Humidity: Error")
        text['timestamp'].set(f"Timestamp: Error")
        print(f"Error reading sensor: {e}")

    # recall after 1000 ms
    root.after(1000, update_sensor_data)

if __name__ == '__main__':    
    # Update sensor when GUI started
    update_sensor_data()
    
    # Start GUI
    root.mainloop()

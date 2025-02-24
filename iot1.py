import network
import urequests
import time
from machine import Pin, ADC
from dht import DHT11

# *** Konfigurasi WiFi ***
SSID = "TECNO POVA 5 Pro 5G"
PASSWORD = "irfanbhq"

wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect(SSID, PASSWORD)

while not wifi.isconnected():
    pass  # Tunggu koneksi WiFi

print("Terhubung ke WiFi!")

# *** Inisialisasi Sensor ***
dht_pin = Pin(4)  # GPIO untuk DHT11
dht_sensor = DHT11(dht_pin)
pir_sensor = Pin(23, Pin.IN)  # GPIO untuk PIR
ldr_sensor = ADC(Pin(34))  # GPIO untuk LDR (analog)
ldr_sensor.atten(ADC.ATTN_11DB)  # Atur agar membaca tegangan hingga 3.3V

# *** Konfigurasi Ubidots ***
UBIDOTS_TOKEN = "BBUS-uMeN6SuslZkOynkpcNvEGmIyhPE0SV"
UBIDOTS_DEVICE = "esp32-sic6"
UBIDOTS_URL = f"https://industrial.api.ubidots.com/api/v1.6/devices/{UBIDOTS_DEVICE}/"

HEADERS_UBIDOTS = {
    "X-Auth-Token": UBIDOTS_TOKEN,
    "Content-Type": "application/json"
}

# *** Konfigurasi API untuk MongoDB ***
API_MONGODB_URL = "http://192.168.120.33:5000/sensor"

HEADERS_MONGODB = {
    "Content-Type": "application/json"
}

# *** Fungsi untuk mendapatkan waktu sekarang dalam format YYYY-MM-DD HH:MM ***
def get_current_time():
    tm = time.localtime()
    return "{:04d}-{:02d}-{:02d} {:02d}:{:02d}".format(tm[0], tm[1], tm[2], tm[3], tm[4])

# *** Fungsi Mengirim Data ke Ubidots ***
def send_to_ubidots(temp, humidity, motion, light):
    payload = {
        "temperature": temp,
        "humidity": humidity,
        "motion": motion,
        "light": light  # Data LDR
    }
    try:
        response = urequests.post(UBIDOTS_URL, json=payload, headers=HEADERS_UBIDOTS)
        print("Response Ubidots:", response.text)
        response.close()
    except Exception as e:
        print("Error Ubidots:", e)

# *** Fungsi Mengirim Data ke API MongoDB dengan Waktu ***
def send_to_mongodb(temp, humidity, motion, light):
    timestamp = get_current_time()  # Ambil waktu sekarang
    payload = {
        "temperature": temp,
        "humidity": humidity,
        "motion": motion,
        "light": light,  # Data LDR
        "timestamp": timestamp  # Tambahkan waktu sekarang
    }
    try:
        response = urequests.post(API_MONGODB_URL, json=payload, headers=HEADERS_MONGODB)
        print("Response MongoDB:", response.text)
        response.close()
    except Exception as e:
        print("Error MongoDB:", e)

# *** Loop Utama: Baca Sensor & Kirim Data Setiap 10 Detik ***
while True:
    dht_sensor.measure()
    temperature = dht_sensor.temperature()
    humidity = dht_sensor.humidity()
    motion = pir_sensor.value()
    light_value = ldr_sensor.read()  # Baca nilai LDR (0-4095)
    
    timestamp = get_current_time()  # Dapatkan waktu sekarang
    print(f"[{timestamp}] Suhu: {temperature}C, Kelembapan: {humidity}%, Gerakan: {motion}, Cahaya: {light_value}")

    # Kirim data ke Ubidots
    send_to_ubidots(temperature, humidity, motion, light_value)

    # Kirim data ke MongoDB
    send_to_mongodb(temperature, humidity, motion, light_value)

    time.sleep(5)  # Tunggu 10 detik sebelum membaca ulang

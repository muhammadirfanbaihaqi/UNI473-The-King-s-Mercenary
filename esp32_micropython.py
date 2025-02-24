import network  # Modul untuk menghubungkan ESP32 ke WiFi
import urequests  # Modul untuk melakukan HTTP request (POST ke Ubidots dan MongoDB)
import time  # Modul untuk delay dan mendapatkan waktu
from machine import Pin, ADC  # Modul untuk kontrol GPIO pada ESP32
from dht import DHT11  # Modul untuk sensor DHT11 (Suhu & Kelembapan)

# *** Konfigurasi WiFi ***
SSID = "TECNO POVA 5 Pro 5G"  # Nama jaringan WiFi
PASSWORD = "irfanbhq"  # Password WiFi

wifi = network.WLAN(network.STA_IF)  # Membuat objek WiFi dengan mode Station
wifi.active(True)  # Mengaktifkan WiFi
wifi.connect(SSID, PASSWORD)  # Menghubungkan ESP32 ke WiFi

# Tunggu hingga terhubung ke WiFi
while not wifi.isconnected():
    pass  # Looping sampai koneksi sukses

print("Terhubung ke WiFi!")

# *** Inisialisasi Sensor ***
dht_pin = Pin(4)  # GPIO 4 untuk DHT11
dht_sensor = DHT11(dht_pin)  # Membuat objek sensor DHT11
pir_sensor = Pin(23, Pin.IN)  # GPIO 23 untuk sensor PIR (Gerakan)
ldr_sensor = ADC(Pin(34))  # GPIO 34 sebagai input analog untuk LDR
ldr_sensor.atten(ADC.ATTN_11DB)  # Atur agar membaca tegangan hingga 3.3V

# *** Konfigurasi Ubidots ***
UBIDOTS_TOKEN = "BBUS-uMeN6SuslZkOynkpcNvEGmIyhPE0SV"  # Token autentikasi Ubidots
UBIDOTS_DEVICE = "esp32-sic6"  # Nama perangkat di Ubidots
UBIDOTS_URL = f"https://industrial.api.ubidots.com/api/v1.6/devices/{UBIDOTS_DEVICE}/"  # Endpoint API Ubidots

HEADERS_UBIDOTS = {
    "X-Auth-Token": UBIDOTS_TOKEN,
    "Content-Type": "application/json"
}

# *** Konfigurasi API untuk MongoDB ***
API_MONGODB_URL = "http://192.168.120.33:5000/sensor"  # URL endpoint API MongoDB

HEADERS_MONGODB = {
    "Content-Type": "application/json"
}

# *** Fungsi untuk mendapatkan waktu sekarang dalam format YYYY-MM-DD HH:MM ***
def get_current_time():
    """Mengembalikan timestamp dalam format YYYY-MM-DD HH:MM"""
    tm = time.localtime()  # Dapatkan waktu lokal ESP32
    return "{:04d}-{:02d}-{:02d} {:02d}:{:02d}".format(tm[0], tm[1], tm[2], tm[3], tm[4])

# *** Fungsi Mengirim Data ke Ubidots ***
def send_to_ubidots(temp, humidity, motion, light):
    """Mengirim data sensor ke Ubidots melalui HTTP POST"""
    payload = {
        "temperature": temp,  # Suhu
        "humidity": humidity,  # Kelembapan
        "motion": motion,  # Gerakan dari PIR
        "light": light  # Intensitas cahaya dari LDR
    }
    try:
        response = urequests.post(UBIDOTS_URL, json=payload, headers=HEADERS_UBIDOTS)
        print("Response Ubidots:", response.text)  # Cetak respons dari server Ubidots
        response.close()
    except Exception as e:
        print("Error Ubidots:", e)  # Cetak error jika gagal mengirim data

# *** Fungsi Mengirim Data ke API MongoDB dengan Waktu ***
def send_to_mongodb(temp, humidity, motion, light):
    """Mengirim data sensor ke MongoDB melalui HTTP POST"""
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
        print("Response MongoDB:", response.text)  # Cetak respons dari server MongoDB
        response.close()
    except Exception as e:
        print("Error MongoDB:", e)  # Cetak error jika gagal mengirim data

# *** Loop Utama: Baca Sensor & Kirim Data Setiap 5 Detik ***
while True:
    dht_sensor.measure()  # Baca data dari DHT11
    temperature = dht_sensor.temperature()  # Ambil suhu
    humidity = dht_sensor.humidity()  # Ambil kelembapan
    motion = pir_sensor.value()  # Baca status sensor PIR (0 = tidak ada gerakan, 1 = ada gerakan)
    light_value = ldr_sensor.read()  # Baca nilai LDR (0-4095)
    
    timestamp = get_current_time()  # Dapatkan waktu sekarang
    print(f"[{timestamp}] Suhu: {temperature}C, Kelembapan: {humidity}%, Gerakan: {motion}, Cahaya: {light_value}")

    # Kirim data ke Ubidots
    send_to_ubidots(temperature, humidity, motion, light_value)

    # Kirim data ke MongoDB
    send_to_mongodb(temperature, humidity, motion, light_value)

    time.sleep(5)  # Tunggu 5 detik sebelum membaca ulang

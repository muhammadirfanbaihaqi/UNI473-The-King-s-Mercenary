from flask import Flask, request, jsonify  # Import library Flask untuk membuat API
from pymongo.mongo_client import MongoClient  # Import MongoClient untuk koneksi ke MongoDB
from pymongo.server_api import ServerApi  # Import ServerApi untuk koneksi ke MongoDB Atlas

# Inisialisasi aplikasi Flask
app = Flask(__name__)

# Koneksi ke MongoDB Atlas menggunakan URI
uri = "mongodb+srv://muhammadirfanbaihaqi538:9bS08vSHwy07ETmY@cluster0.rpgtm.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

# Membuat klien baru dan menghubungkan ke server MongoDB
client = MongoClient(uri, server_api=ServerApi('1'))

# Memilih database "iot_db" di dalam MongoDB
db = client["iot_db"]

# Memilih koleksi "SIC6_COLLECTION" untuk menyimpan data sensor
collection = db["SIC6_COLLECTION"]

# Endpoint untuk menerima data sensor melalui metode HTTP POST
@app.route('/sensor', methods=['POST'])
def save_sensor_data():
    try:
        data = request.json  # Mengambil data JSON dari request yang dikirim oleh ESP32
        collection.insert_one(data)  # Menyimpan data ke koleksi MongoDB
        return jsonify({"message": "Data saved"}), 201  # Mengembalikan respon sukses (HTTP 201 Created)
    except Exception as e:
        return jsonify({"error": str(e)}), 500  # Jika terjadi error, kembalikan pesan error dengan status 500

# Menjalankan server Flask pada host 0.0.0.0 dengan port 5000
# debug mode diaktifkan untuk mempermudah debugging
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

from flask import Flask, request, jsonify
# from pymongo import MongoClient
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

app = Flask(__name__)

# Koneksi ke MongoDB
# client = MongoClient("mongodb+srv://user:password@cluster.mongodb.net/mydatabase")
uri = "mongodb+srv://muhammadirfanbaihaqi538:9bS08vSHwy07ETmY@cluster0.rpgtm.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

db = client["iot_db"]
collection = db["SIC6_COLLECTION"]

@app.route('/sensor', methods=['POST'])
def save_sensor_data():
    try:
        data = request.json
        collection.insert_one(data)
        return jsonify({"message": "Data saved"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)



# from pymongo.mongo_client import MongoClient
# from pymongo.server_api import ServerApi

# uri = "mongodb+srv://muhammadirfanbaihaqi538:<db_password>@cluster0.rpgtm.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

# # Create a new client and connect to the server
# client = MongoClient(uri, server_api=ServerApi('1'))

# # Send a ping to confirm a successful connection
# try:
#     client.admin.command('ping')
#     print("Pinged your deployment. You successfully connected to MongoDB!")
# except Exception as e:
#     print(e)

from flask import Flask, request, jsonify
import mysql.connector

app = Flask(__name__)

db_config = {
    "host": "database",  # Change if necessary
    "port": 3306,
    "user": "sensor_app",
    "password": "your_password",
    "database": "sensor_db"
}


# RECEIVE SENSOR DATA
@app.route('/sensor/data', methods=['POST'])
def receive_data():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"status": "error", "message": "Invalid JSON"}), 400

    light = data.get("light")
    temperature = data.get("temperature")
    humidity = data.get("humidity")

    if any(value is None for value in (light, temperature, humidity)):
        return jsonify({"status": "error", "message": "Missing sensor data"}), 400

    connection = None
    cursor = None

    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()

        sql = """
            INSERT INTO sensor_data (light, temperature, humidity)
            VALUES (%s, %s, %s)
        """

        cursor.execute(sql, (light, temperature, humidity))
        connection.commit()

        return jsonify({
            "status": "success",
            "id": cursor.lastrowid
        }), 200

    except mysql.connector.Error:
        app.logger.exception("MySQL error")
        return jsonify({"status": "error", "message": "Database error"}), 500

    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()


# READ SENSOR DATA
@app.route('/sensor/data', methods=['GET'])
def get_data():
    connection = None
    cursor = None

    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()

        cursor.execute("SELECT * FROM sensor_data")
        DBData = cursor.fetchall()

        print(DBData)

        return jsonify(DBData), 200

    except mysql.connector.Error:
        app.logger.exception("MySQL error")
        return jsonify({"status": "error", "message": "Database error"}), 500

    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

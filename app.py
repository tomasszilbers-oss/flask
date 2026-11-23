from flask import Flask, request, jsonify
import mysql.connector

app = Flask(__name__)

# MySQL connection settings
db_config = {
    "host": "127.0.0.1",
    "port": 3306,
    "user": "sensor_app",
    "password": "your_password",
    "database": "sensor_db"
}


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
        # Connect to MySQL
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()

        # Insert sensor data
        sql = """
            INSERT INTO sensor_data (light, temperature, humidity)
            VALUES (%s, %s, %s)
        """

        values = (light, temperature, humidity)

        cursor.execute(sql, values)
        connection.commit()

        print(f"Light: {light}")
        print(f"Temperature: {temperature}")
        print(f"Humidity: {humidity}")

        return jsonify({
            "status": "success",
            "id": cursor.lastrowid
        }), 200

    except mysql.connector.Error as err:
        app.logger.exception("MySQL error")
        return jsonify({
            "status": "error",
            "message": "Database operation failed"
        }), 500

    finally:
        if cursor is not None:
            cursor.close()

        if connection is not None and connection.is_connected():
            connection.close()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

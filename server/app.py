from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/api/v1/log', methods=['POST'])
def log_event():
    """
    Receives and logs a single user behavior data from the extension.
    (This can be kept for simplicity or for single event logging if needed)
    """
    data = request.get_json()
    if not data:
        return jsonify({"status": "error", "message": "No data provided"}), 400

    print("Received single log:", data)
    return jsonify({"status": "success", "message": "Log received"}), 201

@app.route('/api/v1/log_batch', methods=['POST'])
def log_batch_events():
    """
    Receives and logs a batch of user behavior data from the extension.
    """
    data = request.get_json()
    if not isinstance(data, list) or not data:
        return jsonify({"status": "error", "message": "Invalid or empty batch"}), 400

    # In a real implementation, this would be an efficient bulk insert into a database.
    print(f"Received batch of {len(data)} logs.")
    for log in data:
        print(" - Log:", log)

    return jsonify({"status": "success", "message": f"Batch of {len(data)} logs received"}), 201


if __name__ == '__main__':
    app.run(debug=True, port=5000)
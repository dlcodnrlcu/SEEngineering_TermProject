import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from datetime import datetime
import db

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Apply CORS settings
CORS(app, resources={r"/api/*": {"origins": "*"}})

@app.route('/api/v1/log_batch', methods=['POST'])
def log_batch_events():
    """
    Receives a batch of user behavior logs from the extension, adds a timestamp,
    and inserts them into the database.
    """
    logs = request.get_json()
    if not isinstance(logs, list) or not logs:
        return jsonify({"status": "error", "message": "Invalid or empty batch"}), 400

    # Add server-side timestamp
    timestamp = datetime.utcnow()
    for log in logs:
        log['server_received_at'] = timestamp

    # Insert into database
    result = db.insert_logs(logs)
    if result:
        return jsonify({"status": "success", "message": f"Batch of {len(logs)} logs received"}), 201
    else:
        return jsonify({"status": "error", "message": "Failed to save logs to database"}), 500

@app.route('/api/v1/guide', methods=['GET'])
def get_guide():
    """
    Provides a guide for a given URL.
    """
    url = request.args.get('url')
    if not url:
        return jsonify({"status": "error", "message": "URL parameter is required"}), 400

    guide = db.get_guide_for_url(url)
    if guide:
        # Pymongo returns an _id field which is not JSON serializable by default
        if '_id' in guide:
            guide['_id'] = str(guide['_id'])
        return jsonify({"status": "success", "data": guide}), 200
    else:
        return jsonify({"status": "success", "data": None}), 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "true").lower() == "true"
    app.run(debug=debug, port=port)
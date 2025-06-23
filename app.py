from flask import Flask, request, jsonify, send_from_directory
import os
import json
from datetime import datetime

app = Flask(__name__, static_folder='static', static_url_path='')

DATA_FILE = 'schedule_data.json'

def load_schedule():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

def save_schedule(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/api/schedule', methods=['GET'])
def get_schedule():
    year = request.args.get('year')
    month = request.args.get('month')
    if not year or not month:
        return jsonify({"error": "year and month parameters are required"}), 400
    schedule = load_schedule()
    # Filter schedule for the requested year and month
    filtered = {}
    for date_str, text in schedule.items():
        try:
            dt = datetime.strptime(date_str, '%Y-%m-%d')
            if dt.year == int(year) and dt.month == int(month):
                filtered[date_str] = text
        except ValueError:
            continue
    return jsonify(filtered)

@app.route('/api/schedule', methods=['POST'])
def post_schedule():
    data = request.get_json()
    if not data or 'date' not in data or 'text' not in data:
        return jsonify({"error": "date and text fields are required"}), 400
    date_str = data['date']
    text = data['text']
    # Validate date format
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        return jsonify({"error": "date format must be YYYY-MM-DD"}), 400
    schedule = load_schedule()
    schedule[date_str] = text
    save_schedule(schedule)
    return jsonify({"message": "Schedule saved successfully"})

if __name__ == '__main__':
    app.run(debug=True)

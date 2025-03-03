from flask import Flask, render_template, request, jsonify
import csv
import os
from collections import defaultdict

app = Flask(__name__)

DATA_FILE = "user_interests.csv"

def initialize_csv(file_path):
    if not os.path.exists(file_path):
        with open(file_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["name", "interests"])
        print(f"Created {file_path} with headers.")
    else:
        with open(file_path, 'r', newline='') as f:
            first_line = f.readline().strip()
            if not first_line or first_line != "name,interests":
                with open(file_path, 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(["name", "interests"])
                print(f"Reset {file_path} with correct headers.")

initialize_csv(DATA_FILE)

class RecommendationSystem:
    def __init__(self):
        self.users = {}
        self.inverted_index = defaultdict(set)

    def load_data(self, file_path):
        self.users.clear()
        self.inverted_index.clear()
        try:
            with open(file_path, 'r') as f:
                reader = csv.DictReader(f)
                if 'name' not in reader.fieldnames or 'interests' not in reader.fieldnames:
                    print(f"Error: CSV file {file_path} missing required headers.")
                    return
                for row in reader:
                    user_id = row['name']
                    interests = set(interest.lower() for interest in row['interests'].split(','))
                    self.users[user_id] = interests
                    for interest in interests:
                        self.inverted_index[interest].add(user_id)
            print(f"Loaded {len(self.users)} users for recommendation.")
        except Exception as e:
            print(f"Failed to load data from {file_path}: {e}")

    def jaccard_similarity(self, set1, set2):
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        return intersection / union if union != 0 else 0

    def recommend(self):
        if len(self.users) < 2:
            return {}
        recommendations = {}
        for user_id, interests in self.users.items():
            other_users = set(self.users.keys()) - {user_id}
            user_recs = []
            for other_user in other_users:
                similarity = self.jaccard_similarity(interests, self.users[other_user])
                user_recs.append((other_user, similarity))
            user_recs.sort(key=lambda x: x[1], reverse=True)
            recommendations[user_id] = user_recs
        return recommendations

def name_exists(name, file_path):
    if not os.path.exists(file_path):
        return False
    try:
        with open(file_path, 'r') as f:
            reader = csv.DictReader(f)
            if 'name' not in reader.fieldnames:
                print(f"Error: 'name' column not found in {file_path}.")
                return False
            for row in reader:
                if row['name'].strip().lower() == name.strip().lower():
                    return True
    except Exception as e:
        print(f"Error checking name in {file_path}: {e}")
        return False
    return False

@app.route('/', methods=['GET', 'POST'])
def index():
    print(f"Request method: {request.method}, URL: {request.url}")
    rec_system = RecommendationSystem()
    users = []
    recommendations = {}
    error_message = None

    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    if request.method == 'POST':
        print("POST request received at /")
        name = request.form.get('name')
        interests = request.form.get('interests')
        
        print(f"Received submission - Name: {name}, Interests: {interests}")
        
        if not name or not interests:
            error_message = "Please provide both name and interests!"
        elif name_exists(name, DATA_FILE):
            error_message = f"Error: The name '{name}' is already registered!"
        else:
            interests_lower = ','.join(interest.strip().lower() for interest in interests.split(','))
            with open(DATA_FILE, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([name, interests_lower])
                print(f"Saved to CSV: {name}, {interests_lower}")

        rec_system.load_data(DATA_FILE)
        recommendations = rec_system.recommend()
        with open(DATA_FILE, 'r') as f:
            reader = csv.DictReader(f)
            if 'name' not in reader.fieldnames or 'interests' not in reader.fieldnames:
                print(f"Error: CSV file {DATA_FILE} missing required headers.")
            else:
                users = list(reader)

        if is_ajax:
            response_data = {
                'error_message': error_message,
                'users': [{'name': user['name'], 'interests': user['interests']} for user in users],
                'recommendations': {user: [(rec[0], float(rec[1])) for rec in recs] for user, recs in recommendations.items()}
            }
            print(f"Sending JSON response: {response_data}")
            return jsonify(response_data)

    try:
        rec_system.load_data(DATA_FILE)
        recommendations = rec_system.recommend()
        with open(DATA_FILE, 'r') as f:
            reader = csv.DictReader(f)
            if 'name' not in reader.fieldnames or 'interests' not in reader.fieldnames:
                print(f"Error: CSV file {DATA_FILE} missing required headers.")
            else:
                users = list(reader)
        print("Loaded users from CSV:", users)
        print("Generated recommendations:", recommendations)
    except Exception as e:
        print(f"Error processing data: {e}")
        return f"Error: {e}", 500

    return render_template('index.html', users=users, recommendations=recommendations, error_message=error_message)

@app.route('/submit', methods=['GET', 'POST'])
def catch_submit():
    print("Unexpected request to /submit")
    return "Error: This route should not be accessed. Form should submit to /", 404

if __name__ == '__main__':
    print("Starting Flask app...")
    app.run(debug=True, host='0.0.0.0', port=5000)
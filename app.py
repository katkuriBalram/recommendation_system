from flask import Flask, render_template, request, redirect, url_for
import csv
import os
from collections import defaultdict

app = Flask(__name__)

DATA_FILE = "user_interests.csv"

# Initialize CSV file with headers if it doesn't exist
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["name", "interests"])
    print(f"Created {DATA_FILE} with headers.")

# Recommendation System Class
class RecommendationSystem:
    def __init__(self, threshold=0.3, top_n=5):
        self.threshold = threshold
        self.top_n = top_n
        self.users = {}
        self.inverted_index = defaultdict(set)

    def load_data(self, file_path):
        with open(file_path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                user_id = row['name']  # Use 'name' instead of 'user_id'
                interests = set(row['interests'].split(','))
                self.users[user_id] = interests
                for interest in interests:
                    self.inverted_index[interest].add(user_id)
        print(f"Loaded {len(self.users)} users for recommendation.")

    def jaccard_similarity(self, set1, set2):
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        return intersection / union if union != 0 else 0

    def get_candidate_users(self, user_interests):
        candidates = set()
        for interest in user_interests:
            candidates.update(self.inverted_index[interest])
        return candidates

    def recommend(self):
        recommendations = {}
        for user_id, interests in self.users.items():
            candidates = self.get_candidate_users(interests) - {user_id}
            user_recs = []
            for candidate_id in candidates:
                similarity = self.jaccard_similarity(interests, self.users[candidate_id])
                if similarity >= self.threshold:
                    user_recs.append((candidate_id, similarity))
            user_recs.sort(key=lambda x: x[1], reverse=True)
            recommendations[user_id] = user_recs[:self.top_n]
        return recommendations

@app.route('/')
def index():
    """Display the form and existing user data."""
    users = []
    try:
        with open(DATA_FILE, 'r') as f:
            reader = csv.DictReader(f)
            users = list(reader)
            print("Loaded users from CSV:", users)
    except Exception as e:
        print(f"Error loading CSV: {e}")
    return render_template('index.html', users=users)

@app.route('/submit', methods=['POST'])
def submit():
    """Handle form submission."""
    name = request.form.get('name')
    interests = request.form.get('interests')
    
    print(f"Received submission - Name: {name}, Interests: {interests}")
    
    if not name or not interests:
        return "Please provide both name and interests!", 400
    
    with open(DATA_FILE, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([name, interests])
        print(f"Saved to CSV: {name}, {interests}")
    
    return redirect(url_for('index'))

@app.route('/recommend')
def recommend():
    """Generate and display recommendations."""
    rec_system = RecommendationSystem(threshold=0.3, top_n=3)
    try:
        rec_system.load_data(DATA_FILE)
        recommendations = rec_system.recommend()
        print("Generated recommendations:", recommendations)  # Debug print
        return render_template('recommend.html', recommendations=recommendations)
    except Exception as e:
        return f"Error generating recommendations: {e}", 500

if __name__ == '__main__':
    print("Starting Flask app...")
    app.run(debug=True, host='0.0.0.0', port=5000)
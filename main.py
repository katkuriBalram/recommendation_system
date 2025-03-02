import csv
from collections import defaultdict
import json
import time
import random

# Pool of possible interests
INTEREST_POOL = [
    "python", "ml", "data science", "visualizations", "django", "flask", "backend",
    "html", "css", "javascript", "react", "node.js", "frontend", "sql", "nosql",
    "cloud", "aws", "devops", "security", "ai", "nlp", "big data", "statistics",
    "java", "kotlin", "android", "ios", "swift", "tensorflow", "pytorch"
]

class RecommendationSystem:
    def __init__(self, threshold=0.1, top_n=1):
        self.threshold = threshold
        self.top_n = top_n
        self.users = {}  # user_id -> set of interests
        self.inverted_index = defaultdict(set)  # interest -> set of user_ids

    def load_data(self, file_path):
        with open(file_path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                user_id = row['name']  # Use 'name' instead of 'user_id'
                interests = set(row['interests'].split(','))
                self.users[user_id] = interests
                for interest in interests:
                    self.inverted_index[interest].add(user_id)
        print(f"Loaded {len(self.users)} users.")

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

    def save_recommendations(self, recommendations, output_file):
        with open(output_file, 'w') as f:
            json.dump(recommendations, f, indent=2)
        print(f"Recommendations saved to {output_file}")


# Generate synthetic data
def generate_synthetic_data(file_path, num_users=10, interests_per_user=10):
    data = []
    for i in range(1, num_users + 1):
        user_id = f"user{i}"
        # Randomly sample 10 interests, ensuring some overlap
        interests = random.sample(INTEREST_POOL, interests_per_user)
        data.append({"user_id": user_id, "interests": ",".join(interests)})
    
    with open(file_path, "w", newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["user_id", "interests"])
        writer.writeheader()
        writer.writerows(data)
    print(f"Generated synthetic data for {num_users} users with {interests_per_user} interests each.")



# Main execution
def main():
    # Generate synthetic data
    generate_synthetic_data("users_large.csv", num_users=10, interests_per_user=10)

    # Run recommendation system
    rec_system = RecommendationSystem(threshold=0.3, top_n=3)
    
    start_time = time.time()
    rec_system.load_data("users_large.csv")
    print("User interests:", dict(rec_system.users))  # Debug: Show loaded data
    recommendations = rec_system.recommend()
    rec_system.save_recommendations(recommendations, "recommendations_large.json")
    end_time = time.time()
    
    print(f"Execution time: {end_time - start_time:.2f} seconds")
    
    # Print recommendations
    for user, recs in recommendations.items():
        print(f"{user} recommendations:")
        for rec_user, score in recs:
            print(f"  - {rec_user} (similarity: {score:.2f})")

if __name__ == "__main__":
    main()
import os
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
import joblib

# ✅ Ensure paths work regardless of current folder
data_path = os.path.join(os.path.dirname(__file__), "quiz_data.csv")
model_path = os.path.join(os.path.dirname(__file__), "quiz_predictor.pkl")

# Load data
df = pd.read_csv(data_path)

# Convert difficulty to numeric if stored as strings
difficulty_map = {"easy": 1, "medium": 2, "hard": 3}
df['difficulty'] = df['difficulty'].map(difficulty_map)

# Ensure time_taken is numeric
df['time_taken'] = pd.to_numeric(df['time_taken'], errors='coerce')

# Drop rows with missing values in essential columns
df = df.dropna(subset=['difficulty', 'time_taken', 'is_correct'])

# Prepare features and target
X = df[['difficulty', 'time_taken']]
y = df['is_correct'].astype(int)

# Split dataset
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Train Decision Tree model
model = DecisionTreeClassifier(max_depth=5)
model.fit(X_train, y_train)

# Save trained model
joblib.dump(model, model_path)
print(f"✅ Model trained and saved as {model_path}")

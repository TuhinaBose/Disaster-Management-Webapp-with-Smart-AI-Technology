"""
Disaster Risk Machine Learning Model Trainer
Trains a Scikit-learn RandomForestClassifier on environmental data and saves model to disk.
"""

import os
import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score

def generate_synthetic_disaster_dataset(num_samples=1500):
    """
    Generates realistic synthetic environmental data for training using numpy.
    Features:
    - rainfall (mm, 0 - 350)
    - river_level (m, 0.5 - 12.0)
    - wind_speed (km/h, 0 - 160)
    - temperature (°C, 5 - 48)
    - humidity (%, 10 - 100)
    - earthquake_mag (Richter scale, 0 - 8.5)
    """
    np.random.seed(42)

    rainfall = np.random.uniform(0, 350, num_samples)
    river_level = np.random.uniform(0.5, 12.0, num_samples)
    wind_speed = np.random.uniform(0, 160, num_samples)
    temperature = np.random.uniform(5, 48, num_samples)
    humidity = np.random.uniform(10, 100, num_samples)
    earthquake_mag = np.random.uniform(0, 8.5, num_samples)

    X = np.column_stack((rainfall, river_level, wind_speed, temperature, humidity, earthquake_mag))
    labels = []

    for r, riv, w, t, h, eq in zip(rainfall, river_level, wind_speed, temperature, humidity, earthquake_mag):
        score = 0
        if r > 160 or riv > 7.5: score += 40
        elif r > 80 or riv > 4.5: score += 20
        
        if w > 90: score += 30
        elif w > 55: score += 15
        
        if eq > 5.5: score += 45
        elif eq > 3.8: score += 20

        if t > 43 and h < 25: score += 15

        if score >= 55 or eq >= 5.5 or (r > 200 and riv > 8.0):
            labels.append('High')
        elif score >= 25:
            labels.append('Medium')
        else:
            labels.append('Low')

    y = np.array(labels)
    return X, y

def train_and_save_model():
    print("Generating synthetic disaster environmental dataset...")
    X, y = generate_synthetic_disaster_dataset(2000)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    print("Training RandomForestClassifier model...")
    model = RandomForestClassifier(n_estimators=100, random_state=42, max_depth=12)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Model Training Complete! Accuracy: {accuracy * 100:.2f}%")
    print(classification_report(y_test, y_pred))

    # Ensure output folder exists
    output_dir = os.path.join(os.path.dirname(__file__), 'static', 'model')
    os.makedirs(output_dir, exist_ok=True)
    
    model_path = os.path.join(output_dir, 'disaster_model.joblib')
    joblib.dump(model, model_path)
    print(f"Model saved successfully to: {model_path}")


if __name__ == '__main__':
    train_and_save_model()

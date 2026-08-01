import os
import joblib
import numpy as np

class DisasterPredictor:
    """
    AI Machine Learning Disaster Risk Inference Engine.
    Loads trained scikit-learn model and computes risk levels & recommendations.
    """
    def __init__(self, model_path=None):
        self.model_path = model_path
        self.model = None
        self.load_model()

    def load_model(self):
        """Loads serialized Scikit-learn Random Forest model if available."""
        if self.model_path and os.path.exists(self.model_path):
            try:
                self.model = joblib.load(self.model_path)
            except Exception as e:
                print(f"[Warning] Could not load ML model from {self.model_path}: {e}")
                self.model = None

    def predict(self, rainfall, river_level, wind_speed, temperature, humidity, earthquake_mag):
        """
        Executes prediction based on environmental features:
        - rainfall (mm)
        - river_level (m)
        - wind_speed (km/h)
        - temperature (°C)
        - humidity (%)
        - earthquake_mag (Richter scale)

        Returns dict with: risk_level, risk_score (0-100), probabilities, recommendations.
        """
        features = np.array([[rainfall, river_level, wind_speed, temperature, humidity, earthquake_mag]])

        if self.model is not None:
            try:
                # Use Scikit-Learn trained model
                prediction = self.model.predict(features)[0] # 'Low', 'Medium', 'High'
                probs = self.model.predict_proba(features)[0] # class probabilities
                classes = list(self.model.classes_)
                
                high_idx = classes.index('High') if 'High' in classes else -1
                med_idx = classes.index('Medium') if 'Medium' in classes else -1

                high_prob = probs[high_idx] if high_idx != -1 else 0
                med_prob = probs[med_idx] if med_idx != -1 else 0

                risk_score = round(float((high_prob * 1.0 + med_prob * 0.5) * 100), 1)
                risk_level = str(prediction)
            except Exception as e:
                print(f"[Fallback AI] ML inference error: {e}")
                risk_level, risk_score = self._heuristic_prediction(rainfall, river_level, wind_speed, temperature, humidity, earthquake_mag)
        else:
            # Fallback heuristic calculation if .joblib file not trained yet
            risk_level, risk_score = self._heuristic_prediction(rainfall, river_level, wind_speed, temperature, humidity, earthquake_mag)

        recommendations = self._generate_recommendations(risk_level, rainfall, river_level, wind_speed, earthquake_mag)

        return {
            'risk_level': risk_level,
            'risk_score': risk_score,
            'recommendations': recommendations
        }

    def _heuristic_prediction(self, rainfall, river_level, wind_speed, temperature, humidity, earthquake_mag):
        """
        Domain heuristic rule engine used for immediate calculation or validation.
        """
        score = 0.0
        # Rainfall & River level contribution
        if rainfall > 150 or river_level > 7.5:
            score += 45
        elif rainfall > 80 or river_level > 5.0:
            score += 25

        # Wind speed contribution
        if wind_speed > 90:
            score += 35
        elif wind_speed > 60:
            score += 20

        # Earthquake magnitude contribution
        if earthquake_mag > 5.5:
            score += 50
        elif earthquake_mag > 4.0:
            score += 25

        # Extreme Heat contribution
        if temperature > 42 and humidity < 25:
            score += 15

        score = min(100.0, score)

        if score >= 60 or earthquake_mag >= 5.5 or (rainfall > 180 and river_level > 8.0):
            risk_level = 'High'
        elif score >= 30:
            risk_level = 'Medium'
        else:
            risk_level = 'Low'

        return risk_level, round(score, 1)

    def _generate_recommendations(self, risk_level, rainfall, river_level, wind_speed, earthquake_mag):
        """Generates contextual safety recommendations based on predicted risk."""
        recs = []
        if risk_level == 'High':
            recs.append("CRITICAL: Evacuate low-lying areas and move to nearest designated relief shelter immediately.")
            recs.append("Keep emergency SOS device charged and pack essential medications, documents, and water.")
            if earthquake_mag > 4.5:
                recs.append("Drop, Cover, and Hold On! Stay away from heavy infrastructure and electric lines.")
            if rainfall > 100 or river_level > 6.0:
                recs.append("Do NOT attempt to walk, swim, or drive through flooded roads or rivers.")
            if wind_speed > 70:
                recs.append("Secure all roof items, shut window shutters, and avoid trees or metal poles.")
        elif risk_level == 'Medium':
            recs.append("MODERATE RISK: Prepare emergency survival kit (water, canned food, flashlight, battery bank).")
            recs.append("Monitor official weather warning broadcasts continuously.")
            recs.append("Identify nearest emergency shelter location and check bed availability.")
            if wind_speed > 50:
                recs.append("Avoid unnecessary outdoor travel during high wind advisories.")
        else:
            recs.append("LOW RISK: Normal conditions observed. Maintain general disaster preparedness.")
            recs.append("Verify home emergency kit readiness and store local helpline numbers.")

        return recs

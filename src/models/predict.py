"""
Fraud Prediction Module
Loads trained models and provides prediction functionality
"""

import numpy as np
import pandas as pd
import joblib
import os


class FraudPredictor:
    """Real-time fraud prediction"""
    
    def __init__(self, model_dir='models', model_type='random_forest'):
        """
        Initialize predictor
        
        Args:
            model_dir: Directory containing saved models
            model_type: 'random_forest', 'xgboost', or 'isolation_forest'
        """
        self.model_dir = model_dir
        self.model_type = model_type
        self.model = None
        self.scaler = None
        self.feature_names = None
        self.load_model()
    
    def load_model(self):
        """Load the trained model and scaler"""
        try:
            model_path = os.path.join(self.model_dir, f'{self.model_type}.joblib')
            scaler_path = os.path.join(self.model_dir, 'scaler.joblib')
            feature_path = os.path.join(self.model_dir, 'feature_names.joblib')
            
            self.model = joblib.load(model_path)
            self.scaler = joblib.load(scaler_path)
            self.feature_names = joblib.load(feature_path)
            
            print(f"✅ Loaded {self.model_type} model successfully")
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            raise
    
    def predict(self, transaction_data):
        """
        Predict fraud probability for a transaction
        
        Args:
            transaction_data: Dict with transaction features
        
        Returns:
            Dict with prediction results
        """
        try:
            # Convert to DataFrame
            features_df = pd.DataFrame([transaction_data])
            
            # Ensure correct feature order
            features_df = features_df[self.feature_names]
            
            # Get prediction
            if self.model_type == 'isolation_forest':
                # Isolation Forest returns -1 for anomaly, 1 for normal
                prediction = self.model.predict(features_df)[0]
                is_fraud = 1 if prediction == -1 else 0
                
                # Get anomaly score
                anomaly_score = self.model.score_samples(features_df)[0]
                fraud_probability = 1 / (1 + np.exp(anomaly_score))
            else:
                # Classification models
                is_fraud = self.model.predict(features_df)[0]
                fraud_probability = self.model.predict_proba(features_df)[0][1]
            
            # Determine risk level
            if fraud_probability >= 0.8:
                risk_level = "HIGH"
                decision = "BLOCK"
                color = "red"
            elif fraud_probability >= 0.5:
                risk_level = "MEDIUM"
                decision = "WARN"
                color = "orange"
            else:
                risk_level = "LOW"
                decision = "ALLOW"
                color = "green"
            
            # Get explanation
            explanation = self._explain_prediction(transaction_data, fraud_probability)
            
            return {
                'is_fraud': int(is_fraud),
                'fraud_probability': float(fraud_probability),
                'risk_level': risk_level,
                'decision': decision,
                'color': color,
                'explanation': explanation
            }
        
        except Exception as e:
            print(f"❌ Prediction error: {e}")
            raise
    
    def _explain_prediction(self, transaction_data, fraud_probability):
        """Generate human-readable explanation"""
        reasons = []
        
        # Check amount
        if transaction_data['amount'] > 20000:
            reasons.append(f"High transaction amount (₹{transaction_data['amount']:.2f})")
        
        # Check time
        time_mapping = {0: 'Morning', 1: 'Afternoon', 2: 'Evening', 3: 'Night'}
        time_name = time_mapping[transaction_data['time_slot']]
        if transaction_data['time_slot'] == 3:
            reasons.append(f"Transaction at night ({time_name})")
        
        # Check device
        if transaction_data['is_new_device'] == 1:
            reasons.append("New device detected")
        
        # Check beneficiary
        if transaction_data['is_new_beneficiary'] == 1:
            reasons.append("New beneficiary")
        
        # Check location
        if transaction_data['location_change'] == 1:
            reasons.append("Location change detected")
        
        # Check frequency
        if transaction_data['transaction_frequency'] > 10:
            reasons.append(f"High transaction frequency ({transaction_data['transaction_frequency']} in 24h)")
        
        # Check past fraud
        if transaction_data['past_fraud_flag'] == 1:
            reasons.append("Past fraud activity detected")
        
        # Check amount deviation
        if transaction_data['amount_deviation'] > 0.7:
            reasons.append(f"Amount deviates from user pattern ({transaction_data['amount_deviation']:.2f})")
        
        # Check trust score
        if transaction_data['beneficiary_trust_score'] < 0.4:
            reasons.append(f"Low beneficiary trust score ({transaction_data['beneficiary_trust_score']:.2f})")
        
        # Check device age
        if transaction_data['device_age_days'] < 7:
            reasons.append(f"Very new device ({transaction_data['device_age_days']} days old)")
        
        if not reasons:
            return "Transaction appears normal based on user patterns"
        
        return " | ".join(reasons)
    
    def predict_batch(self, transactions):
        """Predict multiple transactions"""
        results = []
        for txn in transactions:
            result = self.predict(txn)
            results.append(result)
        return results


def get_feature_template():
    """Return template for transaction features"""
    return {
        'amount': 0.0,
        'time_slot': 0,  # 0=Morning, 1=Afternoon, 2=Evening, 3=Night
        'is_new_device': 0,
        'is_new_beneficiary': 0,
        'location_change': 0,
        'transaction_frequency': 0,
        'past_fraud_flag': 0,
        'amount_deviation': 0.0,
        'beneficiary_trust_score': 0.5,
        'device_age_days': 100,
        'account_age_days': 365
    }


if __name__ == "__main__":
    # Example usage
    predictor = FraudPredictor(model_type='random_forest')
    
    # Test transaction
    test_txn = {
        'amount': 45000,
        'time_slot': 3,  # Night
        'is_new_device': 1,
        'is_new_beneficiary': 1,
        'location_change': 1,
        'transaction_frequency': 15,
        'past_fraud_flag': 0,
        'amount_deviation': 1.2,
        'beneficiary_trust_score': 0.1,
        'device_age_days': 0,
        'account_age_days': 200
    }
    
    result = predictor.predict(test_txn)
    print("\n🔍 Prediction Result:")
    print(f"  Fraud Probability: {result['fraud_probability']:.2%}")
    print(f"  Risk Level: {result['risk_level']}")
    print(f"  Decision: {result['decision']}")
    print(f"  Explanation: {result['explanation']}")

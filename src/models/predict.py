"""
Fraud Prediction Module
Loads trained models and provides prediction functionality
"""

import numpy as np
import pandas as pd
import joblib
import os
import json
from datetime import datetime


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
        
        # Create logs directory
        os.makedirs('logs', exist_ok=True)
        self.log_file = 'logs/predictions.log'
        
        # Transaction history for pattern detection (in-memory for demo)
        self.transaction_history = []
        self.max_history_size = 100
        
        self.load_model()
    
    def load_model(self):
        """Load the trained model"""
        try:
            model_path = os.path.join(self.model_dir, f'{self.model_type}.joblib')
            feature_path = os.path.join(self.model_dir, 'feature_names.joblib')
            
            self.model = joblib.load(model_path)
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
            # Store device_id separately (not a model feature)
            device_id_str = transaction_data.pop('device_id', 'DEV12345')
            
            # Add default values for missing features (20 base features)
            default_features = {
                'is_small_verification': 0,
                'is_first_time_user': 0,
                'beneficiary_change_velocity': 1,
                'is_rural_user': 0,
                'rapid_transactions_1h': 0,
                'upi_pin_failed_attempts': 0,
                'account_reports': 0,
                'location': 0,  # Encoded location
                'device_id': 1234,  # Encoded device_id (numeric for model)
                'payee_balance_before': 10000.0,
                'payee_balance_after': 0.0,
            }
            
            # Merge with provided data (provided data takes precedence)
            full_data = {**default_features, **transaction_data}
            
            # Calculate balance after if not provided
            if 'amount' in full_data and full_data['payee_balance_after'] == 0.0:
                full_data['payee_balance_after'] = full_data['payee_balance_before'] - full_data['amount']
            
            # ADD HYPER-AGGRESSIVE RISK FEATURES (must match training exactly)
            full_data['night_risk'] = (1 if full_data.get('time_slot', 0) >= 2 else 0) * 4  # Increased
            full_data['new_device_risk'] = full_data.get('is_new_device', 0) * 5  # Increased
            full_data['high_amount_risk'] = (1 if full_data.get('amount', 0) > 20000 else 0) * 3  # Increased
            full_data['suspicious_combo'] = (
                1 if (
                    full_data.get('time_slot', 0) >= 2 and 
                    full_data.get('is_new_device', 0) == 1 and 
                    full_data.get('amount', 0) > 15000
                ) else 0
            ) * 8  # Increased
            full_data['low_trust_risk'] = (1 if full_data.get('beneficiary_trust_score', 1.0) < 0.3 else 0) * 3  # Increased
            full_data['rapid_trans_risk'] = (1 if full_data.get('rapid_transactions_1h', 0) > 10 else 0) * 3  # Increased
            full_data['pin_failure_risk'] = (1 if full_data.get('upi_pin_failed_attempts', 0) > 0 else 0) * 3  # Increased
            full_data['velocity_risk'] = (1 if full_data.get('beneficiary_change_velocity', 0) > 5 else 0) * 2  # New
            
            # Convert to DataFrame
            features_df = pd.DataFrame([full_data])
            
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
            
            # Determine risk level with adjusted thresholds
            if fraud_probability >= 0.55:  # Lowered from 0.8 to 0.55
                risk_level = "HIGH"
                decision = "BLOCK"
                color = "red"
            elif fraud_probability >= 0.3:  # Lowered from 0.5 to 0.3
                risk_level = "MEDIUM"
                decision = "WARN"
                color = "orange"
            else:
                risk_level = "LOW"
                decision = "ALLOW"
                color = "green"
            
            # Get explanation
            explanation = self._explain_prediction(transaction_data, fraud_probability)
            
            # Classify fraud type
            fraud_type = self.classify_fraud_type(transaction_data, fraud_probability)
            
            # Calculate vulnerability score
            vulnerability_score = self.calculate_vulnerability_score(transaction_data)
            
            # Detect specific patterns (pass device_id_str separately)
            rapid_switching_detected, rapid_switching_score, rapid_switching_details = self.detect_rapid_switching(transaction_data)
            vulnerable_night_detected, vulnerable_night_score, vulnerable_night_details = self.detect_vulnerable_user_night(transaction_data)
            
            # Pass device_id separately for verification attack
            transaction_with_device = {**transaction_data, 'device_id': device_id_str}
            verification_attack_detected, verification_attack_score, verification_attack_details = self.detect_verification_attack(transaction_with_device)
            
            # Collect pattern alerts
            pattern_alerts = []
            if verification_attack_detected:
                pattern_alerts.append({
                    'pattern': 'verification_attack',
                    'severity': 'CRITICAL' if verification_attack_score >= 90 else 'HIGH',
                    'score': verification_attack_score,
                    'details': verification_attack_details
                })
            if rapid_switching_detected:
                pattern_alerts.append({
                    'pattern': 'rapid_switching',
                    'severity': 'HIGH' if rapid_switching_score >= 70 else 'MEDIUM',
                    'score': rapid_switching_score,
                    'details': rapid_switching_details
                })
            if vulnerable_night_detected:
                pattern_alerts.append({
                    'pattern': 'vulnerable_user_night',
                    'severity': 'CRITICAL' if vulnerable_night_score >= 80 else 'HIGH',
                    'score': vulnerable_night_score,
                    'details': vulnerable_night_details
                })
            
            # Get balance changes
            balance_change = {
                'payee_before': transaction_data.get('payee_balance_before', 0),
                'payee_after': transaction_data.get('payee_balance_after', 0),
                'beneficiary_before': transaction_data.get('beneficiary_balance_before', 0),
                'beneficiary_after': transaction_data.get('beneficiary_balance_after', 0),
                'payee_impact': transaction_data.get('payee_balance_before', 0) - transaction_data.get('payee_balance_after', 0),
                'beneficiary_gain': transaction_data.get('beneficiary_balance_after', 0) - transaction_data.get('beneficiary_balance_before', 0)
            }
            
            result = {
                'is_fraud': int(is_fraud),
                'fraud_probability': float(fraud_probability),
                'risk_level': risk_level,
                'decision': decision,
                'color': color,
                'explanation': explanation,
                'fraud_type': fraud_type,
                'vulnerability_score': vulnerability_score,
                'pattern_alerts': pattern_alerts,
                'balance_changes': balance_change,
                'location': transaction_data.get('location', 'Unknown'),
                'device_id': device_id_str
            }
            
            # Add to history for future pattern detection
            self.add_to_history(transaction_with_device)
            
            # Log prediction
            self._log_prediction(transaction_data, result)
            
            return result
        
        except Exception as e:
            print(f"❌ Prediction error: {e}")
            raise
    
    def _log_prediction(self, input_data, result):
        """Log prediction details to file"""
        try:
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'input': {k: v for k, v in input_data.items() if k in ['amount', 'time_slot', 'is_new_device', 'is_new_beneficiary', 'transaction_frequency', 'past_fraud_flag']},
                'prediction': {
                    'fraud_probability': result['fraud_probability'],
                    'risk_level': result['risk_level'],
                    'decision': result['decision'],
                    'fraud_type': result['fraud_type']
                }
            }
            
            with open(self.log_file, 'a') as f:
                f.write(json.dumps(log_entry) + '\n')
        except Exception as e:
            print(f"⚠️ Logging failed: {e}")
    
    def classify_fraud_type(self, transaction_data, fraud_probability):
        """Classify the type of fraud based on transaction patterns"""
        if fraud_probability < 0.5:
            return 'legitimate'
        
        score_high_amount = 0
        score_new_device = 0
        score_night_rush = 0
        score_multiple_new = 0
        
        # High amount fraud indicators
        if transaction_data.get('amount', 0) > 10000:
            score_high_amount += 3
        if transaction_data.get('amount_deviation', 0) > 0.7:
            score_high_amount += 2
        if transaction_data.get('upi_pin_failed_attempts', 0) > 0:
            score_high_amount += 2
        
        # New device fraud indicators
        if transaction_data.get('is_new_device', 0) == 1:
            score_new_device += 4
        if transaction_data.get('device_age_days', 999) < 30:
            score_new_device += 2
        if transaction_data.get('is_small_verification', 0) == 1:
            score_new_device += 3
        
        # Night rush fraud indicators
        if transaction_data.get('time_slot', 0) == 3:
            score_night_rush += 3
        if transaction_data.get('rapid_transactions_1h', 0) > 5:
            score_night_rush += 4
        if transaction_data.get('transaction_frequency', 0) > 10:
            score_night_rush += 2
        
        # Multiple new beneficiary fraud indicators
        if transaction_data.get('is_new_beneficiary', 0) == 1:
            score_multiple_new += 3
        if transaction_data.get('beneficiary_change_velocity', 0) > 5:
            score_multiple_new += 4
        if transaction_data.get('beneficiary_trust_score', 1) < 0.3:
            score_multiple_new += 2
        
        # Return fraud type with highest score
        scores = {
            'high_amount': score_high_amount,
            'new_device': score_new_device,
            'night_rush': score_night_rush,
            'multiple_new': score_multiple_new
        }
        
        return max(scores, key=scores.get)
    
    def detect_rapid_switching(self, transaction_data):
        """
        Detect rapid beneficiary switching pattern
        Returns: (is_detected: bool, risk_score: int, details: str)
        """
        beneficiary_velocity = transaction_data.get('beneficiary_change_velocity', 0)
        is_new_beneficiary = transaction_data.get('is_new_beneficiary', 0)
        trust_score = transaction_data.get('beneficiary_trust_score', 1.0)
        
        risk_score = 0
        details = []
        
        # Check velocity threshold
        if beneficiary_velocity > 5:
            risk_score += 40
            details.append(f"High velocity: {beneficiary_velocity} beneficiary changes")
        elif beneficiary_velocity > 3:
            risk_score += 20
            details.append(f"Moderate velocity: {beneficiary_velocity} beneficiary changes")
        
        # Check if current is new beneficiary
        if is_new_beneficiary == 1:
            risk_score += 25
            details.append("Current transaction to new beneficiary")
        
        # Check trust score
        if trust_score < 0.3:
            risk_score += 35
            details.append(f"Very low trust score: {trust_score:.2f}")
        elif trust_score < 0.5:
            risk_score += 20
            details.append(f"Low trust score: {trust_score:.2f}")
        
        # Pattern detected if risk_score >= 50
        is_detected = risk_score >= 50
        
        if is_detected:
            return True, risk_score, " | ".join(details)
        else:
            return False, risk_score, "No rapid switching pattern detected"
    
    def detect_vulnerable_user_night(self, transaction_data):
        """
        Detect vulnerable user (rural/first-time) making night transactions
        Returns: (is_detected: bool, risk_score: int, details: str)
        """
        is_rural = transaction_data.get('is_rural_user', 0)
        is_first_time = transaction_data.get('is_first_time_user', 0)
        account_age = transaction_data.get('account_age_days', 999)
        time_slot = transaction_data.get('time_slot', 0)
        amount = transaction_data.get('amount', 0)
        
        risk_score = 0
        details = []
        vulnerability_factors = []
        
        # Check user vulnerability
        if is_rural == 1:
            risk_score += 25
            vulnerability_factors.append("Rural user (low digital literacy)")
        
        if is_first_time == 1 or account_age < 30:
            risk_score += 30
            vulnerability_factors.append(f"New user (account age: {account_age} days)")
        elif account_age < 90:
            risk_score += 15
            vulnerability_factors.append(f"Recent user (account age: {account_age} days)")
        
        # Check time slot (Night = 3, Late Night = 4)
        if time_slot >= 3:
            time_name = "Late Night" if time_slot == 4 else "Night"
            risk_score += 30
            details.append(f"Transaction at {time_name} (exploiting vulnerable hours)")
        
        # Check amount
        if amount > 20000:
            risk_score += 25
            details.append(f"High amount: ₹{amount:,.0f}")
        elif amount > 10000:
            risk_score += 15
            details.append(f"Significant amount: ₹{amount:,.0f}")
        
        # Combine vulnerability factors
        if vulnerability_factors:
            details.insert(0, " + ".join(vulnerability_factors))
        
        # Pattern detected if:
        # 1. User is vulnerable (rural OR first-time)
        # 2. Transaction is at night
        # 3. Amount is significant
        is_vulnerable = (is_rural == 1 or is_first_time == 1 or account_age < 90)
        is_night = time_slot >= 3
        is_significant_amount = amount > 10000
        
        is_detected = is_vulnerable and is_night and is_significant_amount
        
        if is_detected:
            return True, risk_score, " | ".join(details)
        else:
            return False, risk_score, "No vulnerable user night pattern detected"
    
    def detect_verification_attack(self, transaction_data):
        """
        Detect verification attack: small test transaction followed by large fraud
        Pattern: ₹1-10 test → ₹20k+ fraud within 5-10 minutes
        Returns: (is_detected: bool, risk_score: int, details: str)
        """
        current_amount = transaction_data.get('amount', 0)
        device_id = transaction_data.get('device_id', 'unknown')
        is_new_device = transaction_data.get('is_new_device', 0)
        
        risk_score = 0
        details = []
        
        # Check if current transaction is large
        is_large_transaction = current_amount > 20000
        
        # Look for small verification transaction in history (same device, within last 10 mins)
        found_verification = False
        verification_amount = 0
        
        for hist_txn in reversed(self.transaction_history[-20:]):  # Check last 20 transactions
            # Same device check
            if hist_txn.get('device_id') == device_id:
                hist_amount = hist_txn.get('amount', 0)
                
                # Found small transaction (₹1-10)
                if hist_amount <= 10:
                    found_verification = True
                    verification_amount = hist_amount
                    break
        
        # Pattern detected: small test + large current
        if found_verification and is_large_transaction:
            risk_score = 95  # Critical pattern
            details.append(f"Test transaction of ₹{verification_amount:.0f} detected")
            details.append(f"Followed by large transaction: ₹{current_amount:,.0f}")
            details.append("Classic verification attack pattern")
            
            if is_new_device == 1:
                risk_score = 100
                details.append("New device used - credential compromise likely")
            
            return True, risk_score, " | ".join(details)
        
        # Check if current is small (potential verification)
        elif current_amount <= 10 and is_new_device == 1:
            risk_score = 60
            details.append(f"Small amount (₹{current_amount:.0f}) from new device")
            details.append("Possible verification attempt - monitor next transaction")
            return True, risk_score, " | ".join(details)
        
        return False, 0, "No verification attack pattern detected"
    
    def add_to_history(self, transaction_data):
        """Add transaction to history for pattern detection"""
        # Keep only essential fields for history
        hist_entry = {
            'amount': transaction_data.get('amount', 0),
            'device_id': transaction_data.get('device_id', 'unknown'),
            'timestamp': datetime.now().isoformat(),
            'is_new_device': transaction_data.get('is_new_device', 0)
        }
        
        self.transaction_history.append(hist_entry)
        
        # Keep history size manageable
        if len(self.transaction_history) > self.max_history_size:
            self.transaction_history.pop(0)
    
    def calculate_vulnerability_score(self, transaction_data):
        """Calculate vulnerability score (0-100) based on risk factors"""
        vulnerability = 0
        max_score = 100
        
        # Account age vulnerability (20 points)
        account_age = transaction_data.get('account_age_days', 365)
        if account_age < 30:
            vulnerability += 20
        elif account_age < 90:
            vulnerability += 15
        elif account_age < 180:
            vulnerability += 10
        elif account_age < 365:
            vulnerability += 5
        
        # Device trust (15 points)
        device_age = transaction_data.get('device_age_days', 180)
        if device_age < 7:
            vulnerability += 15
        elif device_age < 30:
            vulnerability += 10
        elif device_age < 90:
            vulnerability += 5
        
        # Behavioral patterns (25 points)
        if transaction_data.get('rapid_transactions_1h', 0) > 5:
            vulnerability += 10
        if transaction_data.get('upi_pin_failed_attempts', 0) > 0:
            vulnerability += 15
        
        # Account reputation (20 points)
        if transaction_data.get('account_reports', 0) > 0:
            vulnerability += 15
        if transaction_data.get('past_fraud_flag', 0) == 1:
            vulnerability += 5
        
        # Beneficiary trust (10 points)
        trust_score = transaction_data.get('beneficiary_trust_score', 0.5)
        vulnerability += int((1 - trust_score) * 10)
        
        # Location risk (10 points)
        if transaction_data.get('is_rural_user', 0) == 1:
            vulnerability += 5
        if transaction_data.get('location_change', 0) == 1:
            vulnerability += 5
        
        return min(vulnerability, max_score)
    
    def _explain_prediction(self, transaction_data, fraud_probability):
        """Generate human-readable explanation with enhanced features"""
        reasons = []
        
        # Check amount
        if transaction_data['amount'] > 20000:
            reasons.append(f"High transaction amount (₹{transaction_data['amount']:.2f})")
        
        # Check time
        time_mapping = {0: 'Morning', 1: 'Afternoon', 2: 'Evening', 3: 'Night', 4: 'Late Night'}
        time_name = time_mapping.get(transaction_data['time_slot'], 'Unknown')
        if transaction_data['time_slot'] >= 3:
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
        if transaction_data.get('device_age_days', 999) < 7:
            reasons.append(f"Very new device ({transaction_data['device_age_days']} days old)")
        
        # Check small verification
        if transaction_data.get('is_small_verification', 0) == 1:
            reasons.append("Small verification transaction detected (possible precursor to fraud)")
        
        # Check PIN failures
        if transaction_data.get('upi_pin_failed_attempts', 0) > 0:
            reasons.append(f"{transaction_data['upi_pin_failed_attempts']} failed PIN attempts")
        
        # Check rapid transactions
        if transaction_data.get('rapid_transactions_1h', 0) > 5:
            reasons.append(f"Rapid transactions: {transaction_data['rapid_transactions_1h']} in last hour")
        
        # Check account reports
        if transaction_data.get('account_reports', 0) > 0:
            reasons.append("Account has been reported for suspicious activity")
        
        # Check beneficiary velocity
        if transaction_data.get('beneficiary_change_velocity', 0) > 10:
            reasons.append(f"High beneficiary changes ({transaction_data['beneficiary_change_velocity']})")
        
        # Check first time user
        if transaction_data.get('is_first_time_user', 0) == 1:
            reasons.append("First-time user")
        
        # Check rural location
        if transaction_data.get('is_rural_user', 0) == 1:
            reasons.append(f"Transaction from rural area ({transaction_data.get('location', 'Unknown')})")
        
        if not reasons:
            return "Transaction appears normal based on user patterns and behavioral analysis"
        
        return " | ".join(reasons)
    
    def predict_batch(self, transactions):
        """Predict multiple transactions"""
        results = []
        for txn in transactions:
            result = self.predict(txn)
            results.append(result)
        return results


def get_feature_template():
    """Return template for transaction features (24 input features)"""
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
        'account_age_days': 365,
        'is_small_verification': 0,
        'is_first_time_user': 0,
        'beneficiary_change_velocity': 0,
        'is_rural_user': 0,
        'rapid_transactions_1h': 0,
        'upi_pin_failed_attempts': 0,
        'account_reports': 0,
        'location': 'Mumbai',
        'device_id': 'DEV00000',
        'payee_balance_before': 10000.0,
        'payee_balance_after': 10000.0,
        'beneficiary_balance_before': 5000.0,
        'beneficiary_balance_after': 5000.0
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

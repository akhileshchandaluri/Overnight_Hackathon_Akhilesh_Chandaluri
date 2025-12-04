"""
Train an AGGRESSIVE fraud detection model with enhanced fraud signals
"""
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import joblib

# Load dataset
df = pd.read_csv("data/raw/upi_transactions.csv")

# Select features
selected_features = [
    "amount", "time_slot", "is_new_device",
    "location_change", "transaction_frequency",
    "past_fraud_flag", "amount_deviation",
    "beneficiary_trust_score", "account_age_days",
    "is_small_verification", "is_first_time_user",
    "beneficiary_change_velocity", "is_rural_user",
    "rapid_transactions_1h", "upi_pin_failed_attempts",
    "account_reports", "location", "device_id",
    "payee_balance_before", "payee_balance_after",
]

# Encode categorical
from sklearn.preprocessing import LabelEncoder
label_cols = ["location", "device_id"]
encoders = {}

for col in label_cols:
    encoders[col] = LabelEncoder()
    df[col] = encoders[col].fit_transform(df[col].astype(str))

# CREATE HYPER-AGGRESSIVE FEATURES - Maximum sensitivity
df['night_risk'] = (df['time_slot'] >= 2).astype(int) * 4  # Night = 4x risk (increased)
df['new_device_risk'] = df['is_new_device'] * 5  # New device = 5x risk (increased)
df['high_amount_risk'] = (df['amount'] > 20000).astype(int) * 3  # High amount = 3x risk (increased)
df['suspicious_combo'] = (
    (df['time_slot'] >= 2) & 
    (df['is_new_device'] == 1) & 
    (df['amount'] > 15000)
).astype(int) * 8  # Deadly combo = 8x risk (increased)

df['low_trust_risk'] = (df['beneficiary_trust_score'] < 0.3).astype(int) * 3  # Increased
df['rapid_trans_risk'] = (df['rapid_transactions_1h'] > 10).astype(int) * 3  # Increased
df['pin_failure_risk'] = (df['upi_pin_failed_attempts'] > 0).astype(int) * 3  # Increased
df['velocity_risk'] = (df['beneficiary_change_velocity'] > 5).astype(int) * 2  # New feature

# Add all risk features
risk_features = [
    'night_risk', 'new_device_risk', 'high_amount_risk', 
    'suspicious_combo', 'low_trust_risk', 'rapid_trans_risk', 
    'pin_failure_risk', 'velocity_risk'  # Added new feature
]

all_features = selected_features + risk_features

X = df[all_features]
y = df["is_fraud"]

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

print(f"Training samples: {len(X_train)}")
print(f"Fraud cases in training: {y_train.sum()} ({y_train.sum()/len(y_train)*100:.1f}%)")
print(f"\nTraining AGGRESSIVE model with {len(all_features)} features...")

# Train with HYPER-AGGRESSIVE parameters that favor fraud detection
model = RandomForestClassifier(
    n_estimators=400,  # More trees for better stability
    max_depth=25,  # Even deeper trees
    min_samples_split=2,  # Allow maximum splitting
    min_samples_leaf=1,  # Allow pure leaves (most aggressive)
    class_weight={0: 1, 1: 6},  # 6x weight to fraud class (HYPER-AGGRESSIVE)
    random_state=42,
    max_features='sqrt',
    n_jobs=-1
)

model.fit(X_train, y_train)

# Evaluate
y_pred = model.predict(X_test)
y_proba = model.predict_proba(X_test)

print(f"\n{'='*60}")
print("MODEL PERFORMANCE")
print(f"{'='*60}")
print(f"Accuracy: {accuracy_score(y_test, y_pred):.4f}")

print("\nClassification Report:")
print(classification_report(y_test, y_pred, target_names=['Legitimate', 'Fraud']))

print("\nConfusion Matrix:")
cm = confusion_matrix(y_test, y_pred)
print(f"True Negatives (Legit→Legit): {cm[0][0]}")
print(f"False Positives (Legit→Fraud): {cm[0][1]}")
print(f"False Negatives (Fraud→Legit): {cm[1][0]}")  
print(f"True Positives (Fraud→Fraud): {cm[1][1]}")

# Feature importance
feature_importance = pd.DataFrame({
    'feature': all_features,
    'importance': model.feature_importances_
}).sort_values('importance', ascending=False)

print(f"\n{'='*60}")
print("TOP 10 MOST IMPORTANT FEATURES")
print(f"{'='*60}")
for idx, row in feature_importance.head(10).iterrows():
    print(f"{row['feature']:35s}: {row['importance']:.4f}")

# Test aggressive behavior
print(f"\n{'='*60}")
print("TESTING AGGRESSIVE DETECTION")
print(f"{'='*60}")

test_cases = [
    {
        'name': 'High Amount Night + New Device',
        'data': {'amount': 45000, 'time_slot': 3, 'is_new_device': 1}
    },
    {
        'name': 'Medium Amount Night',
        'data': {'amount': 25000, 'time_slot': 3, 'is_new_device': 0}
    },
    {
        'name': 'High Amount Day',
        'data': {'amount': 45000, 'time_slot': 1, 'is_new_device': 0}
    },
    {
        'name': 'Safe Transaction',
        'data': {'amount': 500, 'time_slot': 1, 'is_new_device': 0}
    }
]

for test in test_cases:
    # Create full feature vector with defaults
    test_features = {
        'amount': 5000, 'time_slot': 1, 'is_new_device': 0,
        'location_change': 0, 'transaction_frequency': 3,
        'past_fraud_flag': 0, 'amount_deviation': 0.5,
        'beneficiary_trust_score': 0.8, 'account_age_days': 365,
        'is_small_verification': 0, 'is_first_time_user': 0,
        'beneficiary_change_velocity': 1, 'is_rural_user': 0,
        'rapid_transactions_1h': 0, 'upi_pin_failed_attempts': 0,
        'account_reports': 0, 'location': 0, 'device_id': 0,
        'payee_balance_before': 50000, 'payee_balance_after': 45000,
    }
    
    # Update with test data
    test_features.update(test['data'])
    
    # Calculate risk features
    test_features['night_risk'] = (test_features['time_slot'] >= 2) * 2
    test_features['new_device_risk'] = test_features['is_new_device'] * 3
    test_features['high_amount_risk'] = (test_features['amount'] > 20000) * 2
    test_features['suspicious_combo'] = (
        (test_features['time_slot'] >= 2) and 
        (test_features['is_new_device'] == 1) and 
        (test_features['amount'] > 15000)
    ) * 5
    test_features['low_trust_risk'] = (test_features['beneficiary_trust_score'] < 0.3) * 2
    test_features['rapid_trans_risk'] = (test_features['rapid_transactions_1h'] > 10) * 2
    test_features['pin_failure_risk'] = (test_features['upi_pin_failed_attempts'] > 0) * 2
    
    test_df = pd.DataFrame([test_features])
    test_df = test_df[all_features]  # Ensure correct order
    
    pred_proba = model.predict_proba(test_df)[0][1]
    pred = model.predict(test_df)[0]
    
    print(f"\n{test['name']}")
    print(f"  Fraud Probability: {pred_proba*100:.1f}%")
    print(f"  Prediction: {'🔴 FRAUD' if pred == 1 else '🟢 LEGITIMATE'}")

# Save model
joblib.dump(model, 'models/random_forest.joblib')
joblib.dump(all_features, 'models/feature_names.joblib')

print(f"\n{'='*60}")
print(f"✅ AGGRESSIVE MODEL SAVED")
print(f"{'='*60}")
print(f"Total Features: {len(all_features)}")
print(f"Base Features: {len(selected_features)}")
print(f"Risk Features: {len(risk_features)}")
print("\nRisk multipliers applied:")
print("  - Night time (slot >= 2): 2x risk")
print("  - New device: 3x risk")
print("  - High amount (>20K): 2x risk")
print("  - Suspicious combo (night+new+high): 5x risk")
print("  - Low trust (<0.3): 2x risk")
print("  - Rapid transactions (>10): 2x risk")
print("  - PIN failures: 2x risk")

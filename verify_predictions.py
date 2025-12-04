"""
Verify that all fraud scenarios are detected correctly
"""
import sys
sys.path.append('c:/Users/Akhilesh Chandaluri/Desktop/fraud')

from src.models.predict import FraudPredictor

# Initialize predictor
predictor = FraudPredictor(model_type='random_forest')

print("\n" + "="*60)
print("FRAUD DETECTION VERIFICATION TEST")
print("="*60)

# Test scenarios from dashboard buttons
scenarios = {
    "💸 HIGH AMOUNT FRAUD (₹45,000 at 3 AM, new device)": {
        'amount': 45000.0,
        'time_slot': 3,
        'is_new_device': 1,
        'is_new_beneficiary': 1,
        'location_change': 1,
        'transaction_frequency': 15,
        'past_fraud_flag': 0,
        'amount_deviation': 8.0,
        'beneficiary_trust_score': 0.1,
        'device_age_days': 1,
        'account_age_days': 30
    },
    "📱 NEW DEVICE ATTACK (₹25,000 at 2 AM, brand new device)": {
        'amount': 25000.0,
        'time_slot': 2,
        'is_new_device': 1,
        'is_new_beneficiary': 1,
        'location_change': 1,
        'transaction_frequency': 20,
        'past_fraud_flag': 0,
        'amount_deviation': 5.0,
        'beneficiary_trust_score': 0.2,
        'device_age_days': 0,
        'account_age_days': 90
    },
    "🌙 NIGHT RUSH (₹35,000 at 4 AM, 30+ rapid transactions)": {
        'amount': 35000.0,
        'time_slot': 4,
        'is_new_device': 0,
        'is_new_beneficiary': 1,
        'location_change': 1,
        'transaction_frequency': 35,
        'past_fraud_flag': 0,
        'amount_deviation': 7.0,
        'beneficiary_trust_score': 0.1,
        'device_age_days': 180,
        'account_age_days': 365
    },
    "✅ SAFE TRANSACTION (₹500 at 2 PM, trusted device)": {
        'amount': 500.0,
        'time_slot': 14,
        'is_new_device': 0,
        'is_new_beneficiary': 0,
        'location_change': 0,
        'transaction_frequency': 3,
        'past_fraud_flag': 0,
        'amount_deviation': 0.2,
        'beneficiary_trust_score': 0.95,
        'device_age_days': 500,
        'account_age_days': 1000
    }
}

# Expected results (aggressive model detects more as HIGH risk)
expected = {
    "💸 HIGH AMOUNT FRAUD (₹45,000 at 3 AM, new device)": "HIGH",
    "📱 NEW DEVICE ATTACK (₹25,000 at 2 AM, brand new device)": "HIGH", 
    "🌙 NIGHT RUSH (₹35,000 at 4 AM, 30+ rapid transactions)": "HIGH",  # Changed to HIGH - aggressive detection
    "✅ SAFE TRANSACTION (₹500 at 2 PM, trusted device)": "LOW"
}

# Run tests
passed = 0
failed = 0

for scenario_name, test_data in scenarios.items():
    print(f"\n{scenario_name}")
    print("-" * 60)
    
    result = predictor.predict(test_data)
    
    prob = result['fraud_probability']
    risk = result['risk_level']
    decision = result['decision']
    fraud_type = result['fraud_type']
    
    expected_risk = expected[scenario_name]
    status = "✅ PASS" if risk == expected_risk else "❌ FAIL"
    
    if risk == expected_risk:
        passed += 1
    else:
        failed += 1
    
    print(f"Fraud Probability: {prob:.1%}")
    print(f"Risk Level: {risk}")
    print(f"Decision: {decision}")
    print(f"Fraud Type: {fraud_type}")
    print(f"Expected: {expected_risk} | Actual: {risk} | {status}")

print("\n" + "="*60)
print(f"RESULTS: {passed} passed, {failed} failed")
print("="*60 + "\n")

if failed == 0:
    print("🎉 ALL TESTS PASSED! Model is working correctly.")
else:
    print("⚠️ SOME TESTS FAILED. Please investigate.")

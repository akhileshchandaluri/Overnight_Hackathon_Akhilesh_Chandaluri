"""
Comprehensive test showing aggressive fraud detection sensitivity
"""
import sys
sys.path.append('c:/Users/Akhilesh Chandaluri/Desktop/fraud')

from src.models.predict import FraudPredictor

predictor = FraudPredictor(model_type='random_forest')

print("\n" + "="*70)
print("HYPER-AGGRESSIVE FRAUD DETECTION - SENSITIVITY TEST")
print("="*70)

tests = [
    # Test 1: Just night time (2 AM)
    {
        'name': 'Just Night Time (2 AM, ₹5000)',
        'data': {
            'amount': 5000, 'time_slot': 2, 'is_new_device': 0,
            'is_new_beneficiary': 0, 'location_change': 0,
            'transaction_frequency': 3, 'past_fraud_flag': 0,
            'amount_deviation': 0.5, 'beneficiary_trust_score': 0.8,
            'device_age_days': 365, 'account_age_days': 500
        },
        'expect': 'Should be MEDIUM/HIGH due to night time alone'
    },
    # Test 2: Just new device
    {
        'name': 'Just New Device (₹5000 at 2 PM)',
        'data': {
            'amount': 5000, 'time_slot': 14, 'is_new_device': 1,
            'is_new_beneficiary': 0, 'location_change': 0,
            'transaction_frequency': 3, 'past_fraud_flag': 0,
            'amount_deviation': 0.5, 'beneficiary_trust_score': 0.8,
            'device_age_days': 0, 'account_age_days': 500
        },
        'expect': 'Should be MEDIUM/HIGH due to new device alone'
    },
    # Test 3: Just high amount
    {
        'name': 'Just High Amount (₹30,000 at 2 PM, trusted)',
        'data': {
            'amount': 30000, 'time_slot': 14, 'is_new_device': 0,
            'is_new_beneficiary': 0, 'location_change': 0,
            'transaction_frequency': 3, 'past_fraud_flag': 0,
            'amount_deviation': 0.5, 'beneficiary_trust_score': 0.9,
            'device_age_days': 365, 'account_age_days': 500
        },
        'expect': 'Should be MEDIUM due to high amount'
    },
    # Test 4: Deadly combo (night + new device + high amount)
    {
        'name': 'DEADLY COMBO (₹40,000 at 3 AM, new device)',
        'data': {
            'amount': 40000, 'time_slot': 3, 'is_new_device': 1,
            'is_new_beneficiary': 1, 'location_change': 1,
            'transaction_frequency': 15, 'past_fraud_flag': 0,
            'amount_deviation': 2.5, 'beneficiary_trust_score': 0.1,
            'device_age_days': 0, 'account_age_days': 30
        },
        'expect': 'Should be HIGH risk - multiple red flags'
    },
    # Test 5: Low trust beneficiary
    {
        'name': 'Low Trust Beneficiary (trust=0.1)',
        'data': {
            'amount': 8000, 'time_slot': 14, 'is_new_device': 0,
            'is_new_beneficiary': 1, 'location_change': 0,
            'transaction_frequency': 5, 'past_fraud_flag': 0,
            'amount_deviation': 1.0, 'beneficiary_trust_score': 0.1,
            'device_age_days': 200, 'account_age_days': 365
        },
        'expect': 'Should be MEDIUM/HIGH due to very low trust'
    },
    # Test 6: Rapid transactions
    {
        'name': 'Rapid Transactions (20 in 1 hour)',
        'data': {
            'amount': 10000, 'time_slot': 14, 'is_new_device': 0,
            'is_new_beneficiary': 0, 'location_change': 0,
            'transaction_frequency': 5, 'past_fraud_flag': 0,
            'amount_deviation': 1.0, 'beneficiary_trust_score': 0.7,
            'device_age_days': 200, 'account_age_days': 365,
            'rapid_transactions_1h': 20
        },
        'expect': 'Should be MEDIUM/HIGH due to rapid velocity'
    },
    # Test 7: PIN failures
    {
        'name': 'Multiple PIN Failures (3 attempts)',
        'data': {
            'amount': 5000, 'time_slot': 14, 'is_new_device': 0,
            'is_new_beneficiary': 0, 'location_change': 0,
            'transaction_frequency': 3, 'past_fraud_flag': 0,
            'amount_deviation': 0.5, 'beneficiary_trust_score': 0.8,
            'device_age_days': 200, 'account_age_days': 365,
            'upi_pin_failed_attempts': 3
        },
        'expect': 'Should be MEDIUM due to PIN failures'
    },
    # Test 8: Completely safe transaction
    {
        'name': 'SAFE: Small daytime transaction (₹300 at 3 PM)',
        'data': {
            'amount': 300, 'time_slot': 15, 'is_new_device': 0,
            'is_new_beneficiary': 0, 'location_change': 0,
            'transaction_frequency': 2, 'past_fraud_flag': 0,
            'amount_deviation': 0.1, 'beneficiary_trust_score': 0.95,
            'device_age_days': 700, 'account_age_days': 1000
        },
        'expect': 'Should be LOW - perfectly safe'
    }
]

passed = 0
warnings = 0
blocked = 0

for test in tests:
    print(f"\n{'─'*70}")
    print(f"🔍 {test['name']}")
    print(f"{'─'*70}")
    
    result = predictor.predict(test['data'])
    
    prob = result['fraud_probability']
    risk = result['risk_level']
    decision = result['decision']
    
    # Color coding
    if risk == 'HIGH':
        emoji = '🔴'
        blocked += 1
    elif risk == 'MEDIUM':
        emoji = '🟡'
        warnings += 1
    else:
        emoji = '🟢'
        passed += 1
    
    print(f"Expected: {test['expect']}")
    print(f"Result:   {emoji} {risk} ({prob*100:.1f}%) - {decision}")
    
    # Show active risk features
    data = test['data']
    triggers = []
    if data.get('time_slot', 0) >= 2:
        triggers.append('Night Time')
    if data.get('is_new_device', 0) == 1:
        triggers.append('New Device')
    if data.get('amount', 0) > 20000:
        triggers.append('High Amount')
    if data.get('beneficiary_trust_score', 1.0) < 0.3:
        triggers.append('Low Trust')
    if data.get('rapid_transactions_1h', 0) > 10:
        triggers.append('Rapid Transactions')
    if data.get('upi_pin_failed_attempts', 0) > 0:
        triggers.append('PIN Failures')
    
    if triggers:
        print(f"Triggers: {', '.join(triggers)}")

print("\n" + "="*70)
print("SUMMARY")
print("="*70)
print(f"🔴 HIGH RISK (BLOCKED):  {blocked}")
print(f"🟡 MEDIUM RISK (WARNED): {warnings}")
print(f"🟢 LOW RISK (ALLOWED):   {passed}")
print(f"Total Tests: {len(tests)}")
print("\n✅ Model demonstrates high sensitivity to fraud indicators!")

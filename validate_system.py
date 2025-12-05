"""
Automated Validation Script for UPI Fraud Detection System
Tests message filter and transaction analysis
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from models.predict import FraudPredictor
from models.message_filter import MessageFilter

def test_message_filter():
    """Test message filter with various inputs"""
    print("\n" + "="*80)
    print("MESSAGE FILTER VALIDATION")
    print("="*80)
    
    mf = MessageFilter()
    
    test_cases = [
        {
            'name': 'HIGH RISK - OTP Phishing',
            'message': 'Dear customer, your account will be blocked. Share OTP immediately: bit.ly/verify',
            'expected_risk': 'HIGH',
            'should_block': True
        },
        {
            'name': 'HIGH RISK - Fake Refund',
            'message': 'Rs 45000 refund pending. Update KYC by clicking: tinyurl.com/refund. Enter CVV',
            'expected_risk': 'HIGH',
            'should_block': True
        },
        {
            'name': 'HIGH RISK - Lottery Scam',
            'message': 'CONGRATULATIONS! You won Rs 50 lakhs. Share OTP now: goo.gl/prize',
            'expected_risk': 'HIGH',
            'should_block': True
        },
        {
            'name': 'LOW RISK - Legitimate Transaction',
            'message': 'Payment successful. Rs 5000 credited to your account. Transaction ID: TXN123',
            'expected_risk': 'LOW',
            'should_block': False
        },
        {
            'name': 'NONE - Empty Message',
            'message': '',
            'expected_risk': 'NONE',
            'should_block': False
        }
    ]
    
    passed = 0
    failed = 0
    
    for tc in test_cases:
        print(f"\n📝 Test: {tc['name']}")
        print(f"Message: {tc['message'][:60]}..." if len(tc['message']) > 60 else f"Message: {tc['message']}")
        
        result = mf.analyze_message(tc['message'])
        
        print(f"   Risk Level: {result['risk_level']} (Expected: {tc['expected_risk']})")
        print(f"   Fraud Score: {result['fraud_score']}/100")
        print(f"   Can Proceed: {result['can_proceed']} (Expected: {not tc['should_block']})")
        
        # Validation
        risk_match = result['risk_level'] == tc['expected_risk']
        block_match = (not result['can_proceed']) == tc['should_block']
        
        if risk_match and block_match:
            print("   ✅ PASSED")
            passed += 1
        else:
            print("   ❌ FAILED")
            if not risk_match:
                print(f"      Risk mismatch: got {result['risk_level']}, expected {tc['expected_risk']}")
            if not block_match:
                print(f"      Block mismatch: got {not result['can_proceed']}, expected {tc['should_block']}")
            failed += 1
    
    print(f"\n{'='*80}")
    print(f"Message Filter Results: {passed} passed, {failed} failed")
    print(f"{'='*80}\n")
    
    return passed, failed


def test_transaction_analysis():
    """Test transaction fraud detection"""
    print("\n" + "="*80)
    print("TRANSACTION ANALYSIS VALIDATION")
    print("="*80)
    
    try:
        predictor = FraudPredictor(model_type='random_forest')
    except Exception as e:
        print(f"❌ Failed to load model: {e}")
        return 0, 1
    
    test_cases = [
        {
            'name': 'Safe Transaction - Tech-Savvy User',
            'data': {
                'amount': 3000.0,
                'time_slot': 1,
                'is_new_device': 0,
                'is_new_beneficiary': 0,
                'location_change': 0,
                'transaction_frequency': 5,
                'past_fraud_flag': 0,
                'amount_deviation': 0.3,
                'beneficiary_trust_score': 0.9,
                'device_age_days': 600,
                'account_age_days': 900,
                'is_rural_user': 0,
                'device_id': 'SAFE001'
            },
            'expected_risk': 'LOW',
            'expected_decision': 'ALLOW'
        },
        {
            'name': 'High Amount Fraud',
            'data': {
                'amount': 75000.0,
                'time_slot': 4,
                'is_new_device': 1,
                'is_new_beneficiary': 1,
                'location_change': 1,
                'transaction_frequency': 20,
                'past_fraud_flag': 0,
                'amount_deviation': 8.0,
                'beneficiary_trust_score': 0.1,
                'device_age_days': 3,
                'account_age_days': 60,
                'is_rural_user': 1,
                'device_id': 'FRAUD999'
            },
            'expected_risk': 'HIGH',
            'expected_decision': 'BLOCK'
        },
        {
            'name': 'Rural First-Timer Night Transaction',
            'data': {
                'amount': 35000.0,
                'time_slot': 4,
                'is_new_device': 0,
                'is_new_beneficiary': 1,
                'location_change': 0,
                'transaction_frequency': 8,
                'past_fraud_flag': 0,
                'amount_deviation': 2.0,
                'beneficiary_trust_score': 0.3,
                'device_age_days': 180,
                'account_age_days': 20,
                'is_rural_user': 1,
                'device_id': 'RURAL123'
            },
            'expected_risk': 'HIGH',
            'expected_has_pattern': True
        }
    ]
    
    passed = 0
    failed = 0
    
    for tc in test_cases:
        print(f"\n📊 Test: {tc['name']}")
        print(f"   Amount: ₹{tc['data']['amount']:.0f}, Time: {tc['data']['time_slot']}, Account Age: {tc['data']['account_age_days']} days")
        
        result = predictor.predict(tc['data'])
        
        print(f"   Risk Level: {result['risk_level']} (Expected: {tc['expected_risk']})")
        print(f"   Decision: {result['decision']}")
        print(f"   Fraud Probability: {result['fraud_probability']:.2%}")
        print(f"   Vulnerability Score: {result.get('vulnerability_score', 'N/A')}/100")
        print(f"   User Type: {result.get('user_type', 'N/A')}")
        
        if 'pattern_alerts' in result and result['pattern_alerts']:
            print(f"   Pattern Alerts: {len(result['pattern_alerts'])} detected")
            for alert in result['pattern_alerts']:
                print(f"      - {alert['pattern']}: {alert['severity']}")
        
        # Validation
        risk_match = result['risk_level'] == tc['expected_risk']
        
        if 'expected_decision' in tc:
            decision_match = result['decision'] == tc['expected_decision']
        else:
            decision_match = True
        
        if 'expected_has_pattern' in tc:
            pattern_match = ('pattern_alerts' in result and len(result['pattern_alerts']) > 0) == tc['expected_has_pattern']
        else:
            pattern_match = True
        
        if risk_match and decision_match and pattern_match:
            print("   ✅ PASSED")
            passed += 1
        else:
            print("   ❌ FAILED")
            if not risk_match:
                print(f"      Risk mismatch: got {result['risk_level']}, expected {tc['expected_risk']}")
            if not decision_match:
                print(f"      Decision mismatch: got {result['decision']}, expected {tc.get('expected_decision')}")
            if not pattern_match:
                print(f"      Pattern mismatch")
            failed += 1
    
    print(f"\n{'='*80}")
    print(f"Transaction Analysis Results: {passed} passed, {failed} failed")
    print(f"{'='*80}\n")
    
    return passed, failed


def test_verification_attack():
    """Test verification attack detection"""
    print("\n" + "="*80)
    print("VERIFICATION ATTACK PATTERN VALIDATION")
    print("="*80)
    
    try:
        predictor = FraudPredictor(model_type='random_forest')
    except Exception as e:
        print(f"❌ Failed to load model: {e}")
        return 0, 1
    
    print("\n📝 Test: Verification Attack Sequence")
    
    # Small test transaction
    print("\n   Step 1: Small test transaction (₹5)")
    small_tx = {
        'amount': 5.0,
        'time_slot': 2,
        'is_new_device': 0,
        'is_new_beneficiary': 1,
        'location_change': 0,
        'transaction_frequency': 5,
        'past_fraud_flag': 0,
        'amount_deviation': 0.1,
        'beneficiary_trust_score': 0.5,
        'device_age_days': 100,
        'account_age_days': 300,
        'is_rural_user': 0,
        'device_id': 'VERIFY789'
    }
    result1 = predictor.predict(small_tx)
    print(f"   Result: {result1['risk_level']}, {result1['decision']}")
    
    # Large fraud transaction from SAME device
    print("\n   Step 2: Large transaction from SAME device (₹60,000)")
    large_tx = {
        'amount': 60000.0,
        'time_slot': 3,
        'is_new_device': 0,
        'is_new_beneficiary': 1,
        'location_change': 0,
        'transaction_frequency': 5,
        'past_fraud_flag': 0,
        'amount_deviation': 5.0,
        'beneficiary_trust_score': 0.2,
        'device_age_days': 100,
        'account_age_days': 300,
        'is_rural_user': 0,
        'device_id': 'VERIFY789'  # SAME DEVICE
    }
    result2 = predictor.predict(large_tx)
    print(f"   Result: {result2['risk_level']}, {result2['decision']}")
    
    # Check for verification attack alert
    verification_detected = False
    if 'pattern_alerts' in result2 and result2['pattern_alerts']:
        for alert in result2['pattern_alerts']:
            if alert['pattern'] == 'verification_attack':
                verification_detected = True
                print(f"\n   ✅ Verification Attack Detected!")
                print(f"      Severity: {alert['severity']}")
                print(f"      Score: {alert['score']}")
                print(f"      Details: {alert['details']}")
    
    if verification_detected:
        print("\n   ✅ PASSED - Verification attack pattern detected")
        return 1, 0
    else:
        print("\n   ❌ FAILED - Verification attack not detected")
        return 0, 1


def main():
    """Run all validation tests"""
    print("\n" + "="*80)
    print("🛡️  UPI FRAUD DETECTION SYSTEM - VALIDATION SUITE")
    print("="*80)
    
    total_passed = 0
    total_failed = 0
    
    # Test 1: Message Filter
    p, f = test_message_filter()
    total_passed += p
    total_failed += f
    
    # Test 2: Transaction Analysis
    p, f = test_transaction_analysis()
    total_passed += p
    total_failed += f
    
    # Test 3: Verification Attack
    p, f = test_verification_attack()
    total_passed += p
    total_failed += f
    
    # Final Summary
    print("\n" + "="*80)
    print("FINAL VALIDATION RESULTS")
    print("="*80)
    print(f"✅ Total Passed: {total_passed}")
    print(f"❌ Total Failed: {total_failed}")
    print(f"📊 Success Rate: {(total_passed/(total_passed+total_failed)*100):.1f}%")
    print("="*80 + "\n")
    
    if total_failed == 0:
        print("🎉 All tests passed! System is working correctly.")
        return 0
    else:
        print(f"⚠️  {total_failed} test(s) failed. Please review the results above.")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

"""
UPI Transaction Dataset Generator
Generates synthetic UPI transaction data with realistic fraud patterns
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import random
import os

# Set random seed for reproducibility
np.random.seed(42)
random.seed(42)

def generate_upi_transactions(n_samples=10000, fraud_ratio=0.15):
    """
    Generate synthetic UPI transaction dataset
    
    Args:
        n_samples: Total number of transactions
        fraud_ratio: Proportion of fraudulent transactions
    """
    
    n_fraud = int(n_samples * fraud_ratio)
    n_legitimate = n_samples - n_fraud
    
    # Indian cities for realistic locations
    metro_cities = ['Mumbai', 'Delhi', 'Bangalore', 'Hyderabad', 'Chennai', 'Kolkata', 'Pune']
    tier2_cities = ['Lucknow', 'Jaipur', 'Ahmedabad', 'Surat', 'Nagpur', 'Indore', 'Chandigarh', 'Coimbatore']
    rural_areas = ['Meerut', 'Bhopal', 'Amritsar', 'Mysore', 'Ranchi', 'Raipur', 'Guwahati', 'Dehradun']
    
    # Initialize lists
    data = []
    
    print(f"Generating {n_legitimate} legitimate transactions...")
    # Generate legitimate transactions
    for i in range(n_legitimate):
        # Choose location type
        location_type = np.random.choice(['metro', 'tier2', 'rural'], p=[0.5, 0.3, 0.2])
        if location_type == 'metro':
            location = np.random.choice(metro_cities)
            is_rural = 0
        elif location_type == 'tier2':
            location = np.random.choice(tier2_cities)
            is_rural = 0
        else:
            location = np.random.choice(rural_areas)
            is_rural = 1
        
        # Amount patterns
        amount = np.random.choice([
            np.random.uniform(10, 500),      # 60% small amounts
            np.random.uniform(500, 2000),    # 30% medium amounts
            np.random.uniform(2000, 10000)   # 10% large amounts
        ], p=[0.6, 0.3, 0.1])
        
        # Device and account info
        device_age = np.random.uniform(30, 1000)
        account_age = np.random.uniform(100, 2000)
        
        transaction = {
            'transaction_id': f'TXN{str(i+1).zfill(8)}',
            'amount': amount,
            'time_slot': np.random.choice([0, 1, 2, 3], p=[0.2, 0.4, 0.3, 0.1]),  # Morning, Afternoon, Evening, Night
            'is_new_device': np.random.choice([0, 1], p=[0.95, 0.05]),  # 5% new device
            'is_new_beneficiary': np.random.choice([0, 1], p=[0.7, 0.3]),  # 30% new beneficiary
            'location_change': np.random.choice([0, 1], p=[0.9, 0.1]),  # 10% location change
            'transaction_frequency': np.random.poisson(3),  # Average 3 transactions per day
            'past_fraud_flag': 0,  # No past fraud for legitimate users
            'amount_deviation': np.random.uniform(0, 0.3),  # Low deviation from user average
            'beneficiary_trust_score': np.random.uniform(0.7, 1.0),  # High trust
            'device_age_days': int(device_age),
            'account_age_days': int(account_age),
            
            # NEW COLUMNS
            'is_small_verification': 1 if amount < 10 else 0,
            'is_first_time_user': 1 if account_age < 30 else 0,
            'beneficiary_change_velocity': np.random.randint(0, 5),  # Low velocity for legitimate
            'is_rural_user': is_rural,
            'rapid_transactions_1h': np.random.randint(0, 3),  # Low for legitimate
            'upi_pin_failed_attempts': 0,  # No failed attempts for legitimate
            'account_reports': 0,  # No reports for legitimate users
            'location': location,
            'device_id': f'DEV{np.random.randint(10000, 99999)}',
            'payee_balance_before': round(np.random.uniform(1000, 50000), 2),
            'payee_balance_after': 0,  # Will calculate
            'beneficiary_balance_before': round(np.random.uniform(500, 30000), 2),
            'beneficiary_balance_after': 0,  # Will calculate
            
            'fraud_type': 'legitimate',
            'is_fraud': 0
        }
        
        # Calculate balances after transaction
        transaction['payee_balance_after'] = round(transaction['payee_balance_before'] - amount, 2)
        transaction['beneficiary_balance_after'] = round(transaction['beneficiary_balance_before'] + amount, 2)
        
        data.append(transaction)
    
    print(f"Generating {n_fraud} fraudulent transactions...")
    # Generate fraudulent transactions
    for i in range(n_fraud):
        # Fraud patterns
        fraud_type = np.random.choice(['high_amount', 'new_device', 'night_rush', 'multiple_new'])
        
        # Fraud tends to come from varied locations
        location = np.random.choice(metro_cities + tier2_cities + rural_areas)
        is_rural = 1 if location in rural_areas else 0
        
        if fraud_type == 'high_amount':
            # Large amount fraud
            amount = np.random.uniform(10000, 50000)
            device_age = np.random.uniform(0, 10)
            account_age = np.random.uniform(10, 500)
            
            transaction = {
                'transaction_id': f'TXN{str(n_legitimate + i + 1).zfill(8)}',
                'amount': amount,
                'time_slot': np.random.choice([2, 3], p=[0.3, 0.7]),  # Mostly night
                'is_new_device': np.random.choice([0, 1], p=[0.3, 0.7]),  # Often new device
                'is_new_beneficiary': 1,  # Always new beneficiary
                'location_change': np.random.choice([0, 1], p=[0.4, 0.6]),
                'transaction_frequency': np.random.randint(8, 20),  # High frequency
                'past_fraud_flag': np.random.choice([0, 1], p=[0.7, 0.3]),
                'amount_deviation': np.random.uniform(0.7, 1.5),  # High deviation
                'beneficiary_trust_score': np.random.uniform(0, 0.3),  # Low trust
                'device_age_days': int(device_age),
                'account_age_days': int(account_age),
                
                # NEW COLUMNS - Fraud patterns
                'is_small_verification': 0,  # Big fraud, not small test
                'is_first_time_user': 1 if account_age < 30 else 0,
                'beneficiary_change_velocity': np.random.randint(5, 15),  # High velocity
                'is_rural_user': is_rural,
                'rapid_transactions_1h': np.random.randint(5, 20),  # Many rapid transactions
                'upi_pin_failed_attempts': np.random.randint(0, 3),  # Some failed attempts
                'account_reports': np.random.choice([0, 1], p=[0.7, 0.3]),  # Some reported
                'location': location,
                'device_id': f'DEV{np.random.randint(10000, 99999)}',
                'payee_balance_before': round(np.random.uniform(5000, 100000), 2),
                'payee_balance_after': 0,
                'beneficiary_balance_before': round(np.random.uniform(100, 5000), 2),
                'beneficiary_balance_after': 0,
                
                'fraud_type': 'high_amount',
                'is_fraud': 1
            }
            
            transaction['payee_balance_after'] = round(transaction['payee_balance_before'] - amount, 2)
            transaction['beneficiary_balance_after'] = round(transaction['beneficiary_balance_before'] + amount, 2)
        
        elif fraud_type == 'new_device':
            # New device + suspicious pattern
            amount = np.random.uniform(5000, 30000)
            account_age = np.random.uniform(50, 800)
            
            transaction = {
                'transaction_id': f'TXN{str(n_legitimate + i + 1).zfill(8)}',
                'amount': amount,
                'time_slot': np.random.choice([1, 2, 3]),
                'is_new_device': 1,  # New device
                'is_new_beneficiary': 1,
                'location_change': 1,  # Location changed
                'transaction_frequency': np.random.randint(5, 15),
                'past_fraud_flag': np.random.choice([0, 1], p=[0.8, 0.2]),
                'amount_deviation': np.random.uniform(0.5, 1.2),
                'beneficiary_trust_score': np.random.uniform(0, 0.4),
                'device_age_days': 0,  # Brand new device
                'account_age_days': int(account_age),
                
                # NEW COLUMNS
                'is_small_verification': 0,
                'is_first_time_user': 1 if account_age < 30 else 0,
                'beneficiary_change_velocity': np.random.randint(7, 15),
                'is_rural_user': is_rural,
                'rapid_transactions_1h': np.random.randint(6, 18),
                'upi_pin_failed_attempts': np.random.randint(1, 4),  # Failed attempts on new device
                'account_reports': np.random.choice([0, 1], p=[0.6, 0.4]),
                'location': location,
                'device_id': f'DEV{np.random.randint(10000, 99999)}',
                'payee_balance_before': round(np.random.uniform(3000, 80000), 2),
                'payee_balance_after': 0,
                'beneficiary_balance_before': round(np.random.uniform(200, 8000), 2),
                'beneficiary_balance_after': 0,
                
                'fraud_type': 'new_device',
                'is_fraud': 1
            }
            
            transaction['payee_balance_after'] = round(transaction['payee_balance_before'] - amount, 2)
            transaction['beneficiary_balance_after'] = round(transaction['beneficiary_balance_before'] + amount, 2)
        
        elif fraud_type == 'night_rush':
            # Multiple night transactions
            amount = np.random.uniform(3000, 20000)
            device_age = np.random.uniform(0, 30)
            account_age = np.random.uniform(20, 600)
            
            transaction = {
                'transaction_id': f'TXN{str(n_legitimate + i + 1).zfill(8)}',
                'amount': amount,
                'time_slot': 3,  # Night only
                'is_new_device': np.random.choice([0, 1], p=[0.5, 0.5]),
                'is_new_beneficiary': 1,
                'location_change': np.random.choice([0, 1], p=[0.3, 0.7]),
                'transaction_frequency': np.random.randint(10, 25),  # Very high frequency
                'past_fraud_flag': np.random.choice([0, 1], p=[0.6, 0.4]),
                'amount_deviation': np.random.uniform(0.6, 1.3),
                'beneficiary_trust_score': np.random.uniform(0, 0.5),
                'device_age_days': int(device_age),
                'account_age_days': int(account_age),
                
                # NEW COLUMNS
                'is_small_verification': 0,
                'is_first_time_user': 1 if account_age < 30 else 0,
                'beneficiary_change_velocity': np.random.randint(8, 20),  # Very high
                'is_rural_user': is_rural,
                'rapid_transactions_1h': np.random.randint(10, 25),  # Many at night
                'upi_pin_failed_attempts': np.random.randint(0, 2),
                'account_reports': np.random.choice([0, 1], p=[0.5, 0.5]),
                'location': location,
                'device_id': f'DEV{np.random.randint(10000, 99999)}',
                'payee_balance_before': round(np.random.uniform(2000, 70000), 2),
                'payee_balance_after': 0,
                'beneficiary_balance_before': round(np.random.uniform(100, 3000), 2),
                'beneficiary_balance_after': 0,
                
                'fraud_type': 'night_rush',
                'is_fraud': 1
            }
            
            transaction['payee_balance_after'] = round(transaction['payee_balance_before'] - amount, 2)
            transaction['beneficiary_balance_after'] = round(transaction['beneficiary_balance_before'] + amount, 2)
        
        else:  # multiple_new
            # Multiple new indicators + small verification pattern
            amount = np.random.uniform(2000, 25000)
            device_age = np.random.uniform(0, 5)
            account_age = np.random.uniform(5, 400)
            
            # 30% chance this is a small verification transaction before big fraud
            if np.random.random() < 0.3:
                amount = np.random.uniform(1, 9)  # Small test amount
                is_small_verif = 1
            else:
                is_small_verif = 0
            
            transaction = {
                'transaction_id': f'TXN{str(n_legitimate + i + 1).zfill(8)}',
                'amount': amount,
                'time_slot': np.random.choice([2, 3]),
                'is_new_device': 1,
                'is_new_beneficiary': 1,
                'location_change': 1,
                'transaction_frequency': np.random.randint(7, 18),
                'past_fraud_flag': np.random.choice([0, 1], p=[0.5, 0.5]),
                'amount_deviation': np.random.uniform(0.8, 1.6),
                'beneficiary_trust_score': np.random.uniform(0, 0.2),
                'device_age_days': int(device_age),
                'account_age_days': int(account_age),
                
                # NEW COLUMNS
                'is_small_verification': is_small_verif,
                'is_first_time_user': 1 if account_age < 30 else 0,
                'beneficiary_change_velocity': np.random.randint(10, 20),  # Very high
                'is_rural_user': is_rural,
                'rapid_transactions_1h': np.random.randint(8, 22),
                'upi_pin_failed_attempts': np.random.randint(1, 5),  # Many failed attempts
                'account_reports': np.random.choice([0, 1], p=[0.4, 0.6]),  # Often reported
                'location': location,
                'device_id': f'DEV{np.random.randint(10000, 99999)}',
                'payee_balance_before': round(np.random.uniform(1000, 60000), 2),
                'payee_balance_after': 0,
                'beneficiary_balance_before': round(np.random.uniform(50, 2000), 2),
                'beneficiary_balance_after': 0,
                
                'fraud_type': 'multiple_new',
                'is_fraud': 1
            }
            
            transaction['payee_balance_after'] = round(transaction['payee_balance_before'] - amount, 2)
            transaction['beneficiary_balance_after'] = round(transaction['beneficiary_balance_before'] + amount, 2)
        
        data.append(transaction)
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Shuffle the dataset
    df = df.sample(frac=1).reset_index(drop=True)
    
    # Round numerical values
    df['amount'] = df['amount'].round(2)
    df['amount_deviation'] = df['amount_deviation'].round(3)
    df['beneficiary_trust_score'] = df['beneficiary_trust_score'].round(3)
    df['payee_balance_before'] = df['payee_balance_before'].round(2)
    df['payee_balance_after'] = df['payee_balance_after'].round(2)
    df['beneficiary_balance_before'] = df['beneficiary_balance_before'].round(2)
    df['beneficiary_balance_after'] = df['beneficiary_balance_after'].round(2)
    
    return df


def save_dataset(df, output_dir='data/raw'):
    """Save the generated dataset"""
    os.makedirs(output_dir, exist_ok=True)
    
    output_path = os.path.join(output_dir, 'upi_transactions.csv')
    df.to_csv(output_path, index=False)
    
    print(f"\n✅ Dataset saved to: {output_path}")
    print(f"Total transactions: {len(df)}")
    print(f"Fraudulent: {df['is_fraud'].sum()} ({df['is_fraud'].mean()*100:.1f}%)")
    print(f"Legitimate: {(~df['is_fraud'].astype(bool)).sum()} ({(~df['is_fraud'].astype(bool)).mean()*100:.1f}%)")
    
    return output_path


def print_dataset_stats(df):
    """Print comprehensive dataset statistics"""
    print("\n" + "="*60)
    print("UPI FRAUD DETECTION - ENHANCED DATASET STATISTICS")
    print("="*60)
    
    fraud_df = df[df['is_fraud'] == 1]
    legit_df = df[df['is_fraud'] == 0]
    
    print(f"\n📊 Dataset Size: {len(df):,} transactions ({df.shape[1]} features)")
    print(f"   Fraudulent: {len(fraud_df):,} ({len(fraud_df)/len(df)*100:.1f}%)")
    print(f"   Legitimate: {len(legit_df):,} ({len(legit_df)/len(df)*100:.1f}%)")
    
    print("\n" + "-"*60)
    print("FRAUD TYPE BREAKDOWN")
    print("-"*60)
    fraud_types = fraud_df['fraud_type'].value_counts()
    for fraud_type, count in fraud_types.items():
        print(f"  {fraud_type.replace('_', ' ').title():.<40} {count:>5,} ({count/len(fraud_df)*100:>5.1f}%)")
    
    print("\n" + "-"*60)
    print("LOCATION INTELLIGENCE")
    print("-"*60)
    location_fraud = df[df['is_fraud'] == 1]['location'].value_counts().head(5)
    print("Top 5 High-Risk Cities:")
    for city, count in location_fraud.items():
        print(f"  {city:.<40} {count:>5,} frauds")
    
    print("\n" + "-"*60)
    print("ENHANCED FEATURES SNAPSHOT")
    print("-"*60)
    print(f"  Small Verification Txns: {df['is_small_verification'].sum():,}")
    print(f"  First-Time Users: {df['is_first_time_user'].sum():,}")
    print(f"  Rural Transactions: {df['is_rural_user'].sum():,}")
    print(f"  Total PIN Failures: {df['upi_pin_failed_attempts'].sum():,.0f}")
    print(f"  Total Account Reports: {df['account_reports'].sum():,.0f}")
    print(f"  Rapid Transactions (1h): {df[df['rapid_transactions_1h'] > 0]['rapid_transactions_1h'].sum():,.0f}")
    
    print("\n" + "-"*60)
    print("FINANCIAL METRICS")
    print("-"*60)
    print(f"  Average Transaction: ₹{df['amount'].mean():>10,.2f}")
    print(f"  Fraud Avg Amount: ₹{fraud_df['amount'].mean():>10,.2f}")
    print(f"  Legitimate Avg: ₹{legit_df['amount'].mean():>10,.2f}")
    print(f"  Total Volume: ₹{df['amount'].sum():>10,.0f}")
    
    print("\n" + "-"*60)
    print("TIME DISTRIBUTION")
    print("-"*60)
    time_mapping = {0: 'Morning', 1: 'Afternoon', 2: 'Evening', 3: 'Night'}
    for time_val, time_name in time_mapping.items():
        count = (df['time_slot'] == time_val).sum()
        print(f"  {time_name:.<40} {count:>5,} ({count/len(df)*100:>5.1f}%)")
    
    print("\n" + "="*60)


if __name__ == "__main__":
    print("🚀 Starting UPI Transaction Dataset Generation...")
    print("="*60)
    
    # Generate dataset
    df = generate_upi_transactions(n_samples=10000, fraud_ratio=0.15)
    
    # Print statistics
    print_dataset_stats(df)
    
    # Save dataset
    output_path = save_dataset(df)
    
    # Show sample data
    print("\n📋 Sample Transactions:")
    print("\nLegitimate Transactions:")
    print(df[df['is_fraud'] == 0].head(3))
    print("\nFraudulent Transactions:")
    print(df[df['is_fraud'] == 1].head(3))
    
    print("\n✅ Dataset generation complete! 🎉")
    print(f"Next step: Run 'python src/models/train_model.py' to train the model")

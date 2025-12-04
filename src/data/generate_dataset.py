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
    
    # Initialize lists
    data = []
    
    print(f"Generating {n_legitimate} legitimate transactions...")
    # Generate legitimate transactions
    for i in range(n_legitimate):
        transaction = {
            'transaction_id': f'TXN{str(i+1).zfill(8)}',
            'amount': np.random.choice([
                np.random.uniform(10, 500),      # 60% small amounts
                np.random.uniform(500, 2000),    # 30% medium amounts
                np.random.uniform(2000, 10000)   # 10% large amounts
            ], p=[0.6, 0.3, 0.1]),
            'time_slot': np.random.choice([0, 1, 2, 3], p=[0.2, 0.4, 0.3, 0.1]),  # Morning, Afternoon, Evening, Night
            'is_new_device': np.random.choice([0, 1], p=[0.95, 0.05]),  # 5% new device
            'is_new_beneficiary': np.random.choice([0, 1], p=[0.7, 0.3]),  # 30% new beneficiary
            'location_change': np.random.choice([0, 1], p=[0.9, 0.1]),  # 10% location change
            'transaction_frequency': np.random.poisson(3),  # Average 3 transactions per day
            'past_fraud_flag': 0,  # No past fraud for legitimate users
            'amount_deviation': np.random.uniform(0, 0.3),  # Low deviation from user average
            'beneficiary_trust_score': np.random.uniform(0.7, 1.0),  # High trust
            'device_age_days': np.random.uniform(30, 1000),  # Device used for a while
            'account_age_days': np.random.uniform(100, 2000),  # Account established
            'is_fraud': 0
        }
        data.append(transaction)
    
    print(f"Generating {n_fraud} fraudulent transactions...")
    # Generate fraudulent transactions
    for i in range(n_fraud):
        # Fraud patterns
        fraud_type = np.random.choice(['high_amount', 'new_device', 'night_rush', 'multiple_new'])
        
        if fraud_type == 'high_amount':
            # Large amount fraud
            transaction = {
                'transaction_id': f'TXN{str(n_legitimate + i + 1).zfill(8)}',
                'amount': np.random.uniform(10000, 50000),  # Large amounts
                'time_slot': np.random.choice([2, 3], p=[0.3, 0.7]),  # Mostly night
                'is_new_device': np.random.choice([0, 1], p=[0.3, 0.7]),  # Often new device
                'is_new_beneficiary': 1,  # Always new beneficiary
                'location_change': np.random.choice([0, 1], p=[0.4, 0.6]),
                'transaction_frequency': np.random.randint(8, 20),  # High frequency
                'past_fraud_flag': np.random.choice([0, 1], p=[0.7, 0.3]),
                'amount_deviation': np.random.uniform(0.7, 1.5),  # High deviation
                'beneficiary_trust_score': np.random.uniform(0, 0.3),  # Low trust
                'device_age_days': np.random.uniform(0, 10),  # New device
                'account_age_days': np.random.uniform(10, 500),
                'is_fraud': 1
            }
        
        elif fraud_type == 'new_device':
            # New device + suspicious pattern
            transaction = {
                'transaction_id': f'TXN{str(n_legitimate + i + 1).zfill(8)}',
                'amount': np.random.uniform(5000, 30000),
                'time_slot': np.random.choice([1, 2, 3]),
                'is_new_device': 1,  # New device
                'is_new_beneficiary': 1,
                'location_change': 1,  # Location changed
                'transaction_frequency': np.random.randint(5, 15),
                'past_fraud_flag': np.random.choice([0, 1], p=[0.8, 0.2]),
                'amount_deviation': np.random.uniform(0.5, 1.2),
                'beneficiary_trust_score': np.random.uniform(0, 0.4),
                'device_age_days': 0,  # Brand new device
                'account_age_days': np.random.uniform(50, 800),
                'is_fraud': 1
            }
        
        elif fraud_type == 'night_rush':
            # Multiple night transactions
            transaction = {
                'transaction_id': f'TXN{str(n_legitimate + i + 1).zfill(8)}',
                'amount': np.random.uniform(3000, 20000),
                'time_slot': 3,  # Night only
                'is_new_device': np.random.choice([0, 1], p=[0.5, 0.5]),
                'is_new_beneficiary': 1,
                'location_change': np.random.choice([0, 1], p=[0.3, 0.7]),
                'transaction_frequency': np.random.randint(10, 25),  # Very high frequency
                'past_fraud_flag': np.random.choice([0, 1], p=[0.6, 0.4]),
                'amount_deviation': np.random.uniform(0.6, 1.3),
                'beneficiary_trust_score': np.random.uniform(0, 0.5),
                'device_age_days': np.random.uniform(0, 30),
                'account_age_days': np.random.uniform(20, 600),
                'is_fraud': 1
            }
        
        else:  # multiple_new
            # Multiple new indicators
            transaction = {
                'transaction_id': f'TXN{str(n_legitimate + i + 1).zfill(8)}',
                'amount': np.random.uniform(2000, 25000),
                'time_slot': np.random.choice([2, 3]),
                'is_new_device': 1,
                'is_new_beneficiary': 1,
                'location_change': 1,
                'transaction_frequency': np.random.randint(7, 18),
                'past_fraud_flag': np.random.choice([0, 1], p=[0.5, 0.5]),
                'amount_deviation': np.random.uniform(0.8, 1.6),
                'beneficiary_trust_score': np.random.uniform(0, 0.2),
                'device_age_days': np.random.uniform(0, 5),
                'account_age_days': np.random.uniform(5, 400),
                'is_fraud': 1
            }
        
        data.append(transaction)
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Shuffle the dataset
    df = df.sample(frac=1).reset_index(drop=True)
    
    # Round numerical values
    df['amount'] = df['amount'].round(2)
    df['amount_deviation'] = df['amount_deviation'].round(3)
    df['beneficiary_trust_score'] = df['beneficiary_trust_score'].round(3)
    df['device_age_days'] = df['device_age_days'].round(0).astype(int)
    df['account_age_days'] = df['account_age_days'].round(0).astype(int)
    
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
    """Print dataset statistics"""
    print("\n" + "="*60)
    print("📊 DATASET STATISTICS")
    print("="*60)
    
    print(f"\n🔢 Shape: {df.shape[0]} rows × {df.shape[1]} columns")
    
    print(f"\n💰 Amount Statistics:")
    print(f"  Mean: ₹{df['amount'].mean():.2f}")
    print(f"  Median: ₹{df['amount'].median():.2f}")
    print(f"  Max: ₹{df['amount'].max():.2f}")
    print(f"  Min: ₹{df['amount'].min():.2f}")
    
    print(f"\n🕐 Time Distribution:")
    time_mapping = {0: 'Morning', 1: 'Afternoon', 2: 'Evening', 3: 'Night'}
    for time_val, time_name in time_mapping.items():
        count = (df['time_slot'] == time_val).sum()
        print(f"  {time_name}: {count} ({count/len(df)*100:.1f}%)")
    
    print(f"\n🚨 Fraud Distribution:")
    fraud_counts = df['is_fraud'].value_counts()
    print(f"  Legitimate: {fraud_counts[0]} ({fraud_counts[0]/len(df)*100:.1f}%)")
    print(f"  Fraudulent: {fraud_counts[1]} ({fraud_counts[1]/len(df)*100:.1f}%)")
    
    print(f"\n📱 Feature Statistics:")
    print(f"  New Device: {df['is_new_device'].sum()} transactions")
    print(f"  New Beneficiary: {df['is_new_beneficiary'].sum()} transactions")
    print(f"  Location Change: {df['location_change'].sum()} transactions")
    print(f"  Past Fraud Flag: {df['past_fraud_flag'].sum()} transactions")
    
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

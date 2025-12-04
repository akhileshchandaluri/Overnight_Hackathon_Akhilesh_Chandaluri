"""
ML Model Training Pipeline
Trains RandomForest, XGBoost, and Isolation Forest models for fraud detection
"""

import numpy as np
import pandas as pd
import os
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.metrics import (
    classification_report, 
    confusion_matrix, 
    roc_auc_score, 
    precision_recall_curve,
    f1_score,
    accuracy_score
)
from imblearn.over_sampling import SMOTE
import xgboost as xgb
import matplotlib.pyplot as plt
import seaborn as sns


class FraudDetectionModel:
    """Fraud Detection Model Trainer"""
    
    def __init__(self, data_path='data/raw/upi_transactions.csv'):
        self.data_path = data_path
        self.models = {}
        self.scaler = StandardScaler()
        self.feature_names = []
        
    def load_data(self):
        """Load the dataset"""
        print("📂 Loading dataset...")
        self.df = pd.read_csv(self.data_path)
        print(f"✅ Loaded {len(self.df)} transactions")
        return self.df
    
    def preprocess_data(self):
        """Preprocess and prepare features"""
        print("\n🔧 Preprocessing data...")
        
        # Feature columns (excluding ID and target)
        feature_cols = [
            'amount', 'time_slot', 'is_new_device', 'is_new_beneficiary',
            'location_change', 'transaction_frequency', 'past_fraud_flag',
            'amount_deviation', 'beneficiary_trust_score', 'device_age_days',
            'account_age_days'
        ]
        
        self.feature_names = feature_cols
        
        # Prepare X and y
        X = self.df[feature_cols]
        y = self.df['is_fraud']
        
        # Split data
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        print(f"✅ Train set: {len(self.X_train)} samples")
        print(f"✅ Test set: {len(self.X_test)} samples")
        
        # Handle class imbalance with SMOTE
        print("\n⚖️ Balancing classes with SMOTE...")
        smote = SMOTE(random_state=42)
        self.X_train_balanced, self.y_train_balanced = smote.fit_resample(
            self.X_train, self.y_train
        )
        print(f"✅ Balanced train set: {len(self.X_train_balanced)} samples")
        
        # Scale features
        self.X_train_scaled = self.scaler.fit_transform(self.X_train_balanced)
        self.X_test_scaled = self.scaler.transform(self.X_test)
        
        print("✅ Feature scaling completed")
        
    def train_random_forest(self):
        """Train Random Forest model"""
        print("\n🌲 Training Random Forest...")
        
        rf_model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            min_samples_split=10,
            min_samples_leaf=4,
            random_state=42,
            n_jobs=-1
        )
        
        rf_model.fit(self.X_train_balanced, self.y_train_balanced)
        self.models['random_forest'] = rf_model
        
        # Predictions
        y_pred = rf_model.predict(self.X_test)
        y_pred_proba = rf_model.predict_proba(self.X_test)[:, 1]
        
        # Evaluation
        print("\n📊 Random Forest Results:")
        self._print_metrics(y_pred, y_pred_proba)
        
        # Feature importance
        self._plot_feature_importance(rf_model, 'random_forest')
        
        return rf_model
    
    def train_xgboost(self):
        """Train XGBoost model"""
        print("\n🚀 Training XGBoost...")
        
        xgb_model = xgb.XGBClassifier(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42,
            eval_metric='logloss'
        )
        
        xgb_model.fit(self.X_train_balanced, self.y_train_balanced)
        self.models['xgboost'] = xgb_model
        
        # Predictions
        y_pred = xgb_model.predict(self.X_test)
        y_pred_proba = xgb_model.predict_proba(self.X_test)[:, 1]
        
        # Evaluation
        print("\n📊 XGBoost Results:")
        self._print_metrics(y_pred, y_pred_proba)
        
        # Feature importance
        self._plot_feature_importance(xgb_model, 'xgboost')
        
        return xgb_model
    
    def train_isolation_forest(self):
        """Train Isolation Forest for anomaly detection"""
        print("\n🌳 Training Isolation Forest...")
        
        iso_model = IsolationForest(
            n_estimators=100,
            contamination=0.15,  # Expected fraud ratio
            random_state=42,
            n_jobs=-1
        )
        
        iso_model.fit(self.X_train_scaled)
        self.models['isolation_forest'] = iso_model
        
        # Predictions (-1 for anomaly/fraud, 1 for normal)
        y_pred_iso = iso_model.predict(self.X_test_scaled)
        y_pred = (y_pred_iso == -1).astype(int)  # Convert to 0/1
        
        # Get anomaly scores
        anomaly_scores = iso_model.score_samples(self.X_test_scaled)
        # Convert to probability (higher score = less anomalous)
        y_pred_proba = 1 / (1 + np.exp(anomaly_scores))
        
        # Evaluation
        print("\n📊 Isolation Forest Results:")
        self._print_metrics(y_pred, y_pred_proba)
        
        return iso_model
    
    def _print_metrics(self, y_pred, y_pred_proba):
        """Print evaluation metrics"""
        accuracy = accuracy_score(self.y_test, y_pred)
        f1 = f1_score(self.y_test, y_pred)
        roc_auc = roc_auc_score(self.y_test, y_pred_proba)
        
        print(f"  Accuracy: {accuracy:.4f}")
        print(f"  F1-Score: {f1:.4f}")
        print(f"  ROC-AUC: {roc_auc:.4f}")
        
        print("\n  Classification Report:")
        print(classification_report(self.y_test, y_pred, 
                                   target_names=['Legitimate', 'Fraud']))
        
        print("\n  Confusion Matrix:")
        cm = confusion_matrix(self.y_test, y_pred)
        print(f"  [[TN={cm[0][0]}, FP={cm[0][1]}]")
        print(f"   [FN={cm[1][0]}, TP={cm[1][1]}]]")
    
    def _plot_feature_importance(self, model, model_name):
        """Plot feature importance"""
        if hasattr(model, 'feature_importances_'):
            importance_df = pd.DataFrame({
                'feature': self.feature_names,
                'importance': model.feature_importances_
            }).sort_values('importance', ascending=False)
            
            print("\n  Top 5 Important Features:")
            for idx, row in importance_df.head(5).iterrows():
                print(f"    {row['feature']}: {row['importance']:.4f}")
    
    def save_models(self, output_dir='models'):
        """Save trained models"""
        os.makedirs(output_dir, exist_ok=True)
        
        print("\n💾 Saving models...")
        
        # Save each model
        for model_name, model in self.models.items():
            model_path = os.path.join(output_dir, f'{model_name}.joblib')
            joblib.dump(model, model_path)
            print(f"  ✅ Saved {model_name} to {model_path}")
        
        # Save scaler
        scaler_path = os.path.join(output_dir, 'scaler.joblib')
        joblib.dump(self.scaler, scaler_path)
        print(f"  ✅ Saved scaler to {scaler_path}")
        
        # Save feature names
        feature_path = os.path.join(output_dir, 'feature_names.joblib')
        joblib.dump(self.feature_names, feature_path)
        print(f"  ✅ Saved feature names to {feature_path}")
        
        print("\n✅ All models saved successfully!")
    
    def compare_models(self):
        """Compare all models"""
        print("\n" + "="*60)
        print("📊 MODEL COMPARISON")
        print("="*60)
        
        results = []
        
        for model_name, model in self.models.items():
            if model_name == 'isolation_forest':
                y_pred_iso = model.predict(self.X_test_scaled)
                y_pred = (y_pred_iso == -1).astype(int)
                anomaly_scores = model.score_samples(self.X_test_scaled)
                y_pred_proba = 1 / (1 + np.exp(anomaly_scores))
            else:
                y_pred = model.predict(self.X_test)
                y_pred_proba = model.predict_proba(self.X_test)[:, 1]
            
            accuracy = accuracy_score(self.y_test, y_pred)
            f1 = f1_score(self.y_test, y_pred)
            roc_auc = roc_auc_score(self.y_test, y_pred_proba)
            
            results.append({
                'Model': model_name,
                'Accuracy': f"{accuracy:.4f}",
                'F1-Score': f"{f1:.4f}",
                'ROC-AUC': f"{roc_auc:.4f}"
            })
        
        results_df = pd.DataFrame(results)
        print("\n", results_df.to_string(index=False))
        print("\n" + "="*60)


def main():
    """Main training pipeline"""
    print("🚀 Starting ML Model Training Pipeline")
    print("="*60)
    
    # Initialize trainer
    trainer = FraudDetectionModel()
    
    # Load data
    trainer.load_data()
    
    # Preprocess
    trainer.preprocess_data()
    
    # Train models
    trainer.train_random_forest()
    trainer.train_xgboost()
    trainer.train_isolation_forest()
    
    # Compare models
    trainer.compare_models()
    
    # Save models
    trainer.save_models()
    
    print("\n✅ Training pipeline completed! 🎉")
    print("Next step: Run 'streamlit run src/ui/dashboard.py' to launch the UI")


if __name__ == "__main__":
    main()

"""
ML Model Training Pipeline
Trains RandomForest, XGBoost, and Isolation Forest models for fraud detection
"""

import numpy as np
import pandas as pd
import os
import joblib
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.metrics import (
    classification_report, 
    confusion_matrix, 
    roc_auc_score, 
    precision_recall_curve,
    f1_score,
    accuracy_score,
    precision_score,
    recall_score
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
        
        # All 24 feature columns (excluding transaction_id, fraud_type, is_fraud)
        feature_cols = [
            # Basic transaction features
            'amount', 'time_slot', 'is_new_device', 'is_new_beneficiary',
            'location_change', 'transaction_frequency', 'past_fraud_flag',
            'amount_deviation', 'beneficiary_trust_score', 'device_age_days',
            'account_age_days',
            # Enhanced fraud detection features
            'is_small_verification', 'is_first_time_user', 'beneficiary_change_velocity',
            'is_rural_user', 'rapid_transactions_1h', 'upi_pin_failed_attempts',
            'account_reports', 'payee_balance_before', 'payee_balance_after',
            'beneficiary_balance_before', 'beneficiary_balance_after'
        ]
        
        # Encode location if it exists in columns
        if 'location' in self.df.columns:
            # Label encode location (categorical -> numerical)
            from sklearn.preprocessing import LabelEncoder
            le = LabelEncoder()
            self.df['location_encoded'] = le.fit_transform(self.df['location'])
            feature_cols.append('location_encoded')
            # Save label encoder for later use
            self.location_encoder = le
        
        # Encode device_id if it exists (hash to numeric)
        if 'device_id' in self.df.columns:
            self.df['device_id_hash'] = self.df['device_id'].apply(hash).apply(abs) % 10000
            feature_cols.append('device_id_hash')
        
        self.feature_names = feature_cols
        print(f"✅ Using {len(feature_cols)} features for training")
        
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
        
        # Note: RandomForest works well with raw features, no scaling needed
        print("✅ Data preprocessing completed (no scaling for tree-based models)")
        
    def train_random_forest(self):
        """Train Random Forest model"""
        print("\n🌲 Training Random Forest (Best Model)...")
        
        rf_model = RandomForestClassifier(
            n_estimators=200,
            max_depth=15,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1,
            class_weight='balanced'
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
        """Plot and save feature importance"""
        if hasattr(model, 'feature_importances_'):
            importance_df = pd.DataFrame({
                'feature': self.feature_names,
                'importance': model.feature_importances_
            }).sort_values('importance', ascending=False)
            
            print("\n  Top 5 Important Features:")
            for idx, row in importance_df.head(5).iterrows():
                print(f"    {row['feature']}: {row['importance']:.4f}")
            
            # Create visualization directory
            os.makedirs('reports/figures', exist_ok=True)
            
            # Plot feature importance
            plt.figure(figsize=(12, 8))
            top_features = importance_df.head(15)
            plt.barh(range(len(top_features)), top_features['importance'])
            plt.yticks(range(len(top_features)), top_features['feature'])
            plt.xlabel('Feature Importance', fontsize=12, fontweight='bold')
            plt.ylabel('Features', fontsize=12, fontweight='bold')
            plt.title(f'Top 15 Feature Importance - {model_name.upper()}', fontsize=14, fontweight='bold')
            plt.gca().invert_yaxis()
            plt.tight_layout()
            
            # Save plot
            plot_path = f'reports/figures/{model_name}_feature_importance.png'
            plt.savefig(plot_path, dpi=300, bbox_inches='tight')
            print(f"  ✅ Saved feature importance plot to {plot_path}")
            plt.close()
    
    def plot_confusion_matrix(self, model_name='random_forest'):
        """Plot and save confusion matrix"""
        model = self.models.get(model_name)
        if not model:
            return
        
        y_pred = model.predict(self.X_test)
        cm = confusion_matrix(self.y_test, y_pred)
        
        # Create heatmap
        plt.figure(figsize=(10, 8))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                    xticklabels=['Legitimate', 'Fraud'],
                    yticklabels=['Legitimate', 'Fraud'],
                    cbar_kws={'label': 'Count'})
        plt.xlabel('Predicted Label', fontsize=12, fontweight='bold')
        plt.ylabel('True Label', fontsize=12, fontweight='bold')
        plt.title(f'Confusion Matrix - {model_name.upper()}', fontsize=14, fontweight='bold')
        
        # Add accuracy text
        accuracy = accuracy_score(self.y_test, y_pred)
        plt.text(0.5, -0.15, f'Accuracy: {accuracy:.2%}', 
                ha='center', transform=plt.gca().transAxes, fontsize=12, fontweight='bold')
        
        plt.tight_layout()
        plot_path = f'reports/figures/{model_name}_confusion_matrix.png'
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        print(f"  ✅ Saved confusion matrix to {plot_path}")
        plt.close()
    
    def plot_roc_curve(self, model_name='random_forest'):
        """Plot and save ROC curve"""
        from sklearn.metrics import roc_curve, auc
        
        model = self.models.get(model_name)
        if not model:
            return
        
        y_pred_proba = model.predict_proba(self.X_test)[:, 1]
        fpr, tpr, thresholds = roc_curve(self.y_test, y_pred_proba)
        roc_auc = auc(fpr, tpr)
        
        plt.figure(figsize=(10, 8))
        plt.plot(fpr, tpr, color='darkorange', lw=3, label=f'ROC curve (AUC = {roc_auc:.4f})')
        plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--', label='Random Classifier')
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])
        plt.xlabel('False Positive Rate', fontsize=12, fontweight='bold')
        plt.ylabel('True Positive Rate', fontsize=12, fontweight='bold')
        plt.title(f'ROC Curve - {model_name.upper()}', fontsize=14, fontweight='bold')
        plt.legend(loc="lower right", fontsize=11)
        plt.grid(alpha=0.3)
        plt.tight_layout()
        
        plot_path = f'reports/figures/{model_name}_roc_curve.png'
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        print(f"  ✅ Saved ROC curve to {plot_path}")
        plt.close()
    
    def save_models(self, output_dir='models'):
        """Save trained models"""
        os.makedirs(output_dir, exist_ok=True)
        
        print("\n💾 Saving models...")
        
        # Save each model
        for model_name, model in self.models.items():
            model_path = os.path.join(output_dir, f'{model_name}.joblib')
            joblib.dump(model, model_path)
            print(f"  ✅ Saved {model_name} to {model_path}")
        
        # Save feature names (no scaler needed for RandomForest)
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
            
            # Calculate precision and recall
            from sklearn.metrics import precision_score, recall_score
            precision = precision_score(self.y_test, y_pred)
            recall = recall_score(self.y_test, y_pred)
            
            results.append({
                'Model': model_name,
                'Accuracy': f"{accuracy:.4f}",
                'Precision': f"{precision:.4f}",
                'Recall': f"{recall:.4f}",
                'F1-Score': f"{f1:.4f}",
                'ROC-AUC': f"{roc_auc:.4f}"
            })
        
        results_df = pd.DataFrame(results)
        print("\n", results_df.to_string(index=False))
        print("\n" + "="*60)
        
    def fraud_type_analysis(self):
        """Analyze fraud detection by fraud type"""
        print("\n" + "="*60)
        print("🔍 FRAUD TYPE ANALYSIS")
        print("="*60)
        
        if 'fraud_type' not in self.df.columns:
            print("⚠️ fraud_type column not found in dataset")
            return
        
        # Get predictions from best model (random_forest)
        rf_model = self.models.get('random_forest')
        if not rf_model:
            print("⚠️ Random Forest model not trained")
            return
        
        y_pred = rf_model.predict(self.X_test)
        
        # Map test indices to fraud types
        test_indices = self.y_test.index
        fraud_types = self.df.loc[test_indices, 'fraud_type']
        
        # Analyze by fraud type
        print("\nDetection Rate by Fraud Type:")
        print("-" * 60)
        
        for fraud_type in fraud_types.unique():
            mask = fraud_types == fraud_type
            y_true_type = self.y_test[mask]
            y_pred_type = y_pred[mask]
            
            if len(y_true_type) > 0 and y_true_type.sum() > 0:
                detection_rate = recall_score(y_true_type, y_pred_type, zero_division=0)
                accuracy_type = accuracy_score(y_true_type, y_pred_type)
                
                print(f"  {fraud_type.upper():.<40} {detection_rate:>6.1%} (n={len(y_true_type)})")
        
        print("=" * 60)


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
    
    # Generate visualizations
    print("\n📊 Generating Model Visualizations...")
    trainer.plot_confusion_matrix('random_forest')
    trainer.plot_roc_curve('random_forest')
    
    # Fraud type analysis
    trainer.fraud_type_analysis()
    
    # Save models
    trainer.save_models()
    
    print("\n✅ Training pipeline completed! 🎉")
    print("Next step: Run 'streamlit run src/ui/dashboard.py' to launch the UI")


if __name__ == "__main__":
    main()

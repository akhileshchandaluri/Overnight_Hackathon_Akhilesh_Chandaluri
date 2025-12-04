# 💸 UPI Transaction Fraud Detection System

Real-time fraud detection for UPI transactions using Machine Learning and behavioral analysis.

## 🎯 Problem
UPI transactions are instant and irreversible. Fraudsters exploit:
- Fake refund scams
- Social engineering attacks
- QR code swapping
- SIM swap & device change fraud
- Small test transactions before big fraud

**Our Solution:** Detect fraud BEFORE the transaction completes, not after money is lost.

## 🧠 Key Features
- **Fraud Probability Score**: ML model gives 0-1 risk probability
- **Hybrid Detection**: Combines behavioral rules + ML predictions
- **Real-time Dashboard**: Visual fraud detection interface
- **Transaction Simulator**: Test with demo transactions
- **Explainability**: Shows why transactions were flagged
- **Smart Alerts**: Block/Warn/Allow decisions

## 🏗 Architecture
```
User Transaction → Feature Extraction → ML Model → Fraud Score → Decision Engine → Alert/Dashboard
```

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Generate Dataset & Train Model
```bash
python src/data/generate_dataset.py
python src/models/train_model.py
```

### 3. Run Dashboard
```bash
streamlit run src/ui/dashboard.py
```

### 4. Run API (Optional)
```bash
python src/api/app.py
```

## 📊 Dataset Features
- **amount**: Transaction value in ₹
- **time_slot**: Time of transaction (Morning/Afternoon/Evening/Night)
- **is_new_device**: First transaction from device (0/1)
- **is_new_beneficiary**: First transaction to recipient (0/1)
- **location_change**: Location different from usual (0/1)
- **transaction_frequency**: Transactions in last 24 hours
- **past_fraud_flag**: Previous fraudulent activity (0/1)

## 🔥 Models Used
1. **RandomForest** - Primary model (95%+ accuracy)
2. **XGBoost** - Gradient boosting for comparison
3. **Isolation Forest** - Anomaly detection

## 🎨 Demo Scenarios
1. **Safe Transaction**: ₹500, morning, regular device → SAFE ✅
2. **Medium Risk**: ₹15,000, new beneficiary, night → WARNING ⚠️
3. **High Risk**: ₹45,000, new device, location change, night → BLOCKED 🚫

## 📁 Project Structure
```
fraud/
├── data/
│   ├── raw/                 # Generated datasets
│   └── processed/           # Cleaned data
├── models/                  # Trained model files
├── src/
│   ├── data/               # Data generation
│   ├── models/             # ML training & prediction
│   ├── api/                # Backend API
│   └── ui/                 # Streamlit dashboard
├── notebooks/              # Analysis notebooks
└── tests/                  # Test scenarios
```

## 🏆 Why This Wins
- ✅ **Real Problem**: ₹1,000+ crore fraud annually in India
- ✅ **High Tech**: ML + Cybersecurity + FinTech
- ✅ **Live Demo**: Visual, interactive, impressive
- ✅ **Explainable**: Clear reasoning for decisions
- ✅ **Scalable**: Can integrate with NPCI, banks, UPI apps

## 💡 Future Enhancements
- Network graph fraud ring detection
- Advanced device fingerprinting
- Call scam pattern detection
- Integration with real UPI APIs

---

**Built for Hackathon** | Detects fraud BEFORE money is lost 🚀

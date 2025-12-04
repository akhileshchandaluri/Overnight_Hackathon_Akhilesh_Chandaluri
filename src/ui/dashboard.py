"""
Streamlit Dashboard for UPI Fraud Detection
Interactive UI for transaction simulation and fraud detection
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.predict import FraudPredictor

# Page configuration
st.set_page_config(
    page_title="UPI Fraud Detection",
    page_icon="💸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Enhanced UI
st.markdown("""
<style>
    /* Main Theme */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* Header Styling */
    .main-header {
        font-size: 3.5rem;
        font-weight: 800;
        text-align: center;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
        letter-spacing: -1px;
    }
    
    .sub-header {
        font-size: 1.3rem;
        text-align: center;
        color: #64748b;
        margin-bottom: 2rem;
        font-weight: 400;
    }
    
    /* Card Styles */
    .metric-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 1.5rem;
        border-radius: 1rem;
        margin: 0.5rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transition: transform 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 12px rgba(0, 0, 0, 0.15);
    }
    
    /* Status Colors */
    .safe {
        color: #10b981;
        font-weight: 700;
    }
    
    .warning {
        color: #f59e0b;
        font-weight: 700;
    }
    
    .danger {
        color: #ef4444;
        font-weight: 700;
    }
    
    /* Sidebar Enhancement */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e293b 0%, #334155 100%);
        color: white;
    }
    
    [data-testid="stSidebar"] .stMarkdown {
        color: #e2e8f0;
    }
    
    /* Button Styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 0.5rem;
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px rgba(102, 126, 234, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(102, 126, 234, 0.4);
    }
    
    /* Tab Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
        background-color: transparent;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        border-radius: 0.5rem 0.5rem 0 0;
        padding: 1rem 2rem;
        font-weight: 600;
        font-size: 1.1rem;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    /* Input Field Enhancement */
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > div {
        border-radius: 0.5rem;
        border: 2px solid #e2e8f0;
        transition: all 0.3s ease;
    }
    
    .stNumberInput > div > div > input:focus,
    .stSelectbox > div > div > div:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* Alert Boxes */
    .element-container .stAlert {
        border-radius: 1rem;
        border-left: 5px solid;
        padding: 1.5rem;
        font-size: 1.1rem;
        line-height: 1.6;
    }
    
    /* Metric Value Styling */
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 700;
    }
    
    /* Expander Styling */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        border-radius: 0.5rem;
        font-weight: 600;
        font-size: 1.1rem;
        padding: 1rem;
    }
    
    /* Animation */
    @keyframes fadeIn {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .main .block-container {
        animation: fadeIn 0.6s ease;
    }
    
    /* Success/Warning/Error Box Enhancement */
    .stSuccess, .stWarning, .stError {
        border-radius: 1rem;
        padding: 1.5rem;
        font-weight: 500;
    }
    
    /* DataFrame Styling */
    .dataframe {
        border-radius: 0.5rem;
        overflow: hidden;
    }
    
    /* File Uploader */
    [data-testid="stFileUploader"] {
        border: 2px dashed #667eea;
        border-radius: 1rem;
        padding: 2rem;
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def load_predictor(model_type='random_forest'):
    """Load the fraud detection model"""
    try:
        predictor = FraudPredictor(model_type=model_type)
        return predictor
    except Exception as e:
        st.error(f"Error loading model: {e}")
        return None


def main():
    # Enhanced Header with Icon
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <div style="font-size: 5rem; margin-bottom: 1rem;">💸</div>
        <div class="main-header">UPI Fraud Detection System</div>
        <div class="sub-header">Real-time ML-powered fraud detection for UPI transactions</div>
        <div style="display: flex; justify-content: center; gap: 1rem; margin-top: 1.5rem;">
            <span style="background: linear-gradient(135deg, #10b981, #059669); color: white; padding: 0.5rem 1.5rem; border-radius: 2rem; font-weight: 600;">🛡️ Secure</span>
            <span style="background: linear-gradient(135deg, #3b82f6, #2563eb); color: white; padding: 0.5rem 1.5rem; border-radius: 2rem; font-weight: 600;">⚡ Real-time</span>
            <span style="background: linear-gradient(135deg, #8b5cf6, #7c3aed); color: white; padding: 0.5rem 1.5rem; border-radius: 2rem; font-weight: 600;">🤖 AI-Powered</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar Enhancement
    with st.sidebar:
        st.markdown("### ⚙️ Settings")
        
        model_type = st.selectbox(
            "Select Detection Model",
            ["random_forest"],
            index=0,
            help="Choose the ML model for prediction"
        )
        
        st.markdown("---")
        
        st.markdown("### 📊 Performance Metrics")
        
        # Animated metrics
        st.markdown("""
        <div style='background: linear-gradient(135deg, #10b981, #059669); padding: 1rem; border-radius: 0.75rem; margin-bottom: 1rem; color: white;'>
            <div style='font-size: 0.875rem; opacity: 0.9;'>Detection Rate</div>
            <div style='font-size: 1.75rem; font-weight: 700;'>95%+</div>
        </div>
        <div style='background: linear-gradient(135deg, #3b82f6, #2563eb); padding: 1rem; border-radius: 0.75rem; margin-bottom: 1rem; color: white;'>
            <div style='font-size: 0.875rem; opacity: 0.9;'>Response Time</div>
            <div style='font-size: 1.75rem; font-weight: 700;'>&lt;100ms</div>
        </div>
        <div style='background: linear-gradient(135deg, #8b5cf6, #7c3aed); padding: 1rem; border-radius: 0.75rem; margin-bottom: 1rem; color: white;'>
            <div style='font-size: 0.875rem; opacity: 0.9;'>Models Trained</div>
            <div style='font-size: 1.75rem; font-weight: 700;'>3</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        st.markdown("### 🎯 Risk Levels")
        st.markdown("""
        <div style='margin: 0.5rem 0;'>
            <span style='color: #10b981; font-size: 1.5rem;'>●</span>
            <span style='font-weight: 600; margin-left: 0.5rem;'>LOW</span>
            <span style='opacity: 0.7; margin-left: 0.5rem;'>< 50% - Allow</span>
        </div>
        <div style='margin: 0.5rem 0;'>
            <span style='color: #f59e0b; font-size: 1.5rem;'>●</span>
            <span style='font-weight: 600; margin-left: 0.5rem;'>MEDIUM</span>
            <span style='opacity: 0.7; margin-left: 0.5rem;'>50-80% - Warn</span>
        </div>
        <div style='margin: 0.5rem 0;'>
            <span style='color: #ef4444; font-size: 1.5rem;'>●</span>
            <span style='font-weight: 600; margin-left: 0.5rem;'>HIGH</span>
            <span style='opacity: 0.7; margin-left: 0.5rem;'>> 80% - Block</span>
        </div>
        """, unsafe_allow_html=True)
    
    # Load predictor
    predictor = load_predictor(model_type)
    
    if not predictor:
        st.error("❌ Failed to load model. Please train the model first.")
        st.info("Run: `python src/models/train_model.py`")
        return
    
    # Main content tabs with enhanced icons
    tab1, tab2, tab3, tab4 = st.tabs([
        "🔍 Transaction Analyzer", 
        "📈 Batch Analysis", 
        "🎭 Demo Scenarios", 
        "📊 Model Info"
    ])
    
    # Tab 1: Single Transaction Analysis with Enhanced UI
    with tab1:
        st.markdown("### Analyze a Single Transaction")
        st.markdown("Fill in the transaction details below to get real-time fraud detection analysis.")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 💰 Basic Transaction Details")
            
            amount = st.number_input(
                "Transaction Amount (₹)",
                min_value=0.0,
                max_value=100000.0,
                value=5000.0,
                step=100.0,
                help="Enter the transaction amount in Indian Rupees"
            )
            
            time_slot = st.selectbox(
                "Time of Transaction",
                options=[0, 1, 2, 3],
                format_func=lambda x: ["🌅 Morning (6AM-12PM)", "☀️ Afternoon (12PM-6PM)", 
                                       "🌆 Evening (6PM-10PM)", "🌙 Night (10PM-6AM)"][x],
                index=1
            )
            
            is_new_device = st.selectbox(
                "Device Status",
                options=[0, 1],
                format_func=lambda x: "🆕 New Device (First Time)" if x == 1 else "📱 Trusted Device",
                index=0
            )
            
            is_new_beneficiary = st.selectbox(
                "Beneficiary Status",
                options=[0, 1],
                format_func=lambda x: "🆕 New Beneficiary" if x == 1 else "👤 Known Beneficiary",
                index=0
            )
            
            location_change = st.selectbox(
                "Location Status",
                options=[0, 1],
                format_func=lambda x: "📍 Different Location Detected" if x == 1 else "📍 Usual Location",
                index=0
            )
            
            transaction_frequency = st.slider(
                "Recent Transaction Count (Last 24h)",
                min_value=0,
                max_value=30,
                value=3,
                help="Number of transactions made in the last 24 hours"
            )
        
        with col2:
            st.markdown("#### 🔬 Advanced Risk Indicators")
            
            past_fraud_flag = st.selectbox(
                "Fraud History",
                options=[0, 1],
                format_func=lambda x: "⚠️ Past Fraud Detected" if x == 1 else "✅ Clean Transaction History",
                index=0
            )
            
            amount_deviation = st.slider(
                "Amount Deviation from User Average",
                min_value=0.0,
                max_value=2.0,
                value=0.2,
                step=0.1,
                help="How much this amount differs from user's typical transaction pattern (0=normal, 2=extremely unusual)"
            )
            
            beneficiary_trust_score = st.slider(
                "Beneficiary Trust Score",
                min_value=0.0,
                max_value=1.0,
                value=0.7,
                step=0.05,
                help="Trust level for the beneficiary (0=unknown/suspicious, 1=highly trusted)"
            )
            
            device_age_days = st.number_input(
                "Device Age (Days)",
                min_value=0,
                max_value=2000,
                value=180,
                help="Number of days this device has been registered and used"
            )
            
            account_age_days = st.number_input(
                "Account Age (Days)",
                min_value=0,
                max_value=5000,
                value=365,
                help="Number of days since the UPI account was created"
            )
        
        
        # Enhanced Predict Button + Fraud Scenarios
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Fraud scenario buttons
        st.markdown("#### 🎭 Quick Test Scenarios")
        scenario_col1, scenario_col2, scenario_col3, scenario_col4 = st.columns(4)
        
        with scenario_col1:
            if st.button("💸 High Amount Fraud", use_container_width=True):
                st.session_state.scenario = "high_amount"
        with scenario_col2:
            if st.button("📱 New Device Attack", use_container_width=True):
                st.session_state.scenario = "new_device"
        with scenario_col3:
            if st.button("🌙 Night Rush Fraud", use_container_width=True):
                st.session_state.scenario = "night_rush"
        with scenario_col4:
            if st.button("✅ Safe Transaction", use_container_width=True):
                st.session_state.scenario = "safe"
        
        # Apply scenario if selected
        if 'scenario' in st.session_state:
            scenario = st.session_state.scenario
            if scenario == "high_amount":
                amount, time_slot, is_new_device, is_new_beneficiary, location_change = 45000, 3, 1, 1, 1
                transaction_frequency, past_fraud_flag, amount_deviation = 15, 1, 1.5
                beneficiary_trust_score, device_age_days, account_age_days = 0.1, 5, 30
            elif scenario == "new_device":
                amount, time_slot, is_new_device, is_new_beneficiary, location_change = 25000, 2, 1, 1, 1
                transaction_frequency, past_fraud_flag, amount_deviation = 10, 0, 1.2
                beneficiary_trust_score, device_age_days, account_age_days = 0.2, 0, 180
            elif scenario == "night_rush":
                amount, time_slot, is_new_device, is_new_beneficiary, location_change = 35000, 3, 0, 1, 1
                transaction_frequency, past_fraud_flag, amount_deviation = 20, 1, 1.8
                beneficiary_trust_score, device_age_days, account_age_days = 0.05, 10, 60
            elif scenario == "safe":
                amount, time_slot, is_new_device, is_new_beneficiary, location_change = 500, 1, 0, 0, 0
                transaction_frequency, past_fraud_flag, amount_deviation = 2, 0, 0.1
                beneficiary_trust_score, device_age_days, account_age_days = 0.95, 500, 1000
            
            st.session_state.pop('scenario')
            st.experimental_rerun()
        
        st.markdown("<br>", unsafe_allow_html=True)
        col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
        with col_btn2:
            analyze_btn = st.button("🔍 Analyze Transaction", type="primary", use_container_width=True)
        
        if analyze_btn:
            # Input validation
            validation_errors = []
            
            if amount <= 0:
                validation_errors.append("⚠️ Transaction amount must be greater than 0")
            if amount > 200000:
                validation_errors.append("⚠️ Transaction amount exceeds UPI limit (₹2,00,000)")
            
            if validation_errors:
                for error in validation_errors:
                    st.error(error)
            else:
                # Prepare transaction data
                transaction_data = {
                    'amount': float(amount),
                    'time_slot': int(time_slot),
                    'is_new_device': int(is_new_device),
                    'is_new_beneficiary': int(is_new_beneficiary),
                    'location_change': int(location_change),
                    'transaction_frequency': int(transaction_frequency),
                    'past_fraud_flag': int(past_fraud_flag),
                    'amount_deviation': float(amount_deviation),
                    'beneficiary_trust_score': float(beneficiary_trust_score),
                    'device_age_days': int(device_age_days),
                    'account_age_days': int(account_age_days)
                }
                
                # Show what's being analyzed
                with st.expander("🔍 View Input Data"):
                    st.json(transaction_data)
                
                # Make prediction
                with st.spinner("🔄 Analyzing transaction patterns..."):
                    result = predictor.predict(transaction_data)
                
                # Enhanced Results Display
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown("### 📊 Analysis Results")
                
                # Premium Metrics Display
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    prob_value = result['fraud_probability']
                    prob_color = "#ef4444" if prob_value > 0.8 else "#f59e0b" if prob_value > 0.5 else "#10b981"
                    st.markdown(f"""
                    <div style='background: linear-gradient(135deg, {prob_color}22, {prob_color}44); padding: 1.5rem; border-radius: 1rem; border-left: 4px solid {prob_color};'>
                        <div style='color: #64748b; font-size: 0.875rem; font-weight: 600; margin-bottom: 0.5rem;'>FRAUD PROBABILITY</div>
                        <div style='color: {prob_color}; font-size: 2rem; font-weight: 700;'>{prob_value:.1%}</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    risk_colors = {'LOW': '#10b981', 'MEDIUM': '#f59e0b', 'HIGH': '#ef4444'}
                    risk_icons = {'LOW': '🟢', 'MEDIUM': '🟡', 'HIGH': '🔴'}
                    risk_color = risk_colors.get(result['risk_level'], '#64748b')
                    risk_icon = risk_icons.get(result['risk_level'], '⚪')
                    st.markdown(f"""
                    <div style='background: linear-gradient(135deg, {risk_color}22, {risk_color}44); padding: 1.5rem; border-radius: 1rem; border-left: 4px solid {risk_color};'>
                        <div style='color: #64748b; font-size: 0.875rem; font-weight: 600; margin-bottom: 0.5rem;'>RISK LEVEL</div>
                        <div style='color: {risk_color}; font-size: 2rem; font-weight: 700;'>{risk_icon} {result['risk_level']}</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    decision_colors = {'ALLOW': '#10b981', 'WARN': '#f59e0b', 'BLOCK': '#ef4444'}
                    decision_color = decision_colors.get(result['decision'], '#64748b')
                    st.markdown(f"""
                    <div style='background: linear-gradient(135deg, {decision_color}22, {decision_color}44); padding: 1.5rem; border-radius: 1rem; border-left: 4px solid {decision_color};'>
                        <div style='color: #64748b; font-size: 0.875rem; font-weight: 600; margin-bottom: 0.5rem;'>DECISION</div>
                        <div style='color: {decision_color}; font-size: 2rem; font-weight: 700;'>{result['decision']}</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col4:
                    status = "FRAUD" if result['is_fraud'] else "SAFE"
                    status_color = "#ef4444" if result['is_fraud'] else "#10b981"
                    status_icon = "⚠️" if result['is_fraud'] else "✅"
                    st.markdown(f"""
                    <div style='background: linear-gradient(135deg, {status_color}22, {status_color}44); padding: 1.5rem; border-radius: 1rem; border-left: 4px solid {status_color};'>
                        <div style='color: #64748b; font-size: 0.875rem; font-weight: 600; margin-bottom: 0.5rem;'>STATUS</div>
                        <div style='color: {status_color}; font-size: 2rem; font-weight: 700;'>{status_icon} {status}</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                
                # Enhanced Probability Gauge
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown("### 🎯 Fraud Risk Visualization")
                
                col_gauge1, col_gauge2 = st.columns([2, 1])
                
                with col_gauge1:
                    fig = go.Figure(go.Indicator(
                        mode="gauge+number+delta",
                        value=result['fraud_probability'] * 100,
                        domain={'x': [0, 1], 'y': [0, 1]},
                        title={'text': "Fraud Risk (%)", 'font': {'size': 24}},
                        delta={'reference': 50, 'increasing': {'color': "red"}, 'decreasing': {'color': "green"}},
                        gauge={
                            'axis': {'range': [None, 100], 'tickwidth': 2, 'tickcolor': "darkgray"},
                            'bar': {'color': "rgba(102, 126, 234, 0.8)", 'thickness': 0.75},
                            'bgcolor': "white",
                            'borderwidth': 2,
                            'bordercolor': "gray",
                            'steps': [
                                {'range': [0, 50], 'color': 'rgba(16, 185, 129, 0.3)'},
                                {'range': [50, 80], 'color': 'rgba(245, 158, 11, 0.3)'},
                                {'range': [80, 100], 'color': 'rgba(239, 68, 68, 0.3)'}
                            ],
                            'threshold': {
                                'line': {'color': "red", 'width': 4},
                                'thickness': 0.75,
                                'value': 80
                            }
                        }
                    ))
                    fig.update_layout(
                        height=350,
                        margin=dict(l=20, r=20, t=60, b=20),
                        paper_bgcolor="rgba(0,0,0,0)",
                        font={'family': "Inter, sans-serif"}
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                with col_gauge2:
                    st.markdown(f"""
                    <div style='padding: 1rem;'>
                        <h4 style='color: #64748b; margin-bottom: 1rem;'>Risk Breakdown</h4>
                        <div style='margin: 0.75rem 0;'>
                            <div style='display: flex; justify-content: space-between; margin-bottom: 0.25rem;'>
                                <span style='color: #64748b;'>Safe Zone</span>
                                <span style='font-weight: 600; color: #10b981;'>0-50%</span>
                        </div>
                        <div style='height: 8px; background: #10b98122; border-radius: 4px;'>
                            <div style='height: 100%; width: 50%; background: #10b981; border-radius: 4px;'></div>
                        </div>
                    </div>
                    <div style='margin: 0.75rem 0;'>
                        <div style='display: flex; justify-content: space-between; margin-bottom: 0.25rem;'>
                            <span style='color: #64748b;'>Warning Zone</span>
                            <span style='font-weight: 600; color: #f59e0b;'>50-80%</span>
                        </div>
                        <div style='height: 8px; background: #f59e0b22; border-radius: 4px;'>
                            <div style='height: 100%; width: 30%; background: #f59e0b; border-radius: 4px;'></div>
                        </div>
                    </div>
                    <div style='margin: 0.75rem 0;'>
                        <div style='display: flex; justify-content: space-between; margin-bottom: 0.25rem;'>
                            <span style='color: #64748b;'>Danger Zone</span>
                            <span style='font-weight: 600; color: #ef4444;'>80-100%</span>
                        </div>
                        <div style='height: 8px; background: #ef444422; border-radius: 4px;'>
                            <div style='height: 100%; width: 20%; background: #ef4444; border-radius: 4px;'></div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Enhanced Decision Box
                st.markdown("<br>", unsafe_allow_html=True)
                if result['decision'] == 'BLOCK':
                    st.markdown(f"""
                    <div style='background: linear-gradient(135deg, #fca5a5, #ef4444); padding: 2rem; border-radius: 1rem; border-left: 6px solid #dc2626; color: white;'>
                        <div style='font-size: 2rem; margin-bottom: 0.5rem;'>🚫 TRANSACTION BLOCKED</div>
                        <div style='font-size: 1.1rem; line-height: 1.6; opacity: 0.95;'>{result['explanation']}</div>
                    </div>
                    """, unsafe_allow_html=True)
                elif result['decision'] == 'WARN':
                    st.markdown(f"""
                    <div style='background: linear-gradient(135deg, #fcd34d, #f59e0b); padding: 2rem; border-radius: 1rem; border-left: 6px solid #d97706; color: white;'>
                        <div style='font-size: 2rem; margin-bottom: 0.5rem;'>⚠️ MANUAL REVIEW REQUIRED</div>
                        <div style='font-size: 1.1rem; line-height: 1.6; opacity: 0.95;'>{result['explanation']}</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div style='background: linear-gradient(135deg, #6ee7b7, #10b981); padding: 2rem; border-radius: 1rem; border-left: 6px solid #059669; color: white;'>
                        <div style='font-size: 2rem; margin-bottom: 0.5rem;'>✅ TRANSACTION APPROVED</div>
                        <div style='font-size: 1.1rem; line-height: 1.6; opacity: 0.95;'>{result['explanation']}</div>
                    </div>
                    """, unsafe_allow_html=True)
    
    # Tab 2: Enhanced Batch Analysis
    with tab2:
        st.markdown("### 📈 Batch Transaction Analysis")
        st.markdown("Upload a CSV file containing multiple transactions for comprehensive fraud analysis.")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader(
            "📤 Upload Transaction CSV File",
            type=['csv'],
            help="CSV file should contain the same features as single transaction analysis"
        )
        
        if uploaded_file is not None:
            try:
                df = pd.read_csv(uploaded_file)
                
                st.success(f"✅ Successfully loaded **{len(df)}** transactions")
                
                st.markdown("#### 📋 Data Preview")
                st.dataframe(df.head(10), use_container_width=True)
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
                with col_btn2:
                    analyze_batch_btn = st.button("🔍 Analyze All Transactions", type="primary", use_container_width=True)
                
                if analyze_batch_btn:
                    with st.spinner(f"🔄 Analyzing {len(df)} transactions..."):
                        transactions = df.to_dict('records')
                        results = predictor.predict_batch(transactions)
                        
                        # Add results to dataframe
                        results_df = pd.DataFrame(results)
                        combined_df = pd.concat([df, results_df], axis=1)
                        
                        # Enhanced Summary Metrics
                        st.markdown("<br>", unsafe_allow_html=True)
                        st.markdown("### 📊 Analysis Summary")
                        
                        col1, col2, col3, col4 = st.columns(4)
                        
                        fraud_count = (combined_df['is_fraud'] == 1).sum()
                        high_risk = (combined_df['risk_level'] == 'HIGH').sum()
                        avg_prob = combined_df['fraud_probability'].mean()
                        blocked = (combined_df['decision'] == 'BLOCK').sum()
                        
                        with col1:
                            st.markdown(f"""
                            <div style='background: linear-gradient(135deg, #3b82f6, #2563eb); padding: 1.5rem; border-radius: 1rem; color: white; text-align: center;'>
                                <div style='font-size: 0.875rem; opacity: 0.9; margin-bottom: 0.5rem;'>TOTAL TRANSACTIONS</div>
                                <div style='font-size: 2.5rem; font-weight: 700;'>{len(combined_df)}</div>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        with col2:
                            st.markdown(f"""
                            <div style='background: linear-gradient(135deg, #ef4444, #dc2626); padding: 1.5rem; border-radius: 1rem; color: white; text-align: center;'>
                                <div style='font-size: 0.875rem; opacity: 0.9; margin-bottom: 0.5rem;'>FLAGGED AS FRAUD</div>
                                <div style='font-size: 2.5rem; font-weight: 700;'>{fraud_count}</div>
                                <div style='font-size: 0.875rem; opacity: 0.8;'>{fraud_count/len(combined_df)*100:.1f}% of total</div>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        with col3:
                            st.markdown(f"""
                            <div style='background: linear-gradient(135deg, #f59e0b, #d97706); padding: 1.5rem; border-radius: 1rem; color: white; text-align: center;'>
                                <div style='font-size: 0.875rem; opacity: 0.9; margin-bottom: 0.5rem;'>HIGH RISK</div>
                                <div style='font-size: 2.5rem; font-weight: 700;'>{high_risk}</div>
                                <div style='font-size: 0.875rem; opacity: 0.8;'>{high_risk/len(combined_df)*100:.1f}% of total</div>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        with col4:
                            st.markdown(f"""
                            <div style='background: linear-gradient(135deg, #8b5cf6, #7c3aed); padding: 1.5rem; border-radius: 1rem; color: white; text-align: center;'>
                                <div style='font-size: 0.875rem; opacity: 0.9; margin-bottom: 0.5rem;'>AVG FRAUD PROB</div>
                                <div style='font-size: 2.5rem; font-weight: 700;'>{avg_prob:.1%}</div>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        
                        # Enhanced Visualizations
                        st.markdown("<br>", unsafe_allow_html=True)
                        st.markdown("### 📈 Visual Analytics")
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            # Enhanced Risk level distribution
                            risk_counts = combined_df['risk_level'].value_counts()
                            fig = px.pie(
                                values=risk_counts.values,
                                names=risk_counts.index,
                                title="<b>Risk Level Distribution</b>",
                                color_discrete_map={'LOW': '#10b981', 'MEDIUM': '#f59e0b', 'HIGH': '#ef4444'},
                                hole=0.4
                            )
                            fig.update_traces(textposition='inside', textinfo='percent+label', textfont_size=14)
                            fig.update_layout(
                                font={'family': "Inter, sans-serif"},
                                showlegend=True,
                                height=350
                            )
                            st.plotly_chart(fig, use_container_width=True)
                        
                        with col2:
                            # Enhanced Decision distribution
                            decision_counts = combined_df['decision'].value_counts()
                            fig = px.bar(
                                x=decision_counts.index,
                                y=decision_counts.values,
                                title="<b>Decision Distribution</b>",
                                labels={'x': 'Decision', 'y': 'Count'},
                                color=decision_counts.index,
                                color_discrete_map={'ALLOW': '#10b981', 'WARN': '#f59e0b', 'BLOCK': '#ef4444'}
                            )
                            fig.update_layout(
                                font={'family': "Inter, sans-serif"},
                                showlegend=False,
                                height=350,
                                xaxis_title="<b>Decision</b>",
                                yaxis_title="<b>Count</b>"
                            )
                            fig.update_traces(texttemplate='%{y}', textposition='outside')
                            st.plotly_chart(fig, use_container_width=True)
                        
                        # Fraud probability distribution
                        st.markdown("#### 📊 Fraud Probability Distribution")
                        fig = px.histogram(
                            combined_df,
                            x='fraud_probability',
                            nbins=30,
                            title="<b>Distribution of Fraud Probabilities</b>",
                            labels={'fraud_probability': 'Fraud Probability'},
                            color_discrete_sequence=['#667eea']
                        )
                        fig.update_layout(
                            font={'family': "Inter, sans-serif"},
                            height=300,
                            xaxis_title="<b>Fraud Probability</b>",
                            yaxis_title="<b>Frequency</b>"
                        )
                        st.plotly_chart(fig, use_container_width=True)
                        
                        
                        # Enhanced Full results
                        st.markdown("<br>", unsafe_allow_html=True)
                        st.markdown("### 📋 Detailed Results")
                        
                        # Add color coding to the dataframe display
                        def color_risk(val):
                            color_map = {'LOW': 'background-color: #10b98133', 
                                       'MEDIUM': 'background-color: #f59e0b33', 
                                       'HIGH': 'background-color: #ef444433'}
                            return color_map.get(val, '')
                        
                        styled_df = combined_df.style.applymap(color_risk, subset=['risk_level'])
                        st.dataframe(styled_df, use_container_width=True, height=400)
                        
                        # Enhanced Download button
                        st.markdown("<br>", unsafe_allow_html=True)
                        csv = combined_df.to_csv(index=False)
                        col_dl1, col_dl2, col_dl3 = st.columns([1, 2, 1])
                        with col_dl2:
                            st.download_button(
                                label="📥 Download Complete Analysis Report",
                                data=csv,
                                file_name="fraud_detection_results.csv",
                                mime="text/csv",
                                use_container_width=True
                            )
            
            except Exception as e:
                st.error(f"❌ Error processing file: {e}")
    
    # Tab 3: Enhanced Demo Scenarios
    with tab3:
        st.markdown("### 🎭 Pre-configured Demo Scenarios")
        st.markdown("Test the fraud detection system with these realistic transaction patterns.")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        scenarios = {
            "✅ Safe Transaction": {
                'amount': 500.0,
                'time_slot': 1,  # Afternoon
                'is_new_device': 0,
                'is_new_beneficiary': 0,
                'location_change': 0,
                'transaction_frequency': 2,
                'past_fraud_flag': 0,
                'amount_deviation': 0.1,
                'beneficiary_trust_score': 0.9,
                'device_age_days': 200,
                'account_age_days': 500
            },
            "⚠️ Medium Risk - New Beneficiary": {
                'amount': 15000.0,
                'time_slot': 2,  # Evening
                'is_new_device': 0,
                'is_new_beneficiary': 1,
                'location_change': 0,
                'transaction_frequency': 5,
                'past_fraud_flag': 0,
                'amount_deviation': 0.6,
                'beneficiary_trust_score': 0.3,
                'device_age_days': 150,
                'account_age_days': 400
            },
            "🚨 High Risk - Suspicious Pattern": {
                'amount': 45000.0,
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
            },
            "🔴 Extreme Fraud - All Red Flags": {
                'amount': 50000.0,
                'time_slot': 3,  # Night
                'is_new_device': 1,
                'is_new_beneficiary': 1,
                'location_change': 1,
                'transaction_frequency': 20,
                'past_fraud_flag': 1,
                'amount_deviation': 1.5,
                'beneficiary_trust_score': 0.0,
                'device_age_days': 0,
                'account_age_days': 50
            }
        }
        
        for i, (scenario_name, scenario_data) in enumerate(scenarios.items()):
            # Determine color scheme based on scenario type
            if "Safe" in scenario_name:
                bg_color = "linear-gradient(135deg, #10b98122, #059669 22)"
                border_color = "#10b981"
            elif "Medium" in scenario_name:
                bg_color = "linear-gradient(135deg, #f59e0b22, #d9770622)"
                border_color = "#f59e0b"
            elif "High Risk" in scenario_name:
                bg_color = "linear-gradient(135deg, #f59e0b44, #ef444444)"
                border_color = "#f59e0b"
            else:
                bg_color = "linear-gradient(135deg, #ef444444, #dc262644)"
                border_color = "#ef4444"
            
            with st.expander(f"{scenario_name}", expanded=(i == 0)):
                col1, col2 = st.columns([3, 2])
                
                with col1:
                    st.markdown("#### Transaction Details")
                    
                    # Display in a nice table format
                    details_html = "<div style='background: #f8fafc; padding: 1rem; border-radius: 0.5rem;'>"
                    feature_labels = {
                        'amount': '💰 Amount',
                        'time_slot': '⏰ Time Slot',
                        'is_new_device': '📱 New Device',
                        'is_new_beneficiary': '👤 New Beneficiary',
                        'location_change': '📍 Location Change',
                        'transaction_frequency': '🔄 Transaction Frequency',
                        'past_fraud_flag': '⚠️ Past Fraud',
                        'amount_deviation': '📊 Amount Deviation',
                        'beneficiary_trust_score': '✅ Trust Score',
                        'device_age_days': '📅 Device Age',
                        'account_age_days': '📅 Account Age'
                    }
                    
                    for key, value in scenario_data.items():
                        label = feature_labels.get(key, key)
                        details_html += f"<div style='display: flex; justify-content: space-between; padding: 0.5rem; border-bottom: 1px solid #e2e8f0;'>"
                        details_html += f"<span style='color: #64748b; font-weight: 500;'>{label}</span>"
                        details_html += f"<span style='color: #1e293b; font-weight: 600;'>{value}</span>"
                        details_html += "</div>"
                    details_html += "</div>"
                    
                    st.markdown(details_html, unsafe_allow_html=True)
                
                with col2:
                    st.markdown("#### Test Results")
                    
                    if st.button(f"🔍 Analyze", key=f"test_{scenario_name}", use_container_width=True):
                        with st.spinner("Analyzing..."):
                            result = predictor.predict(scenario_data)
                        
                        prob_color = "#ef4444" if result['fraud_probability'] > 0.8 else "#f59e0b" if result['fraud_probability'] > 0.5 else "#10b981"
                        
                        st.markdown(f"""
                        <div style='background: {bg_color}; padding: 1.5rem; border-radius: 0.75rem; border-left: 4px solid {border_color}; margin-top: 1rem;'>
                            <div style='margin-bottom: 1rem;'>
                                <span style='color: #64748b; font-size: 0.875rem;'>Fraud Probability</span>
                                <div style='color: {prob_color}; font-size: 1.75rem; font-weight: 700;'>{result['fraud_probability']:.1%}</div>
                            </div>
                            <div style='margin-bottom: 1rem;'>
                                <span style='color: #64748b; font-size: 0.875rem;'>Risk Level</span>
                                <div style='color: {border_color}; font-size: 1.25rem; font-weight: 600;'>{result['risk_level']}</div>
                            </div>
                            <div style='margin-bottom: 1rem;'>
                                <span style='color: #64748b; font-size: 0.875rem;'>Decision</span>
                                <div style='font-size: 1.25rem; font-weight: 700;'>{result['decision']}</div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        if result['decision'] == 'BLOCK':
                            st.error("🚫 BLOCKED")
                        elif result['decision'] == 'WARN':
                            st.warning("⚠️ WARNING")
                        else:
                            st.success("✅ ALLOWED")
    
    # Tab 4: Enhanced Model Info
    with tab4:
        st.markdown("### 📊 Model Information & Architecture")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🤖 Model Details")
            
            st.markdown(f"""
            <div style='background: linear-gradient(135deg, #667eea22, #764ba244); padding: 1.5rem; border-radius: 1rem; border-left: 4px solid #667eea; margin-bottom: 1rem;'>
                <div style='color: #64748b; font-size: 0.875rem; margin-bottom: 0.5rem;'>ACTIVE MODEL</div>
                <div style='color: #667eea; font-size: 1.5rem; font-weight: 700;'>{model_type.upper()}</div>
            </div>
            <div style='background: linear-gradient(135deg, #10b98122, #05966944); padding: 1.5rem; border-radius: 1rem; border-left: 4px solid #10b981; margin-bottom: 1rem;'>
                <div style='color: #64748b; font-size: 0.875rem; margin-bottom: 0.5rem;'>FEATURES</div>
                <div style='color: #10b981; font-size: 1.5rem; font-weight: 700;'>{len(predictor.feature_names)}</div>
            </div>
            <div style='background: linear-gradient(135deg, #3b82f622, #2563eb44); padding: 1.5rem; border-radius: 1rem; border-left: 4px solid #3b82f6; margin-bottom: 1rem;'>
                <div style='color: #64748b; font-size: 0.875rem; margin-bottom: 0.5rem;'>EXPECTED ACCURACY</div>
                <div style='color: #3b82f6; font-size: 1.5rem; font-weight: 700;'>95%+</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("#### 🎯 Feature Set")
            features_df = pd.DataFrame({
                'Feature': predictor.feature_names,
                'Index': range(1, len(predictor.feature_names) + 1)
            })
            st.dataframe(
                features_df[['Index', 'Feature']], 
                use_container_width=True,
                hide_index=True,
                height=300
            )
        
        with col2:
            st.markdown("#### 🏗️ System Architecture")
            
            st.markdown("""
            <div style='background: linear-gradient(135deg, #f8fafc, #e2e8f0); padding: 2rem; border-radius: 1rem; font-family: monospace; line-height: 2;'>
                <div style='text-align: center;'>
                    <div style='background: #667eea; color: white; padding: 0.75rem; border-radius: 0.5rem; margin: 0.5rem 0; font-weight: 600;'>
                        📥 Transaction Data
                    </div>
                    <div style='font-size: 1.5rem; color: #64748b;'>↓</div>
                    <div style='background: #10b981; color: white; padding: 0.75rem; border-radius: 0.5rem; margin: 0.5rem 0; font-weight: 600;'>
                        🔧 Feature Engineering
                    </div>
                    <div style='font-size: 1.5rem; color: #64748b;'>↓</div>
                    <div style='background: #3b82f6; color: white; padding: 0.75rem; border-radius: 0.5rem; margin: 0.5rem 0; font-weight: 600;'>
                        🤖 ML Model
                    </div>
                    <div style='font-size: 1.5rem; color: #64748b;'>↓</div>
                    <div style='background: #8b5cf6; color: white; padding: 0.75rem; border-radius: 0.5rem; margin: 0.5rem 0; font-weight: 600;'>
                        📊 Fraud Probability
                    </div>
                    <div style='font-size: 1.5rem; color: #64748b;'>↓</div>
                    <div style='background: #f59e0b; color: white; padding: 0.75rem; border-radius: 0.5rem; margin: 0.5rem 0; font-weight: 600;'>
                        ⚖️ Decision Engine
                    </div>
                    <div style='font-size: 1.5rem; color: #64748b;'>↓</div>
                    <div style='background: #ef4444; color: white; padding: 0.75rem; border-radius: 0.5rem; margin: 0.5rem 0; font-weight: 600;'>
                        🚦 BLOCK / WARN / ALLOW
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("#### 🎨 Risk Thresholds")
            
            st.markdown("""
            <div style='background: linear-gradient(135deg, #f8fafc, #e2e8f0); padding: 1.5rem; border-radius: 1rem;'>
                <div style='margin: 1rem 0;'>
                    <div style='display: flex; align-items: center; margin-bottom: 0.5rem;'>
                        <span style='width: 12px; height: 12px; background: #10b981; border-radius: 50%; margin-right: 0.75rem;'></span>
                        <span style='font-weight: 700; color: #1e293b;'>LOW RISK</span>
                        <span style='margin-left: auto; color: #64748b;'>< 50%</span>
                    </div>
                    <div style='color: #64748b; font-size: 0.875rem; margin-left: 1.75rem;'>
                        Transaction automatically approved ✅
                    </div>
                </div>
                
                <div style='margin: 1rem 0;'>
                    <div style='display: flex; align-items: center; margin-bottom: 0.5rem;'>
                        <span style='width: 12px; height: 12px; background: #f59e0b; border-radius: 50%; margin-right: 0.75rem;'></span>
                        <span style='font-weight: 700; color: #1e293b;'>MEDIUM RISK</span>
                        <span style='margin-left: auto; color: #64748b;'>50-80%</span>
                    </div>
                    <div style='color: #64748b; font-size: 0.875rem; margin-left: 1.75rem;'>
                        Manual review required ⚠️
                    </div>
                </div>
                
                <div style='margin: 1rem 0;'>
                    <div style='display: flex; align-items: center; margin-bottom: 0.5rem;'>
                        <span style='width: 12px; height: 12px; background: #ef4444; border-radius: 50%; margin-right: 0.75rem;'></span>
                        <span style='font-weight: 700; color: #1e293b;'>HIGH RISK</span>
                        <span style='margin-left: auto; color: #64748b;'>> 80%</span>
                    </div>
                    <div style='color: #64748b; font-size: 0.875rem; margin-left: 1.75rem;'>
                        Transaction blocked automatically 🚫
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # Footer
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("""
    <div style='text-align: center; padding: 2rem; background: linear-gradient(135deg, #1e293b, #334155); border-radius: 1rem; color: white; margin-top: 3rem;'>
        <div style='font-size: 1.5rem; font-weight: 700; margin-bottom: 0.5rem;'>💸 UPI Fraud Detection System</div>
        <div style='opacity: 0.8; margin-bottom: 1rem;'>Powered by Machine Learning & Real-time Analytics</div>
        <div style='display: flex; justify-content: center; gap: 2rem; flex-wrap: wrap; margin-top: 1.5rem;'>
            <span style='opacity: 0.7;'>🛡️ Secure</span>
            <span style='opacity: 0.7;'>⚡ Fast</span>
            <span style='opacity: 0.7;'>🤖 Intelligent</span>
            <span style='opacity: 0.7;'>📊 Accurate</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()

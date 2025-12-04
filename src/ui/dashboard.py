"""
Stripe-inspired UPI Fraud Detection Dashboard
Clean, minimal, professional design
"""

import streamlit as st
import plotly.graph_objects as go
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.predict import FraudPredictor

# Page config
st.set_page_config(
    page_title="UPI Fraud Detection",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Stripe-inspired CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .main {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 2rem 3rem;
    }
    
    /* Sidebar with gradient */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0A2540 0%, #1e3a5f 100%);
        border-right: none;
        box-shadow: 4px 0 24px rgba(0, 0, 0, 0.1);
    }
    
    [data-testid="stSidebar"] h3 {
        color: #FFFFFF;
        font-weight: 600;
        font-size: 13px;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-bottom: 1.5rem;
    }
    
    /* Animated gradient buttons */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        background-size: 200% 200%;
        animation: gradientShift 3s ease infinite;
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        padding: 14px 28px;
        font-size: 15px;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) scale(1.02);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.5);
    }
    
    .stButton > button:active {
        transform: translateY(0) scale(0.98);
    }
    
    /* Glass morphism inputs */
    .stNumberInput > div > div > input,
    .stSelectbox > div > div {
        background: rgba(255, 255, 255, 0.9);
        backdrop-filter: blur(10px);
        border: 2px solid rgba(99, 91, 255, 0.2);
        border-radius: 10px;
        padding: 12px 16px;
        font-size: 15px;
        transition: all 0.3s ease;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    }
    
    .stNumberInput > div > div > input:focus,
    .stSelectbox > div > div:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.1), 0 4px 12px rgba(0, 0, 0, 0.1);
        transform: translateY(-1px);
    }
    
    /* Animated labels */
    label {
        color: #0A2540 !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    /* Hide Streamlit branding */
    #MainMenu, footer, header {visibility: hidden;}
    
    /* Smooth page entrance */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .element-container {
        animation: fadeInUp 0.6s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    /* Floating animation for cards */
    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
    }
    
    /* Pulse animation */
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    /* Gradient text */
    .gradient-text {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    /* Glassmorphism card effect */
    .glass-card {
        background: rgba(255, 255, 255, 0.7);
        backdrop-filter: blur(20px);
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.3);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    }
    
    /* Shimmer effect */
    @keyframes shimmer {
        0% { background-position: -1000px 0; }
        100% { background-position: 1000px 0; }
    }
    
    @keyframes slideRight {
        from {
            width: 0;
            opacity: 0;
        }
        to {
            opacity: 1;
        }
    }
    
    .shimmer {
        animation: shimmer 2s infinite linear;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
        background-size: 1000px 100%;
    }
    
    /* Hover glow effect */
    .glow-on-hover:hover {
        box-shadow: 0 0 20px rgba(102, 126, 234, 0.6),
                    0 0 40px rgba(102, 126, 234, 0.4),
                    0 0 60px rgba(102, 126, 234, 0.2);
    }
    
    /* Scrollbar styling */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(0, 0, 0, 0.05);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #667eea, #764ba2);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #764ba2, #667eea);
    }
    
    /* Better select dropdown styling */
    .stSelectbox > div > div > div {
        background: rgba(255, 255, 255, 0.9) !important;
        backdrop-filter: blur(10px);
        color: #0A2540 !important;
        font-weight: 500;
    }
    
    .stSelectbox [data-baseweb="select"] > div {
        background: rgba(255, 255, 255, 0.9) !important;
        color: #0A2540 !important;
    }
    
    /* Selected option visibility */
    .stSelectbox [role="button"] {
        color: #0A2540 !important;
        font-weight: 600 !important;
    }
    
    /* Dropdown menu items */
    [data-baseweb="menu"] {
        background: rgba(255, 255, 255, 0.95) !important;
        backdrop-filter: blur(20px);
        border-radius: 10px;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
    }
    
    [data-baseweb="menu"] > ul > li {
        color: #0A2540 !important;
        font-weight: 500;
        padding: 12px 16px;
    }
    
    [data-baseweb="menu"] > ul > li:hover {
        background: linear-gradient(135deg, #667eea15, #764ba215) !important;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def load_predictor():
    try:
        return FraudPredictor(model_type='random_forest')
    except Exception as e:
        st.error(f"Error loading model: {e}")
        return None

def main():
    # Animated Header with Gradient
    st.markdown("""
        <div style='text-align: center; margin-bottom: 3rem; animation: fadeInUp 0.8s ease-out;'>
            <h1 class='gradient-text' style='font-size: 56px; font-weight: 700; margin-bottom: 16px; letter-spacing: -0.03em;'>
                UPI Fraud Detection
            </h1>
            <p style='font-size: 20px; color: #425466; font-weight: 400; animation: fadeInUp 1s ease-out;'>
                Powered by advanced machine learning algorithms
            </p>
            <div style='margin-top: 24px; animation: fadeInUp 1.2s ease-out;'>
                <span style='display: inline-block; background: linear-gradient(135deg, #667eea, #764ba2); color: white; padding: 8px 20px; border-radius: 20px; font-size: 14px; font-weight: 600; margin: 0 8px; box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);'>
                    ⚡ Real-time Analysis
                </span>
                <span style='display: inline-block; background: linear-gradient(135deg, #f093fb, #f5576c); color: white; padding: 8px 20px; border-radius: 20px; font-size: 14px; font-weight: 600; margin: 0 8px; box-shadow: 0 4px 12px rgba(245, 87, 108, 0.3);'>
                    🛡️ 95%+ Accuracy
                </span>
                <span style='display: inline-block; background: linear-gradient(135deg, #4facfe, #00f2fe); color: white; padding: 8px 20px; border-radius: 20px; font-size: 14px; font-weight: 600; margin: 0 8px; box-shadow: 0 4px 12px rgba(79, 172, 254, 0.3);'>
                    🚀 AI-Powered
                </span>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Animated Sidebar
    with st.sidebar:
        st.markdown("### 🎯 Risk Levels")
        st.markdown("""
            <div style='margin: 1rem 0; padding: 16px; background: linear-gradient(135deg, #d4fc79 0%, #96e6a1 100%); border-radius: 12px; box-shadow: 0 4px 15px rgba(150, 230, 161, 0.3); transition: all 0.3s ease;' class='glow-on-hover'>
                <div style='font-weight: 700; color: #0A2540; font-size: 16px;'>✅ LOW RISK</div>
                <div style='color: #0A2540; font-size: 13px; margin-top: 6px; opacity: 0.8;'>< 30% probability</div>
            </div>
            <div style='margin: 1rem 0; padding: 16px; background: linear-gradient(135deg, #ffeaa7 0%, #fdcb6e 100%); border-radius: 12px; box-shadow: 0 4px 15px rgba(253, 203, 110, 0.3); transition: all 0.3s ease;' class='glow-on-hover'>
                <div style='font-weight: 700; color: #0A2540; font-size: 16px;'>⚠️ MEDIUM RISK</div>
                <div style='color: #0A2540; font-size: 13px; margin-top: 6px; opacity: 0.8;'>30-55% probability</div>
            </div>
            <div style='margin: 1rem 0; padding: 16px; background: linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%); border-radius: 12px; box-shadow: 0 4px 15px rgba(255, 107, 107, 0.3); transition: all 0.3s ease;' class='glow-on-hover'>
                <div style='font-weight: 700; color: white; font-size: 16px;'>🚫 HIGH RISK</div>
                <div style='color: white; font-size: 13px; margin-top: 6px; opacity: 0.9;'>> 55% probability</div>
            </div>
        """, unsafe_allow_html=True)
    
    # Load model
    predictor = load_predictor()
    if not predictor:
        st.error("Failed to load model")
        return
    
    # Input Section with Glass Card
    st.markdown("""
        <div style='background: rgba(255, 255, 255, 0.8); backdrop-filter: blur(20px); border-radius: 20px; padding: 32px; margin-bottom: 32px; box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1); border: 1px solid rgba(255, 255, 255, 0.3);'>
            <h3 style='color: #0A2540; font-weight: 700; margin-bottom: 24px; font-size: 24px;'>
                📝 Transaction Details
            </h3>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        amount = st.number_input("Amount (₹)", min_value=0.0, max_value=200000.0, value=5000.0, step=100.0)
        time_slot = st.selectbox("Time of Day", [0, 1, 2, 3, 4], format_func=lambda x: ['Morning', 'Afternoon', 'Evening', 'Night', 'Late Night'][x])
        is_new_device = st.selectbox("New Device", [0, 1], format_func=lambda x: 'Yes' if x else 'No')
        is_new_beneficiary = st.selectbox("New Beneficiary", [0, 1], format_func=lambda x: 'Yes' if x else 'No')
        location_change = st.selectbox("Location Changed", [0, 1], format_func=lambda x: 'Yes' if x else 'No')
        transaction_frequency = st.number_input("Transaction Frequency (24h)", 0, 100, 5)
        is_rural_user = st.selectbox("User Location Type", [0, 1], format_func=lambda x: 'Rural Area' if x else 'Urban/Metro')
    
    with col2:
        past_fraud_flag = st.selectbox("Past Fraud History", [0, 1], format_func=lambda x: 'Yes' if x else 'No')
        amount_deviation = st.number_input("Amount Deviation", 0.0, 10.0, 1.0, 0.1)
        beneficiary_trust_score = st.number_input("Beneficiary Trust Score", 0.0, 1.0, 0.5, 0.05)
        device_age_days = st.number_input("Device Age (days)", 0, 3000, 180)
        account_age_days = st.number_input("Account Age (days)", 0, 5000, 365)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Analyze button
    col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
    with col_btn2:
        if st.button("Analyze Transaction", use_container_width=True):
            # Prepare data
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
                'account_age_days': int(account_age_days),
                'is_rural_user': int(is_rural_user)
            }
            
            # Predict
            result = predictor.predict(transaction_data)
            prob = result['fraud_probability']
            risk = result['risk_level']
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Animated Results Header
            st.markdown("""
                <div style='text-align: center; margin-bottom: 32px; animation: fadeInUp 0.5s ease-out;'>
                    <h2 style='font-size: 32px; font-weight: 700; background: linear-gradient(135deg, #667eea, #764ba2); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>
                        Analysis Results
                    </h2>
                </div>
            """, unsafe_allow_html=True)
            
            # User Vulnerability Profile (NEW!)
            vuln_score = result['vulnerability_score']
            
            # Determine user profile
            if account_age_days < 30 and is_rural_user == 1:
                profile_type = "🌾 Rural First-Timer"
                profile_color = "#ef4444"
                profile_desc = "High-risk profile: New user from rural area requires extra protection"
            elif account_age_days < 90:
                profile_type = "🆕 New User"
                profile_color = "#f59e0b"
                profile_desc = "Moderate-risk profile: Recently joined user, monitoring recommended"
            elif device_age_days > 365 and account_age_days > 365:
                profile_type = "🔒 Tech-Savvy Regular"
                profile_color = "#10b981"
                profile_desc = "Low-risk profile: Experienced user with established patterns"
            else:
                profile_type = "👤 Regular User"
                profile_color = "#3b82f6"
                profile_desc = "Standard profile: Normal activity patterns"
            
            st.markdown(f"""
                <div style='background: linear-gradient(135deg, {profile_color}15, {profile_color}25); border-left: 6px solid {profile_color}; border-radius: 12px; padding: 20px; margin-bottom: 24px; animation: fadeInUp 0.5s ease-out;'>
                    <div style='display: flex; justify-content: space-between; align-items: center;'>
                        <div style='flex: 1;'>
                            <div style='font-size: 11px; color: #64748b; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 8px;'>User Vulnerability Profile</div>
                            <div style='font-size: 24px; font-weight: 800; color: {profile_color}; margin-bottom: 6px;'>{profile_type}</div>
                            <div style='font-size: 14px; color: #425466; line-height: 1.5;'>{profile_desc}</div>
                        </div>
                        <div style='text-align: center; padding: 0 24px; border-left: 2px solid {profile_color}40;'>
                            <div style='font-size: 11px; color: #64748b; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 8px;'>Vulnerability Score</div>
                            <div style='font-size: 42px; font-weight: 800; color: {profile_color};'>{vuln_score}</div>
                            <div style='font-size: 12px; color: #64748b; font-weight: 600;'>/ 100</div>
                        </div>
                    </div>
                    <div style='margin-top: 16px; width: 100%; height: 10px; background: rgba(0,0,0,0.08); border-radius: 5px; overflow: hidden;'>
                        <div style='width: {vuln_score}%; height: 100%; background: linear-gradient(90deg, {profile_color}, {profile_color}dd); animation: slideRight 1.2s ease-out;'></div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            # Pattern Alerts (NEW!)
            if 'pattern_alerts' in result and len(result['pattern_alerts']) > 0:
                st.markdown("""
                    <div style='text-align: center; margin: 24px 0 16px 0;'>
                        <h3 style='font-size: 22px; font-weight: 700; color: #dc2626;'>
                            🚨 Pattern Alerts Detected
                        </h3>
                    </div>
                """, unsafe_allow_html=True)
                
                for alert in result['pattern_alerts']:
                    severity_colors = {
                        'CRITICAL': ('#dc2626', '#fee2e2'),
                        'HIGH': ('#ef4444', '#fef2f2'),
                        'MEDIUM': ('#f59e0b', '#fef3c7')
                    }
                    alert_color, alert_bg = severity_colors.get(alert['severity'], ('#6b7280', '#f3f4f6'))
                    
                    pattern_names = {
                        'rapid_switching': '👥 Rapid Beneficiary Switching',
                        'vulnerable_user_night': '🌙 Vulnerable User Night Transaction'
                    }
                    pattern_name = pattern_names.get(alert['pattern'], alert['pattern'])
                    
                    st.markdown(f"""
                        <div style='background: linear-gradient(135deg, {alert_bg}, {alert_color}15); border-left: 6px solid {alert_color}; border-radius: 12px; padding: 20px; margin-bottom: 16px; animation: pulse 2s ease-in-out infinite;'>
                            <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;'>
                                <h4 style='color: {alert_color}; margin: 0; font-size: 18px; font-weight: 800;'>{pattern_name}</h4>
                                <span style='background: {alert_color}; color: white; padding: 6px 14px; border-radius: 8px; font-size: 11px; font-weight: 700; text-transform: uppercase;'>{alert['severity']}</span>
                            </div>
                            <p style='color: #0A2540; font-size: 15px; margin: 0 0 10px 0; line-height: 1.6;'>{alert['details']}</p>
                            <div style='display: flex; align-items: center; gap: 12px;'>
                                <div style='flex: 1; height: 8px; background: rgba(0,0,0,0.1); border-radius: 4px; overflow: hidden;'>
                                    <div style='width: {alert['score']}%; height: 100%; background: linear-gradient(90deg, {alert_color}, {alert_color}dd); animation: slideRight 1s ease-out;'></div>
                                </div>
                                <span style='font-size: 16px; font-weight: 800; color: {alert_color};'>{alert['score']}</span>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
            
            # Four column layout for metrics
            metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
            
            # Fraud Probability Metric
            with metric_col1:
                color = '#10b981' if risk == 'LOW' else ('#f59e0b' if risk == 'MEDIUM' else '#ef4444')
                st.markdown(f"""
                    <div style='background: linear-gradient(135deg, {color}20, {color}40); border-radius: 16px; padding: 20px; text-align: center; box-shadow: 0 8px 24px {color}30; animation: fadeInUp 0.6s ease-out; border: 2px solid {color};'>
                        <div style='font-size: 11px; color: #425466; font-weight: 600; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 10px;'>Fraud Probability</div>
                        <div style='font-size: 36px; font-weight: 800; color: {color}; margin-bottom: 6px;'>{prob*100:.1f}%</div>
                        <div style='width: 100%; height: 6px; background: rgba(0,0,0,0.1); border-radius: 3px; overflow: hidden; margin-top: 10px;'>
                            <div style='width: {prob*100}%; height: 100%; background: linear-gradient(90deg, {color}, {color}dd); animation: slideRight 1s ease-out;'></div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
            
            # Risk Level Metric
            with metric_col2:
                risk_icons = {'LOW': '✅', 'MEDIUM': '⚠️', 'HIGH': '🚫'}
                st.markdown(f"""
                    <div style='background: linear-gradient(135deg, {color}20, {color}40); border-radius: 16px; padding: 20px; text-align: center; box-shadow: 0 8px 24px {color}30; animation: fadeInUp 0.7s ease-out; border: 2px solid {color};'>
                        <div style='font-size: 11px; color: #425466; font-weight: 600; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 10px;'>Risk Level</div>
                        <div style='font-size: 36px; margin-bottom: 6px;'>{risk_icons[risk]}</div>
                        <div style='font-size: 20px; font-weight: 800; color: {color};'>{risk}</div>
                    </div>
                """, unsafe_allow_html=True)
            
            # Decision Metric
            with metric_col3:
                decision_icons = {'ALLOW': '✓', 'WARN': '!', 'BLOCK': '✗'}
                st.markdown(f"""
                    <div style='background: linear-gradient(135deg, {color}20, {color}40); border-radius: 16px; padding: 20px; text-align: center; box-shadow: 0 8px 24px {color}30; animation: fadeInUp 0.8s ease-out; border: 2px solid {color};'>
                        <div style='font-size: 11px; color: #425466; font-weight: 600; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 10px;'>Decision</div>
                        <div style='font-size: 36px; font-weight: 800; color: {color}; margin-bottom: 6px;'>{decision_icons.get(result['decision'], '?')}</div>
                        <div style='font-size: 18px; font-weight: 700; color: {color};'>{result['decision']}</div>
                    </div>
                """, unsafe_allow_html=True)
            
            # Fraud Type Metric (NEW!)
            with metric_col4:
                fraud_type = result['fraud_type']
                fraud_type_icons = {
                    'legitimate': '✅',
                    'high_amount': '💰',
                    'new_device': '📱',
                    'night_rush': '🌙',
                    'multiple_new': '👥'
                }
                fraud_type_names = {
                    'legitimate': 'Safe',
                    'high_amount': 'High Amount',
                    'new_device': 'Device Attack',
                    'night_rush': 'Night Rush',
                    'multiple_new': 'Multi-Beneficiary'
                }
                fraud_type_color = '#10b981' if fraud_type == 'legitimate' else '#dc2626'
                st.markdown(f"""
                    <div style='background: linear-gradient(135deg, {fraud_type_color}20, {fraud_type_color}40); border-radius: 16px; padding: 20px; text-align: center; box-shadow: 0 8px 24px {fraud_type_color}30; animation: fadeInUp 0.9s ease-out; border: 2px solid {fraud_type_color};'>
                        <div style='font-size: 11px; color: #425466; font-weight: 600; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 10px;'>Fraud Type</div>
                        <div style='font-size: 36px; margin-bottom: 6px;'>{fraud_type_icons.get(fraud_type, '❓')}</div>
                        <div style='font-size: 13px; font-weight: 700; color: {fraud_type_color};'>{fraud_type_names.get(fraud_type, fraud_type)}</div>
                    </div>
                """, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Fraud Type Explanation Card
            if fraud_type != 'legitimate':
                fraud_explanations = {
                    'high_amount': {
                        'title': '💰 High Amount Fraud Attack',
                        'description': 'Unusually large transaction detected with suspicious patterns. Often involves stolen credentials or account takeover.',
                        'indicators': ['Amount > ₹10,000', 'High amount deviation from user pattern', 'Failed PIN attempts', 'Unauthorized access attempt'],
                        'action': 'Verify user identity through secondary authentication. Check if user authorized this large transaction.'
                    },
                    'new_device': {
                        'title': '📱 New Device Attack',
                        'description': 'Transaction initiated from unrecognized device. Common in device takeover scams where fraudster gains access to user\'s UPI credentials.',
                        'indicators': ['First-time device usage', 'Device age < 30 days', 'Small verification transaction detected', 'Credential compromise suspected'],
                        'action': 'Send OTP to registered mobile. Verify device through trusted channel. Consider blocking until device is verified.'
                    },
                    'night_rush': {
                        'title': '🌙 Night Rush Attack',
                        'description': 'Rapid transactions during unusual hours (Night/Late Night). Fraudsters exploit victim\'s sleep time or create urgency through fake emergency calls.',
                        'indicators': ['Transaction at Night/Late Night', 'Multiple rapid transactions (>5 in 1 hour)', 'High transaction frequency in 24h', 'Time-based exploitation'],
                        'action': 'Flag for immediate review. Contact user to confirm transaction legitimacy. Consider transaction limits during night hours.'
                    },
                    'multiple_new': {
                        'title': '👥 Multiple Beneficiary Attack',
                        'description': 'Rapidly switching between new beneficiaries. Classic pattern in scams where fraudster directs victim to send money to multiple "mule" accounts.',
                        'indicators': ['New beneficiary added', 'High beneficiary change velocity (>5)', 'Low beneficiary trust score (<0.3)', 'Money mule network suspected'],
                        'action': 'Block transaction. Verify all new beneficiaries. Check if user is being manipulated through social engineering.'
                    }
                }
                
                if fraud_type in fraud_explanations:
                    exp = fraud_explanations[fraud_type]
                    
                    # Build the card HTML
                    card_html = f"""
                    <div style='background: linear-gradient(135deg, rgba(239, 68, 68, 0.08), rgba(220, 38, 38, 0.12)); border-left: 6px solid #dc2626; border-radius: 12px; padding: 24px; margin-bottom: 24px; animation: fadeInUp 1s ease-out;'>
                        <h3 style='color: #dc2626; margin: 0 0 12px 0; font-size: 20px; font-weight: 800;'>{exp['title']}</h3>
                        <p style='color: #0A2540; font-size: 15px; line-height: 1.7; margin: 0 0 16px 0;'>{exp['description']}</p>
                        
                        <div style='background: rgba(255, 255, 255, 0.6); border-radius: 8px; padding: 16px; margin-bottom: 12px;'>
                            <div style='font-size: 12px; color: #64748b; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 10px;'>🔍 Key Indicators Detected:</div>
                            <ul style='margin: 0; padding-left: 20px; color: #425466; font-size: 14px; line-height: 1.8;'>
                    """
                    
                    # Add indicators
                    for ind in exp['indicators']:
                        card_html += f"<li>{ind}</li>"
                    
                    card_html += f"""
                            </ul>
                        </div>
                        
                        <div style='background: rgba(220, 38, 38, 0.1); border-radius: 8px; padding: 16px; border: 1px solid rgba(220, 38, 38, 0.3);'>
                            <div style='font-size: 12px; color: #dc2626; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 8px;'>⚡ Recommended Action:</div>
                            <p style='margin: 0; color: #0A2540; font-size: 14px; line-height: 1.6; font-weight: 500;'>{exp['action']}</p>
                        </div>
                    </div>
                    """
                    
                    st.markdown(card_html, unsafe_allow_html=True)
            
            # Main Results Display
            col_result1, col_result2 = st.columns([1, 1])
            
            with col_result1:
                # Enhanced Gauge chart with gradient
                color = '#10b981' if risk == 'LOW' else ('#f59e0b' if risk == 'MEDIUM' else '#ef4444')
                
                fig = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=prob * 100,
                    domain={'x': [0, 1], 'y': [0, 1]},
                    number={'suffix': '%', 'font': {'size': 48, 'family': 'Inter'}},
                    gauge={
                        'axis': {'range': [0, 100], 'tickwidth': 1},
                        'bar': {'color': color},
                        'bgcolor': "white",
                        'borderwidth': 2,
                        'bordercolor': "#E3E8EE",
                        'steps': [
                            {'range': [0, 30], 'color': '#F0FDF4'},
                            {'range': [30, 55], 'color': '#FEF3C7'},
                            {'range': [55, 100], 'color': '#FEE2E2'}
                        ],
                    }
                ))
                
                fig.update_layout(
                    height=250,
                    margin=dict(l=20, r=20, t=40, b=20),
                    font={'family': 'Inter'},
                    paper_bgcolor='white'
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            with col_result2:
                # Animated result card with gradient
                st.markdown(f"""
                    <div style='background: linear-gradient(135deg, {color}20 0%, {color}40 100%); border: 2px solid {color}; border-radius: 16px; padding: 28px; margin-top: 20px; box-shadow: 0 8px 24px {color}30; animation: fadeInUp 0.6s ease-out; position: relative; overflow: hidden;'>
                        <div style='position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent); animation: shimmer 2s infinite;'></div>
                        <div style='position: relative; z-index: 1;'>
                            <div style='font-size: 13px; color: #425466; font-weight: 600; margin-bottom: 12px; text-transform: uppercase; letter-spacing: 0.1em;'>RISK ASSESSMENT</div>
                            <div style='font-size: 38px; color: {color}; font-weight: 800; margin-bottom: 16px; text-shadow: 0 2px 4px {color}40;'>{risk} RISK</div>
                            <div style='font-size: 16px; color: #0A2540; line-height: 1.7; font-weight: 500;'>{result['explanation']}</div>
                            <div style='margin-top: 20px; padding-top: 20px; border-top: 2px solid {color}50;'>
                                <div style='font-size: 14px; color: #425466; margin-bottom: 8px;'>
                                    <span style='font-weight: 600; color: #0A2540;'>Fraud Type:</span> 
                                    <span style='background: {color}20; padding: 4px 12px; border-radius: 6px; font-weight: 600; color: {color};'>{result['fraud_type']}</span>
                                </div>
                                <div style='font-size: 14px; color: #425466;'>
                                    <span style='font-weight: 600; color: #0A2540;'>Decision:</span> 
                                    <span style='background: {color}20; padding: 4px 12px; border-radius: 6px; font-weight: 600; color: {color};'>{result['decision']}</span>
                                </div>
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Risk Factors Analysis Section
            st.markdown("""
                <div style='text-align: center; margin: 32px 0 24px 0;'>
                    <h3 style='font-size: 26px; font-weight: 700; background: linear-gradient(135deg, #667eea, #764ba2); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>
                        🔍 Detailed Risk Analysis
                    </h3>
                </div>
            """, unsafe_allow_html=True)
            
            # Calculate dynamic risk factors
            risk_factors = []
            time_labels = ['Morning', 'Afternoon', 'Evening', 'Night', 'Late Night']
            
            if time_slot in [3, 4]:  # Night or Late Night
                severity = 'High' if time_slot == 4 else 'Medium'
                risk_factors.append(("🌙 Night Time Transaction", severity, 85 if time_slot == 4 else 70, f"Transaction at {time_labels[time_slot]} increases fraud risk"))
            
            if is_new_device == 1:
                risk_factors.append(("📱 New Device Detected", "Critical", 95, "First-time device usage is a major fraud indicator"))
            
            if amount > 50000:
                risk_factors.append(("💰 High Transaction Amount", "High", 80, f"Amount ₹{amount:,.0f} exceeds typical transaction patterns"))
            
            if is_new_beneficiary == 1:
                risk_factors.append(("👤 New Beneficiary", "Medium", 60, "First transaction to this beneficiary"))
            
            if beneficiary_trust_score < 0.4:
                risk_factors.append(("⚠️ Low Trust Score", "High", 75, f"Trust score {beneficiary_trust_score:.2f} is below safe threshold"))
            
            if device_age_days < 30:
                risk_factors.append(("📲 Recently Registered Device", "Medium", 65, f"Device only {device_age_days} days old"))
            
            if location_change == 1:
                risk_factors.append(("📍 Location Changed", "Medium", 55, "Unusual geographic transaction pattern detected"))
            
            if transaction_frequency > 15:
                risk_factors.append(("⚡ High Transaction Velocity", "High", 70, f"{transaction_frequency} transactions in 24h is unusually high"))
            
            if past_fraud_flag == 1:
                risk_factors.append(("🚨 Past Fraud History", "Critical", 90, "Account has previous fraud incidents"))
            
            if amount_deviation > 3.0:
                risk_factors.append(("📊 Amount Anomaly", "Medium", 60, f"Deviation of {amount_deviation:.1f}x from typical spending"))
            
            # Risk Factors Display
            if len(risk_factors) > 0:
                col_risk1, col_risk2 = st.columns(2)
                
                for idx, (factor, severity, score, description) in enumerate(risk_factors):
                    col = col_risk1 if idx % 2 == 0 else col_risk2
                    
                    severity_colors = {
                        'Critical': ('#ef4444', '#fee2e2'),
                        'High': ('#f59e0b', '#fef3c7'),
                        'Medium': ('#3b82f6', '#dbeafe')
                    }
                    severity_color, bg_color = severity_colors.get(severity, ('#6b7280', '#f3f4f6'))
                    
                    with col:
                        st.markdown(f"""
                            <div style='background: {bg_color}; border-left: 4px solid {severity_color}; border-radius: 12px; padding: 18px; margin-bottom: 16px; animation: fadeInUp {0.7 + idx * 0.1}s ease-out; box-shadow: 0 4px 12px rgba(0,0,0,0.08);'>
                                <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;'>
                                    <span style='color: #0A2540; font-weight: 700; font-size: 15px;'>{factor}</span>
                                    <span style='background: {severity_color}; color: white; padding: 4px 10px; border-radius: 8px; font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em;'>{severity}</span>
                                </div>
                                <p style='color: #425466; font-size: 13px; margin: 8px 0 12px 0; line-height: 1.5;'>{description}</p>
                                <div style='width: 100%; height: 6px; background: rgba(0,0,0,0.08); border-radius: 3px; overflow: hidden;'>
                                    <div style='width: {score}%; height: 100%; background: linear-gradient(90deg, {severity_color}, {severity_color}cc); animation: slideRight 1.2s ease-out;'></div>
                                </div>
                                <div style='text-align: right; margin-top: 6px;'>
                                    <span style='font-size: 12px; font-weight: 600; color: {severity_color};'>Risk Impact: {score}%</span>
                                </div>
                            </div>
                        """, unsafe_allow_html=True)
            else:
                st.markdown("""
                    <div style='background: linear-gradient(135deg, #d1fae5, #a7f3d0); border-left: 4px solid #10b981; border-radius: 12px; padding: 24px; text-align: center; animation: fadeInUp 0.7s ease-out;'>
                        <div style='font-size: 48px; margin-bottom: 12px;'>✅</div>
                        <h4 style='color: #065f46; font-size: 20px; font-weight: 700; margin-bottom: 8px;'>No Significant Risk Factors Detected</h4>
                        <p style='color: #047857; font-size: 15px; margin: 0;'>This transaction appears clean with normal behavioral patterns</p>
                    </div>
                """, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Transaction Overview Insights
            st.markdown("""
                <div style='text-align: center; margin: 32px 0 24px 0;'>
                    <h3 style='font-size: 26px; font-weight: 700; background: linear-gradient(135deg, #667eea, #764ba2); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>
                        📊 Transaction Overview
                    </h3>
                </div>
            """, unsafe_allow_html=True)
            
            overview_col1, overview_col2, overview_col3, overview_col4 = st.columns(4)
            
            with overview_col1:
                st.markdown(f"""
                    <div style='background: linear-gradient(135deg, rgba(59, 130, 246, 0.1), rgba(37, 99, 235, 0.2)); border-radius: 12px; padding: 20px; text-align: center; border: 2px solid rgba(59, 130, 246, 0.3);'>
                        <div style='font-size: 11px; color: #64748b; font-weight: 700; margin-bottom: 10px; text-transform: uppercase; letter-spacing: 0.1em;'>Amount</div>
                        <div style='font-size: 24px; font-weight: 800; color: #1e40af;'>₹{amount:,.0f}</div>
                    </div>
                """, unsafe_allow_html=True)
            
            with overview_col2:
                st.markdown(f"""
                    <div style='background: linear-gradient(135deg, rgba(168, 85, 247, 0.1), rgba(147, 51, 234, 0.2)); border-radius: 12px; padding: 20px; text-align: center; border: 2px solid rgba(168, 85, 247, 0.3);'>
                        <div style='font-size: 11px; color: #64748b; font-weight: 700; margin-bottom: 10px; text-transform: uppercase; letter-spacing: 0.1em;'>Time</div>
                        <div style='font-size: 24px; font-weight: 800; color: #7c3aed;'>{time_labels[time_slot]}</div>
                    </div>
                """, unsafe_allow_html=True)
            
            with overview_col3:
                st.markdown(f"""
                    <div style='background: linear-gradient(135deg, rgba(236, 72, 153, 0.1), rgba(219, 39, 119, 0.2)); border-radius: 12px; padding: 20px; text-align: center; border: 2px solid rgba(236, 72, 153, 0.3);'>
                        <div style='font-size: 11px; color: #64748b; font-weight: 700; margin-bottom: 10px; text-transform: uppercase; letter-spacing: 0.1em;'>Trust Score</div>
                        <div style='font-size: 24px; font-weight: 800; color: #be185d;'>{beneficiary_trust_score:.2f}</div>
                    </div>
                """, unsafe_allow_html=True)
            
            with overview_col4:
                st.markdown(f"""
                    <div style='background: linear-gradient(135deg, rgba(245, 158, 11, 0.1), rgba(217, 119, 6, 0.2)); border-radius: 12px; padding: 20px; text-align: center; border: 2px solid rgba(245, 158, 11, 0.3);'>
                        <div style='font-size: 11px; color: #64748b; font-weight: 700; margin-bottom: 10px; text-transform: uppercase; letter-spacing: 0.1em;'>24h Txns</div>
                        <div style='font-size: 24px; font-weight: 800; color: #b45309;'>{transaction_frequency}</div>
                    </div>
                """, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Final Recommendation
            st.markdown("""
                <div style='text-align: center; margin: 32px 0 24px 0;'>
                    <h3 style='font-size: 26px; font-weight: 700; background: linear-gradient(135deg, #667eea, #764ba2); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>
                        💡 Recommendation
                    </h3>
                </div>
            """, unsafe_allow_html=True)
            
            if risk == 'HIGH':
                st.markdown(f"""
                    <div style='background: linear-gradient(135deg, #ef4444, #dc2626); padding: 28px; border-radius: 16px; text-align: center; animation: pulse 2s ease-in-out infinite; box-shadow: 0 12px 32px rgba(239, 68, 68, 0.4);'>
                        <div style='font-size: 64px; margin-bottom: 16px;'>🚫</div>
                        <h3 style='color: white; margin: 0 0 12px 0; font-size: 28px; font-weight: 800; text-transform: uppercase; letter-spacing: 0.05em;'>BLOCK TRANSACTION</h3>
                        <p style='color: rgba(255,255,255,0.95); margin: 0; font-size: 16px; line-height: 1.7; font-weight: 500;'>
                            High fraud probability detected with multiple critical risk indicators. <br>
                            <strong>Immediate action required:</strong> Block transaction and initiate manual verification process.
                        </p>
                    </div>
                """, unsafe_allow_html=True)
            elif risk == 'MEDIUM':
                st.markdown(f"""
                    <div style='background: linear-gradient(135deg, #f59e0b, #d97706); padding: 28px; border-radius: 16px; text-align: center; box-shadow: 0 12px 32px rgba(245, 158, 11, 0.4);'>
                        <div style='font-size: 64px; margin-bottom: 16px;'>⚠️</div>
                        <h3 style='color: white; margin: 0 0 12px 0; font-size: 28px; font-weight: 800; text-transform: uppercase; letter-spacing: 0.05em;'>MANUAL REVIEW REQUIRED</h3>
                        <p style='color: rgba(255,255,255,0.95); margin: 0; font-size: 16px; line-height: 1.7; font-weight: 500;'>
                            Moderate fraud risk detected. Additional verification recommended.<br>
                            <strong>Suggested action:</strong> Request additional authentication or limit transaction amount.
                        </p>
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                    <div style='background: linear-gradient(135deg, #10b981, #059669); padding: 28px; border-radius: 16px; text-align: center; box-shadow: 0 12px 32px rgba(16, 185, 129, 0.4);'>
                        <div style='font-size: 64px; margin-bottom: 16px;'>✅</div>
                        <h3 style='color: white; margin: 0 0 12px 0; font-size: 28px; font-weight: 800; text-transform: uppercase; letter-spacing: 0.05em;'>ALLOW TRANSACTION</h3>
                        <p style='color: rgba(255,255,255,0.95); margin: 0; font-size: 16px; line-height: 1.7; font-weight: 500;'>
                            Low fraud probability with normal transaction patterns.<br>
                            <strong>Status:</strong> Transaction appears legitimate and safe to process.
                        </p>
                    </div>
                """, unsafe_allow_html=True)
    
    # Footer
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("""
        <div style='text-align: center; padding: 24px; margin-top: 48px; border-top: 2px solid rgba(102, 126, 234, 0.1);'>
            <p style='font-size: 16px; color: #425466; margin: 0;'>
                Made with <span style='color: #ff6b6b; font-size: 18px; animation: pulse 1.5s ease-in-out infinite;'>❤️</span> by 
                <strong style='background: linear-gradient(135deg, #667eea, #764ba2); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 700;'>Devs on Duty</strong>
            </p>
            <p style='font-size: 13px; color: #64748b; margin-top: 8px;'>Hackathon Project 2025</p>
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()

"""
Message Filter for Fraud Detection
Analyzes SMS/messages for fraud patterns and suspicious keywords
"""

import re

class MessageFilter:
    def __init__(self):
        # Fraud keywords and patterns
        self.fraud_keywords = {
            'high_risk': [
                'verify your account', 'confirm your details', 'update kyc', 
                'account will be blocked', 'suspended', 'click here immediately',
                'congratulations you won', 'claim your prize', 'lottery winner',
                'refund pending', 'refund credited', 'reversed amount',
                'customer care number', 'call this number', 'helpline',
                'share otp', 'enter otp', 'provide otp', 'send otp',
                'courier pending', 'parcel detained', 'customs charge',
                'income tax refund', 'tax refund pending',
                'arrest warrant', 'legal action', 'police complaint',
                'transfer money', 'send money urgently', 'immediate payment'
            ],
            'medium_risk': [
                'verify', 'confirm', 'update', 'expire', 'urgent',
                'limited time', 'act now', 'don\'t miss', 
                'free gift', 'bonus', 'reward', 'cashback',
                'click link', 'visit site', 'download app',
                'bank account', 'credit card', 'debit card',
                'pin', 'password', 'cvv', 'card details'
            ],
            'impersonation': [
                'from bank', 'from paytm', 'from phonepe', 'from gpay',
                'from government', 'from rbi', 'from income tax',
                'official notification', 'bank official', 'government official'
            ]
        }
        
        # Suspicious patterns (regex)
        self.suspicious_patterns = [
            r'\b\d{4}\s*\d{4}\s*\d{4}\s*\d{4}\b',  # Card numbers
            r'\b\d{3,4}\b.*\b\d{3,4}\b',  # OTP-like patterns
            r'https?://[^\s]+',  # URLs
            r'\b\d{10}\b',  # Phone numbers
            r'bit\.ly|tinyurl|goo\.gl',  # Shortened URLs
        ]
        
        # Legitimate transaction keywords (reduces false positives)
        self.legitimate_keywords = [
            'payment successful', 'transaction successful', 'credited to account',
            'debited from account', 'balance is', 'available balance',
            'thank you for', 'order confirmed', 'booking confirmed'
        ]
    
    def analyze_message(self, message):
        """
        Analyze message for fraud indicators
        Returns: dict with fraud_detected, risk_level, flags, and recommendation
        """
        if not message or not message.strip():
            return {
                'fraud_detected': False,
                'risk_level': 'NONE',
                'fraud_score': 0,
                'flags': [],
                'recommendation': 'No message provided',
                'can_proceed': True
            }
        
        message_lower = message.lower()
        flags = []
        fraud_score = 0
        
        # Check for legitimate transaction patterns first
        is_legitimate = any(keyword in message_lower for keyword in self.legitimate_keywords)
        
        # Check high-risk keywords
        high_risk_found = []
        for keyword in self.fraud_keywords['high_risk']:
            if keyword in message_lower:
                high_risk_found.append(keyword)
                fraud_score += 25
        
        if high_risk_found:
            flags.append(f"🚨 High-risk keywords: {', '.join(high_risk_found[:3])}")
        
        # Check medium-risk keywords
        medium_risk_found = []
        for keyword in self.fraud_keywords['medium_risk']:
            if keyword in message_lower:
                medium_risk_found.append(keyword)
                fraud_score += 10
        
        if medium_risk_found:
            flags.append(f"⚠️ Suspicious keywords: {', '.join(medium_risk_found[:3])}")
        
        # Check impersonation attempts
        impersonation_found = []
        for keyword in self.fraud_keywords['impersonation']:
            if keyword in message_lower:
                impersonation_found.append(keyword)
                fraud_score += 20
        
        if impersonation_found:
            flags.append(f"🎭 Impersonation attempt: {', '.join(impersonation_found[:2])}")
        
        # Check suspicious patterns
        for pattern in self.suspicious_patterns:
            if re.search(pattern, message, re.IGNORECASE):
                if 'http' in pattern:
                    flags.append("🔗 Contains suspicious link")
                    fraud_score += 20
                elif 'bit.ly' in pattern or 'tinyurl' in pattern:
                    flags.append("🔗 Contains shortened URL")
                    fraud_score += 25
                elif r'\d{10}' in pattern:
                    flags.append("📞 Contains phone number")
                    fraud_score += 15
                else:
                    flags.append("🔢 Contains sensitive pattern")
                    fraud_score += 15
        
        # Check for urgency tactics
        urgency_words = ['urgent', 'immediately', 'now', 'today', 'expire', 'limited time']
        urgency_count = sum(1 for word in urgency_words if word in message_lower)
        if urgency_count >= 2:
            flags.append("⏰ Creates false urgency")
            fraud_score += 15
        
        # Reduce score if legitimate transaction
        if is_legitimate:
            fraud_score = max(0, fraud_score - 30)
            flags.append("✅ Contains legitimate transaction keywords")
        
        # Cap fraud score at 100
        fraud_score = min(100, fraud_score)
        
        # Determine risk level
        if fraud_score >= 60:
            risk_level = 'HIGH'
            fraud_detected = True
            recommendation = '🚫 HIGH RISK: Do not respond or share any information. Delete this message.'
            can_proceed = False
        elif fraud_score >= 30:
            risk_level = 'MEDIUM'
            fraud_detected = True
            recommendation = '⚠️ SUSPICIOUS: Verify sender through official channels before proceeding.'
            can_proceed = True
        else:
            risk_level = 'LOW'
            fraud_detected = False
            recommendation = '✅ Message appears safe. Proceed with normal transaction verification.'
            can_proceed = True
        
        return {
            'fraud_detected': fraud_detected,
            'risk_level': risk_level,
            'fraud_score': fraud_score,
            'flags': flags if flags else ['No fraud indicators detected'],
            'recommendation': recommendation,
            'can_proceed': can_proceed
        }

    def get_fraud_type(self, message):
        """Identify specific fraud type from message"""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ['otp', 'pin', 'cvv', 'password']):
            return 'OTP/Credential Phishing'
        elif any(word in message_lower for word in ['refund', 'reversed', 'credited back']):
            return 'Fake Refund Scam'
        elif any(word in message_lower for word in ['lottery', 'prize', 'won', 'congratulations']):
            return 'Prize/Lottery Scam'
        elif any(word in message_lower for word in ['courier', 'parcel', 'customs', 'detained']):
            return 'Fake Courier Scam'
        elif any(word in message_lower for word in ['kyc', 'verify account', 'update details']):
            return 'KYC Update Scam'
        elif any(word in message_lower for word in ['arrest', 'legal action', 'police', 'warrant']):
            return 'Threatening/Legal Scam'
        elif any(word in message_lower for word in ['tax refund', 'income tax', 'gst refund']):
            return 'Fake Tax Refund'
        else:
            return 'General Phishing'

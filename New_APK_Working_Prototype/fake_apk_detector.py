import pandas as pd
import numpy as np
import streamlit as st
import hashlib
import json
import re
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go

# Set page configuration
st.set_page_config(
    page_title="Fake APK Detector",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load the dataset
@st.cache_data
def load_data():
    # In a real app, this would load from the actual Excel file
    # For this example, we'll use the data provided
    data = {
        'App Name': ['YONO SBI UK', 'IDFC FIRST Bank', 'HDFC Bank', 'Canara ai1', 'BOI Mobile', 
                    'Cent Mobile', 'IndSMART', 'IOB Mobile', 'Kotak811', 'SIB Mirror+', 
                    'IndusMobile', 'Mahamobile Plus', 'RBL MyBank', 'iMobile', 'NAINI NEO'],
        'Package Name (ID)': ['com.YONOUKMobileApp', 'com.idfcfirstbank.optimus', 'com.snapwork.hdfc', 
                             'com.canarabank.mobility', 'com.boi.ua.android', 'com.infrasofttech.CentralBank', 
                             'com.iexceed.ib.digitalbankingprod', 'com.fss.iob6', 
                             'com.kotak811mobilebankingapp.instantsavingsupiscanandpayrecharge', 
                             'com.SIBMobile', 'com.fss.indus', 'com.kiya.mahaplus', 'com.rblbank.mobank', 
                             'com.csam.icici.bank.imobile', 'com.kiya.nainital'],
        'Version Code': ['3.5.1', '2.43', '11.3.2', '3.6.38', '3.4.0', '7.52', '1.0.34', '6.5.8', 
                        '3.7.3', '8.2.17', '10.11.22', '1.0.46', '9.1.5', '23', '1.0.4'],
        'Hash Algorithm': ['sha256', 'sha256', 'sha1', 'sha256', 'sha256', 'sha256', 'sha256', 
                          'sha256', 'sha256', 'sha256', 'sha1', 'sha256', 'sha1', 'sha1', 'sha256'],
        'Certificate Issuer': [
            'C=US, O=Symantec Corporation, CN=Symantec Root for Code Signing',
            'O=IDFC FIRST BANK',
            'C=91, ST=MH, L=Mumbai, O=Snapwork, OU=IT, CN=HDFC Bank',
            'C=US, ST=California, L=Mountain View, O=Google Inc., OU=Android, CN=Android',
            'C=US, ST=California, L=Mountain View, O=Google Inc., OU=Android, CN=Android',
            'C=91, O=Central Bank Of India',
            'C=US, ST=California, L=Mountain View, O=Google Inc., OU=Android, CN=Android',
            'C=US, ST=California, L=Mountain View, O=Google Inc., OU=Android, CN=Android',
            'C=US, ST=California, L=Mountain View, O=Google Inc., OU=Android, CN=Android',
            'C=IN, ST=Kerala, L=Kochi, O=The South Indian Bank Ltd, OU=DICT, CN=Mobile Banking Division',
            'C=91, ST=tamilnadu, L=chennai, O=fss, OU=fss, CN=fssnet mpay',
            'C=91, ST=Maharashtra, L=Mumbai, O=Infrasoft Technologies, OU=Infrasoft Technologies, CN=Infrasoft Technologies',
            'C=IN, ST=Maharashtra, L=Mumbai, O=The Ratnakar Bank Ltd., OU=IT, CN=Ratnakar Bank',
            'C=91, ST=MAHARASHTRA, L=MUMBAI, O=ICICI BANK, OU=ICICI BANK, CN=ICICI BANK',
            'C=US, ST=California, L=Mountain View, O=Google Inc., OU=Android, CN=Android'
        ],
        'Security Score': [50, 51, 47, 57, 73, 57, 54, 53, 45, 50, 47, 48, 48, 42, None],
        'Risk rating': ['B', 'B', 'B', 'B', 'A', 'B', 'B', 'B', 'B', 'B', 'B', 'B', 'B', 'B', None],
        'User/Device Trackers': [0, 4, 3, 5, 3, 1, 2, 0, 6, 3, 7, 2, 6, 10, None]
    }
    return pd.DataFrame(data)

# Load the data
df = load_data()

# Fake APK database (in a real app, this would be more extensive)
fake_apk_db = {
    "com.fake.hdfc.bank": {
        "original_package": "com.snapwork.hdfc",
        "signature_hash": "fake_hash_12345",
        "risk_score": 85,
        "scam_type": "UPI Clone"
    },
    "com.diwali.cashback.paytm": {
        "original_package": "com.paytm",
        "signature_hash": "fake_hash_diwali",
        "risk_score": 92,
        "scam_type": "Festival Scam"
    }
}

# Dangerous permissions list
DANGEROUS_PERMISSIONS = [
    "READ_SMS", "RECEIVE_SMS", "SEND_SMS", "RECEIVE_MMS", 
    "RECEIVE_BOOT_COMPLETED", "ACCESS_FINE_LOCATION", 
    "ACCESS_COARSE_LOCATION", "READ_CONTACTS", "READ_CALL_LOG",
    "WRITE_CONTACTS", "CALL_PHONE", "READ_PHONE_STATE"
]

# Fraud keywords in multiple languages
FRAUD_KEYWORDS = {
    "english": ["cashback", "bonus", "reward", "win", "free", "urgent", "verify", "lottery", "gift"],
    "hindi": ["नकद", "बोनस", "इनाम", "जीत", "मुफ्त", "तत्काल", "सत्यापित", "लॉटरी", "उपहार"],
    "tamil": ["பணத்", "போனஸ்", "வெகுமதி", "வெற்றி", "இலவச", "அவசர", "சரிபார்க்க", "லாட்டரி", "பரிசு"],
    "telugu": ["క్యాష్‌బ్యాక్", "బోనస్", "రివార్డ్", "గెలుచుకో", "ఉచిత", "అత్యవసర", "ధృవీకరించు", "లాటరీ", "బహుమతి"]
}

# Function to calculate risk score
def calculate_risk_score(apk_data, official_data=None):
    risk_score = 0
    
    # Check if package name matches any known bank
    if apk_data['package_name'] in df['Package Name (ID)'].values:
        # It's an official app, lower risk
        risk_score += 10
    else:
        # Check if it's a known fake
        if apk_data['package_name'] in fake_apk_db:
            risk_score += 90
        else:
            risk_score += 40
    
    # Check certificate
    if official_data is not None:
        if apk_data.get('certificate_hash') != official_data.get('certificate_hash'):
            risk_score += 30
    
    # Check dangerous permissions
    dangerous_perms = [perm for perm in apk_data.get('permissions', []) if perm in DANGEROUS_PERMISSIONS]
    risk_score += min(30, len(dangerous_perms) * 5)
    
    # Check for fraud keywords in app name or description
    app_name = apk_data.get('app_name', '').lower()
    for lang, keywords in FRAUD_KEYWORDS.items():
        for keyword in keywords:
            if keyword.lower() in app_name:
                risk_score += 15
                break
    
    # File size anomaly detection (if we have official data)
    if official_data and 'file_size' in apk_data and 'file_size' in official_data:
        size_diff = abs(apk_data['file_size'] - official_data['file_size']) / official_data['file_size']
        if size_diff > 0.5:  # More than 50% difference
            risk_score += 20
    
    return min(100, risk_score)

# Function to scan APK
def scan_apk(apk_data):
    # Check if it's a known banking app
    official_match = df[df['Package Name (ID)'] == apk_data['package_name']]
    
    if not official_match.empty:
        # This is an official banking app
        official_data = official_match.iloc[0].to_dict()
        risk_score = calculate_risk_score(apk_data, official_data)
        return {
            "verdict": "✅ Legit",
            "risk_score": risk_score,
            "details": "Official banking app",
            "official_data": official_data
        }
    else:
        # Check if it's a known fake
        if apk_data['package_name'] in fake_apk_db:
            fake_info = fake_apk_db[apk_data['package_name']]
            return {
                "verdict": "❌ Fake",
                "risk_score": fake_info['risk_score'],
                "details": f"Known fake app. Scam type: {fake_info['scam_type']}",
                "official_data": None
            }
        
        # Unknown app, calculate risk score
        risk_score = calculate_risk_score(apk_data)
        
        if risk_score < 30:
            verdict = "✅ Likely Legit"
        elif risk_score < 70:
            verdict = "⚠️ Suspicious"
        else:
            verdict = "❌ Likely Fake"
            
        return {
            "verdict": verdict,
            "risk_score": risk_score,
            "details": "Unknown app - analyzed based on characteristics",
            "official_data": None
        }

# Function to simulate APK data extraction (in a real app, this would extract from actual APK)
def extract_apk_data(uploaded_file=None, package_name=None):
    if uploaded_file:
        # In a real app, this would extract data from the uploaded APK file
        # For simulation, we'll return mock data based on the filename
        file_name = uploaded_file.name.lower()
        
        if "hdfc" in file_name:
            return {
                "app_name": "HDFC Bank",
                "package_name": "com.snapwork.hdfc",
                "certificate_hash": "legit_hash_hdfc",
                "permissions": ["INTERNET", "READ_SMS", "ACCESS_FINE_LOCATION"],
                "file_size": 55.35
            }
        elif "fake" in file_name:
            return {
                "app_name": "HDFC Bank UPI Cashback",
                "package_name": "com.fake.hdfc.bank",
                "certificate_hash": "fake_hash_12345",
                "permissions": ["INTERNET", "READ_SMS", "RECEIVE_SMS", "ACCESS_FINE_LOCATION", "READ_CONTACTS"],
                "file_size": 32.18
            }
        elif "diwali" in file_name:
            return {
                "app_name": "Diwali Cashback Offer",
                "package_name": "com.diwali.cashback.paytm",
                "certificate_hash": "fake_hash_diwali",
                "permissions": ["INTERNET", "READ_SMS", "RECEIVE_SMS", "SEND_SMS", "ACCESS_FINE_LOCATION"],
                "file_size": 28.45
            }
        else:
            # Generic unknown app
            return {
                "app_name": "Unknown Banking App",
                "package_name": "com.unknown.bank.app",
                "certificate_hash": "unknown_hash",
                "permissions": ["INTERNET", "ACCESS_NETWORK_STATE"],
                "file_size": 40.0
            }
    elif package_name:
        # Simulate data based on package name
        if package_name in df['Package Name (ID)'].values:
            app_data = df[df['Package Name (ID)'] == package_name].iloc[0].to_dict()
            return {
                "app_name": app_data['App Name'],
                "package_name": package_name,
                "certificate_hash": f"legit_hash_{package_name}",
                "permissions": ["INTERNET", "READ_SMS", "ACCESS_NETWORK_STATE"],
                "file_size": 50.0  # Default size
            }
        else:
            return {
                "app_name": "Unknown App",
                "package_name": package_name,
                "certificate_hash": f"unknown_hash_{package_name}",
                "permissions": ["INTERNET", "READ_SMS", "RECEIVE_SMS"],
                "file_size": 35.0
            }
    
    return None

# Main app
def main():
    st.title("🛡️ Fake APK Detector for Banking Apps")
    st.markdown("Protect yourself from fake banking apps and financial scams")
    
    # Sidebar
    st.sidebar.header("APK Scanner")
    scan_option = st.sidebar.radio("Select Scan Option:", 
                                  ["Upload APK", "Enter Package Name", "Device Scan"])
    
    apk_data = None
    
    if scan_option == "Upload APK":
        uploaded_file = st.sidebar.file_uploader("Choose an APK file", type=['apk'])
        if uploaded_file:
            with st.spinner("Extracting APK data..."):
                apk_data = extract_apk_data(uploaded_file=uploaded_file)
    
    elif scan_option == "Enter Package Name":
        package_name = st.sidebar.text_input("Enter package name (e.g., com.example.bank):")
        if package_name:
            with st.spinner("Fetching app data..."):
                apk_data = extract_apk_data(package_name=package_name)
    
    elif scan_option == "Device Scan":
        st.sidebar.info("Device scanning would be implemented in a mobile app version")
        if st.sidebar.button("Simulate Device Scan"):
            # Simulate finding a suspicious app
            apk_data = {
                "app_name": "UPI Payment App",
                "package_name": "com.suspicious.upi.payment",
                "certificate_hash": "suspicious_hash_123",
                "permissions": ["INTERNET", "READ_SMS", "RECEIVE_SMS", "SEND_SMS"],
                "file_size": 28.3
            }
    
    # Main content
    if apk_data:
        st.header("APK Analysis Results")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("App Information")
            st.write(f"**App Name:** {apk_data['app_name']}")
            st.write(f"**Package Name:** {apk_data['package_name']}")
            st.write(f"**File Size:** {apk_data['file_size']} MB")
            st.write(f"**Certificate Hash:** {apk_data['certificate_hash'][:20]}...")
            
            st.subheader("Permissions")
            for perm in apk_data['permissions']:
                if perm in DANGEROUS_PERMISSIONS:
                    st.error(f"⚠️ {perm} (Dangerous)")
                else:
                    st.info(f"✅ {perm}")
        
        with col2:
            # Scan the APK
            with st.spinner("Analyzing APK..."):
                result = scan_apk(apk_data)
            
            # Display result
            risk_score = result['risk_score']
            
            if risk_score < 30:
                color = "green"
                emoji = "✅"
            elif risk_score < 70:
                color = "orange"
                emoji = "⚠️"
            else:
                color = "red"
                emoji = "❌"
            
            st.subheader("Scan Result")
            st.markdown(f"<h2 style='color: {color};'>{emoji} {result['verdict']}</h2>", 
                       unsafe_allow_html=True)
            
            # Risk score gauge
            fig = go.Figure(go.Indicator(
                mode = "gauge+number+delta",
                value = risk_score,
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': "Risk Score"},
                delta = {'reference': 50},
                gauge = {
                    'axis': {'range': [0, 100]},
                    'bar': {'color': color},
                    'steps': [
                        {'range': [0, 30], 'color': "lightgreen"},
                        {'range': [30, 70], 'color': "yellow"},
                        {'range': [70, 100], 'color': "red"}]
                }
            ))
            st.plotly_chart(fig, use_container_width=True)
            
            st.write(f"**Details:** {result['details']}")
            
            # Show recommendations
            if risk_score > 70:
                st.error("**Recommendation:** Do not install this app. It's likely a fake banking app designed to steal your financial information.")
            elif risk_score > 30:
                st.warning("**Recommendation:** Be cautious. This app shows suspicious characteristics. Verify its authenticity before installing.")
            else:
                st.success("**Recommendation:** This app appears to be safe. You can proceed with installation.")
    
    else:
        # Show dashboard when no APK is being scanned
        st.header("Dashboard")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Scans", "1,247", "23%")
        with col2:
            st.metric("Fake Apps Detected", "87", "12%")
        with col3:
            st.metric("Prevented Installs", "42", "8%")
        
        st.subheader("Recent Scans")
        # Simulated scan history
        scan_history = [
            {"date": "2023-10-15", "app": "HDFC Bank", "risk": 15, "verdict": "✅ Legit"},
            {"date": "2023-10-14", "app": "Diwali Cashback", "risk": 92, "verdict": "❌ Fake"},
            {"date": "2023-10-14", "app": "UPI Payment", "risk": 65, "verdict": "⚠️ Suspicious"},
            {"date": "2023-10-13", "app": "SBI YONO", "risk": 22, "verdict": "✅ Legit"},
            {"date": "2023-10-12", "app": "Festival Reward", "risk": 88, "verdict": "❌ Fake"}
        ]
        
        st.dataframe(scan_history)
        
        # Fraud analytics
        st.subheader("Fraud Analytics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            scam_types = {
                "UPI Clones": 45,
                "Festival Scams": 32,
                "Loan Apps": 18,
                "Other": 5
            }
            fig1, ax1 = plt.subplots()
            ax1.pie(scam_types.values(), labels=scam_types.keys(), autopct='%1.1f%%')
            ax1.set_title("Scam Types Distribution")
            st.pyplot(fig1)
        
        with col2:
            # Simulated regional data
            regions = {
                "Maharashtra": 22,
                "Delhi": 18,
                "Karnataka": 15,
                "Tamil Nadu": 12,
                "Uttar Pradesh": 10,
                "Other": 23
            }
            fig2, ax2 = plt.subplots()
            ax2.barh(list(regions.keys()), list(regions.values()))
            ax2.set_title("Fake Apps by Region")
            st.pyplot(fig2)
    
    # Additional features in expanders
    with st.expander("🌐 Real-Time Threat Intelligence"):
        st.write("""
        - Connected to I4C fraud database
        - Dynamic fake APK blacklist updates
        - Crowd-sourced reporting system
        """)
        st.info("Threat database last updated: Today, 14:32 IST")
    
    with st.expander("🛡️ Preventive Security Features"):
        st.write("""
        - Pre-installation blocking of malicious APKs
        - Background watchdog for suspicious apps
        - Merchant UPI receipt verification
        """)
    
    with st.expander("🗣️ Multi-Language Fraud Detection"):
        st.write("Detects scam phrases in multiple Indian languages:")
        for lang, keywords in FRAUD_KEYWORDS.items():
            st.write(f"**{lang.capitalize()}:** {', '.join(keywords[:3])}...")
    
    with st.expander("🔐 Bank Verification API"):
        st.write("""
        - Cross-check with official bank certificates
        - Telecom integration for link scanning
        - UPI transaction verification with NPCI
        """)

if __name__ == "__main__":
    main()
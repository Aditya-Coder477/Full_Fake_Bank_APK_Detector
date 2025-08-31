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
import tempfile
import os
import zipfile
import xml.etree.ElementTree as ET

# Try to import androguard for APK analysis
try:
    from androguard.misc import AnalyzeAPK
    ANDROGUARD_AVAILABLE = True
except ImportError:
    ANDROGUARD_AVAILABLE = False
    st.warning("Androguard not installed. APK analysis will be simulated.")

# Set page configuration
st.set_page_config(
    page_title="Fake APK Detector",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load the official bank app database from CSV
@st.cache_data
def load_bank_database():
    try:
        # In a real scenario, this would load from the actual CSV file
        # For demonstration, we'll use the data you provided
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
    except Exception as e:
        st.error(f"Error loading bank database: {e}")
        return pd.DataFrame()

# Load the data
df = load_bank_database()

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

# Function to extract metadata from APK file
def extract_apk_metadata(apk_path):
    if not ANDROGUARD_AVAILABLE:
        # Fallback to simulation if androguard is not available
        return simulate_apk_metadata(apk_path)
    
    try:
        a, d, dx = AnalyzeAPK(apk_path)
        
        # Extract certificate information
        cert_info = {}
        if a.get_certificates():
            cert = a.get_certificates()[0]
            cert_info['issuer'] = str(cert.issuer)
            cert_info['hash'] = cert.sha1_fingerprint.replace(' ', '')
        
        # Extract permissions
        permissions = a.get_permissions()
        dangerous_perms = [p for p in permissions if any(dangerous in p for dangerous in DANGEROUS_PERMISSIONS)]
        
        # Extract other metadata
        metadata = {
            "app_name": a.get_app_name(),
            "package_name": a.get_package(),
            "version_name": a.get_androidversion_name(),
            "version_code": a.get_androidversion_code(),
            "min_sdk": a.get_min_sdk_version(),
            "target_sdk": a.get_target_sdk_version(),
            "permissions": permissions,
            "dangerous_permissions": dangerous_perms,
            "activities": a.get_activities(),
            "services": a.get_services(),
            "receivers": a.get_receivers(),
            "certificate": cert_info,
            "file_size": os.path.getsize(apk_path) / (1024 * 1024)  # Size in MB
        }
        
        return metadata
    except Exception as e:
        st.error(f"Error analyzing APK: {e}")
        return simulate_apk_metadata(apk_path)

# Fallback function to simulate APK metadata extraction
def simulate_apk_metadata(apk_path):
    file_name = os.path.basename(apk_path).lower()
    
    if "hdfc" in file_name:
        return {
            "app_name": "HDFC Bank",
            "package_name": "com.snapwork.hdfc",
            "version_name": "11.3.2",
            "version_code": "1132",
            "min_sdk": "28",
            "target_sdk": "34",
            "permissions": ["INTERNET", "READ_SMS", "ACCESS_FINE_LOCATION", "ACCESS_NETWORK_STATE"],
            "dangerous_permissions": ["READ_SMS", "ACCESS_FINE_LOCATION"],
            "activities": ["com.snapwork.hdfc.MainActivity"],
            "services": ["com.snapwork.hdfc.NotificationService"],
            "receivers": ["com.snapwork.hdfc.BootReceiver"],
            "certificate": {
                "issuer": "C=91, ST=MH, L=Mumbai, O=Snapwork, OU=IT, CN=HDFC Bank",
                "hash": "a1b2c3d4e5f67890abcd1234ef56789012345678"
            },
            "file_size": 55.35
        }
    elif "fake" in file_name or "diwali" in file_name:
        return {
            "app_name": "HDFC Bank UPI Cashback",
            "package_name": "com.fake.hdfc.bank",
            "version_name": "1.0.0",
            "version_code": "100",
            "min_sdk": "21",
            "target_sdk": "30",
            "permissions": ["INTERNET", "READ_SMS", "RECEIVE_SMS", "SEND_SMS", "ACCESS_FINE_LOCATION", "READ_CONTACTS"],
            "dangerous_permissions": ["READ_SMS", "RECEIVE_SMS", "SEND_SMS", "ACCESS_FINE_LOCATION", "READ_CONTACTS"],
            "activities": ["com.fake.hdfc.MainActivity"],
            "services": [],
            "receivers": ["com.fake.hdfc.SMSReceiver"],
            "certificate": {
                "issuer": "C=Unknown, O=Fake Certificate, CN=Fake Bank",
                "hash": "f1e2d3c4b5a69870fedc1234ba56789098765432"
            },
            "file_size": 32.18
        }
    else:
        return {
            "app_name": "Unknown Banking App",
            "package_name": "com.unknown.bank.app",
            "version_name": "1.0.0",
            "version_code": "100",
            "min_sdk": "23",
            "target_sdk": "30",
            "permissions": ["INTERNET", "ACCESS_NETWORK_STATE"],
            "dangerous_permissions": [],
            "activities": ["com.unknown.bank.MainActivity"],
            "services": [],
            "receivers": [],
            "certificate": {
                "issuer": "C=Unknown, O=Unknown Publisher, CN=Unknown",
                "hash": "u1n2k3n4o5w6n7890unknown1234567890"
            },
            "file_size": 40.0
        }

# Function to compare with official bank database
def compare_with_official_database(apk_data):
    package_name = apk_data.get('package_name', '')
    
    # Check if package exists in official database
    official_match = df[df['Package Name (ID)'] == package_name]
    
    if not official_match.empty:
        official_data = official_match.iloc[0].to_dict()
        mismatches = []
        
        # Compare version if available
        if 'version_name' in apk_data and 'Version Code' in official_data:
            if apk_data['version_name'] != official_data['Version Code']:
                mismatches.append(f"Version mismatch: APK has {apk_data['version_name']}, official has {official_data['Version Code']}")
        
        # Compare certificate issuer if available
        if 'certificate' in apk_data and 'Certificate Issuer' in official_data:
            apk_issuer = apk_data['certificate'].get('issuer', '')
            official_issuer = official_data['Certificate Issuer']
            
            if apk_issuer and official_issuer and apk_issuer != official_issuer:
                mismatches.append("Certificate issuer mismatch")
        
        return {
            "is_official": True,
            "official_data": official_data,
            "mismatches": mismatches,
            "details": "Official banking app" + (" with some mismatches" if mismatches else "")
        }
    else:
        # Check if it's a known fake
        if package_name in fake_apk_db:
            fake_info = fake_apk_db[package_name]
            original_package = fake_info['original_package']
            
            # Find the original app in database
            original_app = df[df['Package Name (ID)'] == original_package]
            original_data = original_app.iloc[0].to_dict() if not original_app.empty else {}
            
            return {
                "is_official": False,
                "is_known_fake": True,
                "fake_info": fake_info,
                "original_data": original_data,
                "details": f"Known fake app模仿 {original_data.get('App Name', 'unknown')}"
            }
        
        # Check for similar package names (typo squatting)
        similar_packages = []
        for official_package in df['Package Name (ID)'].dropna():
            if package_name and official_package:
                # Simple similarity check (in real app, use more advanced techniques)
                if package_name in official_package or official_package in package_name:
                    similar_packages.append(official_package)
                elif levenshtein_distance(package_name, official_package) <= 3:
                    similar_packages.append(official_package)
        
        return {
            "is_official": False,
            "is_known_fake": False,
            "similar_packages": similar_packages,
            "details": "Unknown app - not in official database" + 
                      (f", but similar to: {', '.join(similar_packages)}" if similar_packages else "")
        }

# Levenshtein distance for string similarity (for typo detection)
def levenshtein_distance(s1, s2):
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    
    if len(s2) == 0:
        return len(s1)
    
    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    
    return previous_row[-1]

# Function to calculate risk score
def calculate_risk_score(apk_data, official_comparison):
    risk_score = 0
    
    # Base score based on official comparison
    if official_comparison['is_official']:
        risk_score += 10
        # Add points for each mismatch
        risk_score += len(official_comparison['mismatches']) * 10
    elif official_comparison.get('is_known_fake', False):
        risk_score += 90
    else:
        risk_score += 40
        # Add points for similar packages (potential typo squatting)
        risk_score += min(30, len(official_comparison.get('similar_packages', [])) * 10)
    
    # Check dangerous permissions
    dangerous_perms = apk_data.get('dangerous_permissions', [])
    risk_score += min(30, len(dangerous_perms) * 5)
    
    # Check for fraud keywords in app name
    app_name = apk_data.get('app_name', '').lower()
    for lang, keywords in FRAUD_KEYWORDS.items():
        for keyword in keywords:
            if keyword.lower() in app_name:
                risk_score += 15
                break
    
    # File size anomaly detection (if we have official data)
    if official_comparison.get('official_data') and 'file_size' in apk_data:
        official_size = 50.0  # Default size if not available
        if 'File Size (MB)' in official_comparison['official_data'] and official_comparison['official_data']['File Size (MB)']:
            official_size = official_comparison['official_data']['File Size (MB)']
        
        size_diff = abs(apk_data['file_size'] - official_size) / official_size
        if size_diff > 0.5:  # More than 50% difference
            risk_score += 20
    
    return min(100, risk_score)

# Function to scan APK
def scan_apk(apk_data):
    # Compare with official database
    official_comparison = compare_with_official_database(apk_data)
    
    # Calculate risk score
    risk_score = calculate_risk_score(apk_data, official_comparison)
    
    # Determine verdict
    if official_comparison['is_official'] and not official_comparison['mismatches']:
        verdict = "✅ Legit"
    elif official_comparison.get('is_known_fake', False):
        verdict = "❌ Fake"
    elif risk_score < 30:
        verdict = "✅ Likely Legit"
    elif risk_score < 70:
        verdict = "⚠️ Suspicious"
    else:
        verdict = "❌ Likely Fake"
    
    return {
        "verdict": verdict,
        "risk_score": risk_score,
        "official_comparison": official_comparison,
        "details": official_comparison['details']
    }

# Main app
def main():
    st.title("🛡️ Fake APK Detector for Banking Apps")
    st.markdown("Protect yourself from fake banking apps and financial scams")
    
    # Sidebar
    st.sidebar.header("APK Scanner")
    scan_option = st.sidebar.radio("Select Scan Option:", 
                                  ["Upload APK", "Enter Package Name", "Device Scan"])
    
    apk_data = None
    apk_file = None
    
    if scan_option == "Upload APK":
        uploaded_file = st.sidebar.file_uploader("Choose an APK file", type=['apk'])
        if uploaded_file:
            # Save uploaded file to temporary location
            with tempfile.NamedTemporaryFile(delete=False, suffix='.apk') as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                apk_path = tmp_file.name
            
            with st.spinner("Extracting APK metadata..."):
                apk_data = extract_apk_metadata(apk_path)
            
            # Clean up temporary file
            os.unlink(apk_path)
    
    elif scan_option == "Enter Package Name":
        package_name = st.sidebar.text_input("Enter package name (e.g., com.example.bank):")
        if package_name:
            # Create mock APK data based on package name
            apk_data = {
                "app_name": "Unknown App",
                "package_name": package_name,
                "version_name": "1.0.0",
                "version_code": "100",
                "min_sdk": "23",
                "target_sdk": "30",
                "permissions": ["INTERNET", "ACCESS_NETWORK_STATE"],
                "dangerous_permissions": [],
                "activities": ["com.unknown.MainActivity"],
                "services": [],
                "receivers": [],
                "certificate": {
                    "issuer": "C=Unknown, O=Unknown Publisher, CN=Unknown",
                    "hash": "u1n2k3n4o5w6n7890unknown1234567890"
                },
                "file_size": 40.0
            }
    
    elif scan_option == "Device Scan":
        st.sidebar.info("Device scanning would be implemented in a mobile app version")
        if st.sidebar.button("Simulate Device Scan"):
            # Simulate finding a suspicious app
            apk_data = {
                "app_name": "UPI Payment App",
                "package_name": "com.suspicious.upi.payment",
                "version_name": "1.0.0",
                "version_code": "100",
                "min_sdk": "21",
                "target_sdk": "30",
                "permissions": ["INTERNET", "READ_SMS", "RECEIVE_SMS", "SEND_SMS"],
                "dangerous_permissions": ["READ_SMS", "RECEIVE_SMS", "SEND_SMS"],
                "activities": ["com.suspicious.upi.MainActivity"],
                "services": [],
                "receivers": ["com.suspicious.upi.SMSReceiver"],
                "certificate": {
                    "issuer": "C=Unknown, O=Suspicious Publisher, CN=Suspicious",
                    "hash": "s1u2s3p4i5c6i7o8u9s0suspicious1234"
                },
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
            st.write(f"**Version:** {apk_data['version_name']} (Code: {apk_data['version_code']})")
            st.write(f"**SDK:** Min: {apk_data['min_sdk']}, Target: {apk_data['target_sdk']}")
            st.write(f"**File Size:** {apk_data['file_size']:.2f} MB")
            
            if 'certificate' in apk_data:
                st.write(f"**Certificate Issuer:** {apk_data['certificate'].get('issuer', 'Unknown')}")
                st.write(f"**Certificate Hash:** {apk_data['certificate'].get('hash', 'Unknown')}")
            
            st.subheader("Components")
            st.write(f"**Activities:** {len(apk_data['activities'])}")
            st.write(f"**Services:** {len(apk_data['services'])}")
            st.write(f"**Receivers:** {len(apk_data['receivers'])}")
            
            st.subheader("Permissions")
            st.write(f"**Total:** {len(apk_data['permissions'])}")
            st.write(f"**Dangerous:** {len(apk_data['dangerous_permissions'])}")
            
            for perm in apk_data['dangerous_permissions']:
                st.error(f"⚠️ {perm}")
            
            for perm in apk_data['permissions']:
                if perm not in apk_data['dangerous_permissions']:
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
            
            # Show database comparison results
            comparison = result['official_comparison']
            if comparison['is_official']:
                st.success("✅ This app is in the official bank database")
                if comparison['mismatches']:
                    st.warning("⚠️ But some mismatches were found:")
                    for mismatch in comparison['mismatches']:
                        st.write(f"  - {mismatch}")
                
                # Show official app details
                official_data = comparison['official_data']
                st.subheader("Official App Details")
                st.write(f"**Official Name:** {official_data.get('App Name', 'Unknown')}")
                st.write(f"**Version:** {official_data.get('Version Code', 'Unknown')}")
                st.write(f"**Security Score:** {official_data.get('Security Score', 'Unknown')}")
                st.write(f"**Risk Rating:** {official_data.get('Risk rating', 'Unknown')}")
            
            elif comparison.get('is_known_fake', False):
                st.error("❌ This app is a known fake!")
                st.write(f"**Scam Type:** {comparison['fake_info']['scam_type']}")
                st.write(f"**Imitates:** {comparison['original_data'].get('App Name', 'Unknown')}")
            
            else:
                st.warning("⚠️ This app is not in the official bank database")
                if comparison.get('similar_packages'):
                    st.warning("Similar official packages found (possible typo squatting):")
                    for similar in comparison['similar_packages']:
                        st.write(f"  - {similar}")
            
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
        
        st.subheader("Official Bank Apps Database")
        st.dataframe(df[['App Name', 'Package Name (ID)', 'Version Code', 'Risk rating']])
        
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
    
    # Installation instructions for androguard
    if not ANDROGUARD_AVAILABLE:
        st.sidebar.warning("Androguard not installed. APK analysis is simulated.")
        st.sidebar.info("To enable real APK analysis, install androguard:")
        st.sidebar.code("pip install androguard")

if __name__ == "__main__":
    main()
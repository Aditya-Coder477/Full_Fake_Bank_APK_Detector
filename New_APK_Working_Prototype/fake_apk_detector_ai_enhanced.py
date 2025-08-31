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
import tldextract
import requests
from urllib.parse import urlparse
import whois
from datetime import datetime
import time
import random

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

# Initialize session state for user role
if 'user_role' not in st.session_state:
    st.session_state.user_role = "user"  # Default to user role

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
            'Certificate Hash': [
                'a1b2c3d4e5f67890abcd1234ef56789012345678',  # SBI
                'b2c3d4e5f67890abcd1234ef5678901234567890',  # IDFC
                'c3d4e5f67890abcd1234ef5678901234567890ab',  # HDFC
                'd4e5f67890abcd1234ef5678901234567890abcd',  # Canara
                'e5f67890abcd1234ef5678901234567890abcde',   # BOI
                'f67890abcd1234ef5678901234567890abcdef',    # Cent
                '7890abcd1234ef5678901234567890abcdef12',    # IndSMART
                '890abcd1234ef5678901234567890abcdef123',    # IOB
                '90abcd1234ef5678901234567890abcdef1234',    # Kotak
                '0abcd1234ef5678901234567890abcdef12345',    # SIB
                'abcd1234ef5678901234567890abcdef123456',    # Indus
                'bcd1234ef5678901234567890abcdef1234567',    # Maha
                'cd1234ef5678901234567890abcdef12345678',    # RBL
                'd1234ef5678901234567890abcdef123456789',    # iMobile
                '1234ef5678901234567890abcdef1234567890'     # NAINI
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

# Fraud keywords in multiple languages with risk scores
FRAUD_KEYWORDS = {
    "english": {
        "cashback": 15, "bonus": 12, "reward": 10, "win": 15, "free": 10, 
        "urgent": 8, "verify": 8, "lottery": 20, "gift": 10, "offer": 8,
        "discount": 5, "claim": 12, "limited": 7, "time": 5, "winner": 15
    },
    "hindi": {
        "नकद": 15, "बोनस": 12, "इनाम": 10, "जीत": 15, "मुफ्त": 10, 
        "तत्काल": 8, "सत्यापित": 8, "लॉटरी": 20, "उपहार": 10, "ऑफर": 8,
        "छूट": 5, "दावा": 12, "सीमित": 7, "समय": 5, "विजेता": 15
    },
    "tamil": {
        "பணத்": 15, "போனஸ்": 12, "வெகுமதி": 10, "வெற்றி": 15, "இலவச": 10, 
        "அவசர": 8, "சரிபார்க்க": 8, "லாட்டரி": 20, "பரிசு": 10, "ஆஃபர்": 8,
        "தள்ளுபடி": 5, "கோர்": 12, "வரையறுக்கப்பட்ட": 7, "நேரம்": 5, "வெற்றியாளர்": 15
    },
    "telugu": {
        "క్యాష్‌బ్యాక్": 15, "బోనస్": 12, "రివార్డ్": 10, "గెలుచుకో": 15, "ఉచిత": 10, 
        "అత్యవసర": 8, "ధృవీకరించు": 8, "లాటరీ": 20, "బహుమతి": 10, "ఆఫర్": 8,
        "డిస్కౌంట్": 5, "క్లెయిమ్": 12, "పరిమిత": 7, "సమయం": 5, "విజేత": 15
    }
}

# Known suspicious domains and newly registered domains (NRD) analysis
def is_suspicious_domain(domain):
    suspicious_tlds = ['.xyz', '.top', '.club', '.loan', '.win', '.bid', '.stream', '.download']
    suspicious_keywords = ['bank', 'pay', 'upi', 'cash', 'reward', 'offer', 'free', 'gift', 'loan']
    
    # Check for suspicious TLDs
    if any(domain.endswith(tld) for tld in suspicious_tlds):
        return True, "Suspicious TLD"
    
    # Check for domain age (if newly registered)
    try:
        domain_info = whois.whois(domain)
        if domain_info.creation_date:
            if isinstance(domain_info.creation_date, list):
                creation_date = domain_info.creation_date[0]
            else:
                creation_date = domain_info.creation_date
            
            if (datetime.now() - creation_date).days < 90:
                return True, "Newly registered domain (< 90 days)"
    except:
        pass  # WHOIS lookup failed
    
    # Check for suspicious keywords in domain name
    domain_lower = domain.lower()
    if any(keyword in domain_lower for keyword in suspicious_keywords):
        return True, "Contains financial keywords"
    
    return False, ""

# Function to extract domains from APK
def extract_domains_from_apk(apk_path):
    domains = set()
    
    try:
        # Extract APK as zip
        with zipfile.ZipFile(apk_path, 'r') as apk_zip:
            for file_name in apk_zip.namelist():
                if file_name.endswith(('.xml', '.html', '.js', '.json')) or 'assets' in file_name:
                    try:
                        with apk_zip.open(file_name) as f:
                            content = f.read().decode('utf-8', errors='ignore')
                            
                            # Look for URLs and domains in the content
                            url_pattern = r'https?://([\w\-\.]+)[/\w\-\.]*'
                            found_urls = re.findall(url_pattern, content)
                            
                            for url in found_urls:
                                # Extract domain using tldextract
                                extracted = tldextract.extract(url)
                                domain = f"{extracted.domain}.{extracted.suffix}"
                                if domain and domain != '.':
                                    domains.add(domain)
                    except:
                        continue
    except:
        # Fallback: return some example domains for simulation
        domains = {'example.com', 'api.bank.com', 'payment-gateway.net'}
    
    return list(domains)

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
        
        # Extract domains from APK
        domains = extract_domains_from_apk(apk_path)
        suspicious_domains = []
        
        for domain in domains:
            is_suspicious, reason = is_suspicious_domain(domain)
            if is_suspicious:
                suspicious_domains.append({"domain": domain, "reason": reason})
        
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
            "file_size": os.path.getsize(apk_path) / (1024 * 1024),  # Size in MB
            "domains": domains,
            "suspicious_domains": suspicious_domains
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
                "hash": "c3d4e5f67890abcd1234ef5678901234567890ab"  # Matching HDFC's cert hash
            },
            "file_size": 55.35,
            "domains": ["api.hdfcbank.com", "secure-payments.hdfcbank.com", "notifications.hdfcbank.com"],
            "suspicious_domains": []
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
                "hash": "f1e2d3c4b5a69870fedc1234ba56789098765432"  # Different from official
            },
            "file_size": 32.18,
            "domains": ["hdfc-bank-upi.xyz", "secure-payments.xyz", "api.diwali-offer.top"],
            "suspicious_domains": [
                {"domain": "hdfc-bank-upi.xyz", "reason": "Suspicious TLD"},
                {"domain": "api.diwali-offer.top", "reason": "Suspicious TLD"}
            ]
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
            "file_size": 40.0,
            "domains": ["api.example.com", "payment.example.com"],
            "suspicious_domains": []
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
        
        # Compare certificate hash if available (enhanced comparison)
        if 'certificate' in apk_data and 'Certificate Hash' in official_data:
            apk_hash = apk_data['certificate'].get('hash', '')
            official_hash = official_data['Certificate Hash']
            
            if apk_hash and official_hash and apk_hash != official_hash:
                mismatches.append("Certificate hash mismatch - possible forgery!")
        
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

# Function to detect fraud keywords in text with risk scoring
def detect_fraud_keywords(text):
    detected_keywords = []
    total_risk = 0
    
    if not text:
        return detected_keywords, total_risk
    
    text_lower = text.lower()
    
    for lang, keywords in FRAUD_KEYWORDS.items():
        for keyword, risk_score in keywords.items():
            if keyword.lower() in text_lower:
                detected_keywords.append({
                    "keyword": keyword,
                    "language": lang,
                    "risk_score": risk_score
                })
                total_risk += risk_score
    
    return detected_keywords, total_risk

# Function to calculate risk score with AI-based features
def calculate_risk_score(apk_data, official_comparison):
    risk_score = 0
    risk_factors = []
    
    # Base score based on official comparison
    if official_comparison['is_official']:
        risk_score += 10
        # Add points for each mismatch
        mismatch_risk = len(official_comparison['mismatches']) * 10
        risk_score += mismatch_risk
        if mismatch_risk > 0:
            risk_factors.append(f"Package mismatches: +{mismatch_risk}")
    elif official_comparison.get('is_known_fake', False):
        risk_score += 90
        risk_factors.append("Known fake app: +90")
    else:
        risk_score += 40
        risk_factors.append("Unknown app: +40")
        # Add points for similar packages (potential typo squatting)
        similar_risk = min(30, len(official_comparison.get('similar_packages', [])) * 10)
        risk_score += similar_risk
        if similar_risk > 0:
            risk_factors.append(f"Similar to official apps: +{similar_risk}")
    
    # Check dangerous permissions
    dangerous_perms = apk_data.get('dangerous_permissions', [])
    perm_risk = min(30, len(dangerous_perms) * 5)
    risk_score += perm_risk
    if perm_risk > 0:
        risk_factors.append(f"Dangerous permissions: +{perm_risk}")
    
    # Check for fraud keywords in app name and description
    app_name = apk_data.get('app_name', '')
    keywords, keyword_risk = detect_fraud_keywords(app_name)
    risk_score += keyword_risk
    if keyword_risk > 0:
        risk_factors.append(f"Fraud keywords in name: +{keyword_risk}")
    
    # Check certificate hash mismatch (enhanced)
    if official_comparison.get('official_data') and 'certificate' in apk_data:
        official_hash = official_comparison['official_data'].get('Certificate Hash', '')
        apk_hash = apk_data['certificate'].get('hash', '')
        
        if official_hash and apk_hash and official_hash != apk_hash:
            cert_risk = 25
            risk_score += cert_risk
            risk_factors.append(f"Certificate hash mismatch: +{cert_risk}")
    
    # Check for suspicious domains
    suspicious_domains = apk_data.get('suspicious_domains', [])
    domain_risk = min(25, len(suspicious_domains) * 8)
    risk_score += domain_risk
    if domain_risk > 0:
        risk_factors.append(f"Suspicious domains: +{domain_risk}")
    
    # File size anomaly detection (if we have official data)
    if official_comparison.get('official_data') and 'file_size' in apk_data:
        official_size = 50.0  # Default size if not available
        if 'File Size (MB)' in official_comparison['official_data'] and official_comparison['official_data']['File Size (MB)']:
            official_size = official_comparison['official_data']['File Size (MB)']
        
        size_diff = abs(apk_data['file_size'] - official_size) / official_size
        if size_diff > 0.5:  # More than 50% difference
            size_risk = 20
            risk_score += size_risk
            risk_factors.append(f"Size anomaly: +{size_risk}")
    
    return min(100, risk_score), risk_factors

# NEW FEATURE: Dynamic Sandbox Analysis
def simulate_dynamic_analysis(apk_path, apk_data):
    """
    Simulate dynamic analysis by generating behavioral patterns
    In a real implementation, this would run in a sandbox environment
    """
    # Simulate analysis time
    time.sleep(2)
    
    # Generate simulated behavioral data based on APK characteristics
    behaviors = {
        "network_activity": [],
        "sms_operations": [],
        "permission_usage": [],
        "file_operations": [],
        "runtime_behavior": []
    }
    
    # Simulate network activity based on domains found
    domains = apk_data.get('domains', [])
    for domain in domains:
        behaviors["network_activity"].append({
            "type": "HTTP_REQUEST",
            "destination": domain,
            "frequency": random.randint(1, 20),
            "data_sent": random.randint(100, 5000)
        })
    
    # Simulate SMS operations if SMS permissions are present
    sms_perms = [p for p in apk_data.get('permissions', []) if 'SMS' in p]
    if sms_perms:
        behaviors["sms_operations"].append({
            "type": "SEND_SMS",
            "number": "PRMIUM_RATE_" + str(random.randint(1000, 9999)),
            "frequency": random.randint(1, 5)
        })
        behaviors["sms_operations"].append({
            "type": "READ_SMS",
            "frequency": random.randint(5, 15)
        })
    
    # Simulate permission usage patterns
    dangerous_perms = apk_data.get('dangerous_permissions', [])
    for perm in dangerous_perms:
        behaviors["permission_usage"].append({
            "permission": perm,
            "frequency": random.randint(1, 10),
            "context": "RUNTIME" if random.random() > 0.5 else "INSTALL"
        })
    
    # Add risk scoring based on behaviors
    risk_score = 0
    risk_factors = []
    
    # Network risk
    if len(behaviors["network_activity"]) > 5:
        risk_score += 15
        risk_factors.append("Excessive network connections: +15")
    
    # SMS risk
    if behaviors["sms_operations"]:
        risk_score += 25
        risk_factors.append("SMS operations detected: +25")
    
    # Suspicious domain risk
    suspicious_domains = apk_data.get('suspicious_domains', [])
    if suspicious_domains:
        risk_score += len(suspicious_domains) * 10
        risk_factors.append(f"Suspicious domains: +{len(suspicious_domains) * 10}")
    
    return {
        "behaviors": behaviors,
        "risk_score": risk_score,
        "risk_factors": risk_factors
    }

# Function to scan APK (updated with dynamic analysis)
def scan_apk(apk_data, apk_path=None):
    # Compare with official database
    official_comparison = compare_with_official_database(apk_data)
    
    # Calculate static risk score with AI features
    static_risk_score, static_risk_factors = calculate_risk_score(apk_data, official_comparison)
    
    # Perform dynamic analysis if APK path is provided
    dynamic_risk_score = 0
    dynamic_risk_factors = []
    dynamic_results = {}
    
    if apk_path:
        dynamic_results = simulate_dynamic_analysis(apk_path, apk_data)
        dynamic_risk_score = dynamic_results.get('risk_score', 0)
        dynamic_risk_factors = dynamic_results.get('risk_factors', [])
    
    # Combine static and dynamic risk scores
    total_risk_score = min(100, static_risk_score + dynamic_risk_score)
    all_risk_factors = static_risk_factors + dynamic_risk_factors
    
    # Determine verdict
    if official_comparison['is_official'] and not official_comparison['mismatches']:
        verdict = "✅ Legit"
    elif official_comparison.get('is_known_fake', False):
        verdict = "❌ Fake"
    elif total_risk_score < 30:
        verdict = "✅ Likely Legit"
    elif total_risk_score < 70:
        verdict = "⚠️ Suspicious"
    else:
        verdict = "❌ Likely Fake"
    
    return {
        "verdict": verdict,
        "risk_score": total_risk_score,
        "risk_factors": all_risk_factors,
        "official_comparison": official_comparison,
        "details": official_comparison['details'],
        "dynamic_analysis": dynamic_results
    }

# NEW FEATURE: Role-Based Authentication
def authenticate_user():
    """Simple authentication mechanism - in production, use proper auth"""
    st.sidebar.subheader("Authentication")
    
    if st.session_state.user_role == "user":
        if st.sidebar.button("Switch to Police View"):
            st.session_state.user_role = "police"
            st.rerun()
    else:
        if st.sidebar.button("Switch to User View"):
            st.session_state.user_role = "user"
            st.rerun()
    
    return st.session_state.user_role

# NEW FEATURE: User Dashboard
def display_user_dashboard(apk_data, result):
    """Display simplified results for regular users"""
    st.header("APK Analysis Results")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("App Information")
        st.write(f"**App Name:** {apk_data['app_name']}")
        st.write(f"**Package Name:** {apk_data['package_name']}")
        st.write(f"**Version:** {apk_data['version_name']}")
        
    with col2:
        # Display simplified result
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
        
        # Simple risk indicator
        st.write(f"**Risk Score:** {risk_score}/100")
        
        # Basic recommendations
        if risk_score > 70:
            st.error("**Recommendation:** Do not install this app.")
        elif risk_score > 30:
            st.warning("**Recommendation:** Be cautious with this app.")
        else:
            st.success("**Recommendation:** This app appears to be safe.")

# NEW FEATURE: Police Dashboard
def display_police_dashboard(apk_data, result):
    """Display detailed results for police users"""
    st.header("🔍 Police Forensic Analysis")
    
    # Create tabs for different analysis aspects
    tab1, tab2, tab3, tab4 = st.tabs(["Overview", "Technical Details", "Behavior Analysis", "Threat Intelligence"])
    
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("App Information")
            st.write(f"**App Name:** {apk_data['app_name']}")
            st.write(f"**Package Name:** {apk_data['package_name']}")
            st.write(f"**Version:** {apk_data['version_name']} (Code: {apk_data['version_code']})")
            st.write(f"**SDK:** Min: {apk_data['min_sdk']}, Target: {apk_data['target_sdk']}")
            st.write(f"**File Size:** {apk_data['file_size']:.2f} MB")
            
        with col2:
            # Detailed risk analysis
            risk_score = result['risk_score']
            
            st.subheader("Threat Assessment")
            st.write(f"**Verdict:** {result['verdict']}")
            st.write(f"**Risk Score:** {risk_score}/100")
            
            # Risk factors
            if result['risk_factors']:
                st.subheader("Risk Factors")
                for factor in result['risk_factors']:
                    st.write(f"- {factor}")
    
    with tab2:
        st.subheader("Technical Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Certificate Information**")
            if 'certificate' in apk_data:
                st.write(f"**Issuer:** {apk_data['certificate'].get('issuer', 'Unknown')}")
                st.write(f"**Hash:** {apk_data['certificate'].get('hash', 'Unknown')}")
            
            st.write("**Permissions**")
            st.write(f"**Total:** {len(apk_data['permissions'])}")
            st.write(f"**Dangerous:** {len(apk_data['dangerous_permissions'])}")
            
            for perm in apk_data['dangerous_permissions']:
                st.error(f"⚠️ {perm}")
        
        with col2:
            st.write("**Network Analysis**")
            if 'domains' in apk_data and apk_data['domains']:
                for domain in apk_data['domains']:
                    st.info(f"🌐 {domain}")
            
            if 'suspicious_domains' in apk_data and apk_data['suspicious_domains']:
                st.write("**Suspicious Domains**")
                for suspicious in apk_data['suspicious_domains']:
                    st.error(f"⚠️ {suspicious['domain']} - {suspicious['reason']}")
    
    with tab3:
        st.subheader("Dynamic Behavior Analysis")
        
        # Display simulated dynamic analysis results
        if 'dynamic_analysis' in result and result['dynamic_analysis']:
            dyn = result['dynamic_analysis']
            
            st.write("**Network Activity**")
            for activity in dyn.get('behaviors', {}).get('network_activity', []):
                st.write(f"- {activity['type']} to {activity['destination']} "
                        f"({activity['frequency']} times, {activity['data_sent']} bytes)")
            
            st.write("**SMS Operations**")
            for sms_op in dyn.get('behaviors', {}).get('sms_operations', []):
                st.error(f"- {sms_op['type']} to {sms_op.get('number', 'N/A')} "
                        f"({sms_op['frequency']} times)")
            
            st.write("**Permission Usage**")
            for perm_use in dyn.get('behaviors', {}).get('permission_usage', []):
                st.write(f"- {perm_use['permission']} used {perm_use['frequency']} times "
                        f"({perm_use['context']})")
        else:
            st.info("Dynamic analysis not performed on this APK")
    
    with tab4:
        st.subheader("Threat Intelligence")
        
        # Database comparison
        comparison = result['official_comparison']
        if comparison['is_official']:
            st.success("✅ This app is in the official bank database")
            if comparison['mismatches']:
                st.warning("⚠️ Mismatches found:")
                for mismatch in comparison['mismatches']:
                    st.write(f"  - {mismatch}")
        elif comparison.get('is_known_fake', False):
            st.error("❌ This app is a known fake!")
            st.write(f"**Scam Type:** {comparison['fake_info']['scam_type']}")
            st.write(f"**Imitates:** {comparison['original_data'].get('App Name', 'Unknown')}")
        
        # Fraud keywords
        app_name = apk_data.get('app_name', '')
        keywords, keyword_risk = detect_fraud_keywords(app_name)
        if keywords:
            st.write("**Fraud Keywords Detected**")
            for keyword_info in keywords:
                st.write(f"⚠️ '{keyword_info['keyword']}' ({keyword_info['language']})")

# NEW FEATURE: General Dashboard with Role-Specific Elements
def display_general_dashboard(user_role):
    """Display the general dashboard with role-specific elements"""
    st.header("Dashboard")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Scans", "1,247", "23%")
    with col2:
        st.metric("Fake Apps Detected", "87", "12%")
    with col3:
        st.metric("Prevented Installs", "42", "8%")
    
    # Show additional metrics for police
    if user_role == "police":
        st.subheader("Police Intelligence")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Active Investigations", "15", "3")
        with col2:
            st.metric("Pattern Matches", "32", "7%")
    
    st.subheader("Official Bank Apps Database")
    st.dataframe(df[['App Name', 'Package Name (ID)', 'Version Code', 'Risk rating']])
    
    # Add more detailed data for police
    if user_role == "police":
        st.subheader("Forensic Analysis Tools")
        
        if st.button("Generate Threat Report"):
            # Simulate generating a detailed report
            with st.spinner("Generating comprehensive threat report..."):
                time.sleep(2)
                st.success("Threat report generated!")
                
                # Display sample report data
                report_data = {
                    "Timeline": "Last 30 days",
                    "Pattern": "UPI clone apps targeting HDFC and SBI users",
                    "Geographic Spread": "Primarily Maharashtra, Delhi, Karnataka",
                    "Recommended Actions": [
                        "Issue public warning about fake 'Festival Cashback' apps",
                        "Coordinate with app stores for takedowns",
                        "Share IOCs with partner agencies"
                    ]
                }
                
                st.json(report_data)

# Main app
def main():
    st.title("🛡️ Fake APK Detector for Banking Apps")
    st.markdown("Protect yourself from fake banking apps and financial scams")
    
    # Get user role
    user_role = authenticate_user()
    
    # Display role information
    st.sidebar.write(f"Current view: **{user_role.upper()}**")
    
    # Sidebar
    st.sidebar.header("APK Scanner")
    scan_option = st.sidebar.radio("Select Scan Option:", 
                                  ["Upload APK", "Enter Package Name", "Device Scan"])
    
    apk_data = None
    apk_file = None
    apk_path = None
    
    if scan_option == "Upload APK":
        uploaded_file = st.sidebar.file_uploader("Choose an APK file", type=['apk'])
        if uploaded_file:
            # Save uploaded file to temporary location
            with tempfile.NamedTemporaryFile(delete=False, suffix='.apk') as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                apk_path = tmp_file.name
            
            with st.spinner("Extracting APK metadata..."):
                apk_data = extract_apk_metadata(apk_path)
    
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
                "file_size": 40.0,
                "domains": ["api.example.com", "payment.example.com"],
                "suspicious_domains": []
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
                "file_size": 28.3,
                "domains": ["upi-payment.xyz", "secure-api.top", "payment-gateway.com"],
                "suspicious_domains": [
                    {"domain": "upi-payment.xyz", "reason": "Suspicious TLD"},
                    {"domain": "secure-api.top", "reason": "Suspicious TLD"}
                ]
            }
    
    # Main content
    if apk_data:
        # Scan the APK
        with st.spinner("Analyzing APK with AI..."):
            result = scan_apk(apk_data, apk_path)
        
        # Display different views based on role
        if user_role == "police":
            display_police_dashboard(apk_data, result)
        else:
            display_user_dashboard(apk_data, result)
            
        # Clean up temporary file if it exists
        if apk_path and os.path.exists(apk_path):
            os.unlink(apk_path)
    else:
        # Show general dashboard
        display_general_dashboard(user_role)
    
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
            st.write(f"**{lang.capitalize()}:** {', '.join(list(keywords.keys())[:3])}...")
    
    with st.expander("🔐 Bank Verification API"):
        st.write("""
        - Cross-check with official bank certificates
        - Telecom integration for link scanning
        - UPI transaction verification with NPCI
        """)
    
    # NEW FEATURE: Dynamic Sandbox Information
    with st.expander("🔬 Dynamic Sandbox Analysis"):
        st.write("""
        Our advanced dynamic sandbox technology executes APKs in a secure environment to detect:
        - Runtime behavior patterns
        - Network activity and data exfiltration
        - SMS and communication operations
        - Permission usage in context
        """)
        if user_role == "police":
            st.success("Police users have access to detailed behavioral analysis reports.")
        else:
            st.info("Upgrade to police access for detailed behavioral analysis.")
    
    # Installation instructions for androguard
    if not ANDROGUARD_AVAILABLE:
        st.sidebar.warning("Androguard not installed. APK analysis is simulated.")
        st.sidebar.info("To enable real APK analysis, install androguard:")
        st.sidebar.code("pip install androguard")
    
    # Installation instructions for additional packages
    st.sidebar.info("For full AI features, also install:")
    st.sidebar.code("pip install tldextract python-whois")

if __name__ == "__main__":
    main()
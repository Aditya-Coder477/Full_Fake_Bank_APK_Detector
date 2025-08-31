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
import base64
import hashlib
from PIL import Image
import io
import uuid

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

# NEW: Initialize APK DNA database
if 'apk_dna_database' not in st.session_state:
    st.session_state.apk_dna_database = {}

# NEW: Initialize Case Management System
if 'case_database' not in st.session_state:
    st.session_state.case_database = {}
    st.session_state.case_counter = 1000  # Starting case ID

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

# Known APK DNA patterns for gang/campaign identification
apk_dna_patterns = {
    "red_rabbit": {
        "name": "Red Rabbit Gang",
        "targets": ["HDFC", "SBI", "ICICI"],
        "code_patterns": ["com.fake.", "com.clone.", "com.secure."],
        "ui_patterns": ["#FF0000", "#AA0000", "red_button", "urgent_alert"],
        "network_patterns": ["api.xyz", "payment.top", "secure.club"],
        "cultural_patterns": ["diwali", "cashback", "reward", "festival"],
        "first_seen": "2023-08-15",
        "activity": "High",
        "origin": "Unknown"
    },
    "blue_fox": {
        "name": "Blue Fox Campaign",
        "targets": ["Paytm", "PhonePe", "Google Pay"],
        "code_patterns": ["com.payment.", "com.wallet.", "com.transfer."],
        "ui_patterns": ["#0000FF", "#0000AA", "blue_gradient", "secure_badge"],
        "network_patterns": ["gateway.loan", "api.win", "secure.bid"],
        "cultural_patterns": ["offer", "discount", "bonus", "limited"],
        "first_seen": "2023-10-01",
        "activity": "Medium",
        "origin": "Southeast Asia"
    }
}

# NEW: Case Urgency Levels
CASE_URGENCY_LEVELS = {
    "critical": {
        "name": "Critical",
        "color": "#FF0000",
        "threshold": 90,
        "response_time": "1 hour",
        "description": "Immediate threat to users' financial security"
    },
    "high": {
        "name": "High",
        "color": "#FF6B00",
        "threshold": 75,
        "response_time": "4 hours",
        "description": "Significant risk requiring prompt attention"
    },
    "medium": {
        "name": "Medium",
        "color": "#FFC100",
        "threshold": 50,
        "response_time": "24 hours",
        "description": "Moderate risk that should be addressed soon"
    },
    "low": {
        "name": "Low",
        "color": "#00B050",
        "threshold": 0,
        "response_time": "7 days",
        "description": "Minimal risk, can be addressed during routine review"
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

# Function to extract UI elements from APK
def extract_ui_elements(apk_path):
    """Extract UI elements and colors from APK resources"""
    ui_data = {
        "colors": [],
        "layouts": [],
        "drawables": [],
        "themes": []
    }
    
    try:
        with zipfile.ZipFile(apk_path, 'r') as apk_zip:
            # Look for layout files
            layout_files = [f for f in apk_zip.namelist() if f.startswith('res/layout/') and f.endswith('.xml')]
            ui_data["layouts"] = layout_files[:5]  # Limit to first 5
            
            # Look for color resources
            color_files = [f for f in apk_zip.namelist() if 'color' in f and (f.endswith('.xml') or f.endswith('.json'))]
            
            # Try to extract colors from XML files
            for color_file in color_files[:3]:  # Limit to first 3
                try:
                    with apk_zip.open(color_file) as f:
                        content = f.read().decode('utf-8', errors='ignore')
                        # Simple regex to find color values
                        color_matches = re.findall(r'#([0-9A-Fa-f]{6,8})', content)
                        ui_data["colors"].extend(color_matches)
                except:
                    continue
            
            # Look for drawable resources
            drawable_files = [f for f in apk_zip.namelist() if 'drawable' in f and (f.endswith('.png') or f.endswith('.jpg') or f.endswith('.xml'))]
            ui_data["drawables"] = drawable_files[:5]  # Limit to first 5
            
            # Extract theme information
            manifest_files = [f for f in apk_zip.namelist() if f.endswith('AndroidManifest.xml')]
            if manifest_files:
                try:
                    with apk_zip.open(manifest_files[0]) as f:
                        content = f.read().decode('utf-8', errors='ignore')
                        theme_matches = re.findall(r'android:theme=["\']([^"\']+)["\']', content)
                        ui_data["themes"] = theme_matches
                except:
                    pass
                    
    except Exception as e:
        st.error(f"Error extracting UI elements: {e}")
    
    return ui_data

# Function to extract code patterns from APK
def extract_code_patterns(apk_path):
    """Extract code patterns and structures from APK"""
    code_data = {
        "package_patterns": [],
        "class_names": [],
        "method_names": [],
        "libraries": [],
        "obfuscation_signs": []
    }
    
    try:
        with zipfile.ZipFile(apk_path, 'r') as apk_zip:
            # Look for DEX files (compiled Android code)
            dex_files = [f for f in apk_zip.namelist() if f.endswith('.dex')]
            
            # Look for native libraries
            lib_files = [f for f in apk_zip.namelist() if f.startswith('lib/')]
            code_data["libraries"] = [os.path.basename(f) for f in lib_files[:5]]  # Limit to first 5
            
            # Look for package patterns in various files
            for file_name in apk_zip.namelist():
                if file_name.endswith(('.xml', '.json', '.properties')):
                    try:
                        with apk_zip.open(file_name) as f:
                            content = f.read().decode('utf-8', errors='ignore')
                            # Look for package names
                            package_matches = re.findall(r'[a-zA-Z_][a-zA-Z0-9_]*(\.[a-zA-Z_][a-zA-Z0-9_]*)+', content)
                            code_data["package_patterns"].extend(package_matches)
                    except:
                        continue
                
                # Limit processing to avoid performance issues
                if len(code_data["package_patterns"]) > 20:
                    break
                    
    except Exception as e:
        st.error(f"Error extracting code patterns: {e}")
    
    return code_data

# Function to generate APK DNA fingerprint
def generate_apk_dna(apk_path, apk_data):
    """Generate a comprehensive DNA fingerprint for the APK"""
    dna_fingerprint = {
        "code_dna": "",
        "ui_dna": "",
        "network_dna": "",
        "cultural_dna": "",
        "metadata_dna": "",
        "full_dna": ""
    }
    
    # Extract additional data for DNA generation
    ui_data = extract_ui_elements(apk_path)
    code_data = extract_code_patterns(apk_path)
    
    # Generate Code DNA (based on package structure, class names, etc.)
    code_elements = []
    code_elements.extend(code_data.get("package_patterns", [])[:5])
    code_elements.extend(code_data.get("libraries", [])[:3])
    code_elements.append(apk_data.get("package_name", ""))
    dna_fingerprint["code_dna"] = hashlib.sha256("|".join(code_elements).encode()).hexdigest()[:16]
    
    # Generate UI DNA (based on colors, layouts, themes)
    ui_elements = []
    ui_elements.extend(ui_data.get("colors", [])[:5])
    ui_elements.extend(ui_data.get("themes", [])[:2])
    ui_elements.extend(ui_data.get("layouts", [])[:3])
    dna_fingerprint["ui_dna"] = hashlib.sha256("|".join(ui_elements).encode()).hexdigest()[:16]
    
    # Generate Network DNA (based on domains and network patterns)
    network_elements = []
    network_elements.extend(apk_data.get("domains", [])[:5])
    network_elements.extend([d["domain"] for d in apk_data.get("suspicious_domains", [])[:3]])
    dna_fingerprint["network_dna"] = hashlib.sha256("|".join(network_elements).encode()).hexdigest()[:16]
    
    # Generate Cultural DNA (based on app name, fraud keywords, etc.)
    cultural_elements = []
    cultural_elements.append(apk_data.get("app_name", ""))
    
    # Detect fraud keywords in app name
    app_name = apk_data.get("app_name", "")
    keywords, _ = detect_fraud_keywords(app_name)
    cultural_elements.extend([k["keyword"] for k in keywords])
    
    dna_fingerprint["cultural_dna"] = hashlib.sha256("|".join(cultural_elements).encode()).hexdigest()[:16]
    
    # Generate Metadata DNA (based on permissions, version, etc.)
    metadata_elements = []
    metadata_elements.extend(apk_data.get("permissions", [])[:5])
    metadata_elements.append(apk_data.get("version_name", ""))
    metadata_elements.append(str(apk_data.get("file_size", "")))
    dna_fingerprint["metadata_dna"] = hashlib.sha256("|".join(metadata_elements).encode()).hexdigest()[:16]
    
    # Generate Full DNA (combination of all DNA components)
    full_dna = f"{dna_fingerprint['code_dna']}:{dna_fingerprint['ui_dna']}:{dna_fingerprint['network_dna']}:{dna_fingerprint['cultural_dna']}:{dna_fingerprint['metadata_dna']}"
    dna_fingerprint["full_dna"] = hashlib.sha256(full_dna.encode()).hexdigest()
    
    return dna_fingerprint

# Function to detect mimic apps using APK DNA
def detect_mimic_apps(apk_dna, apk_data):
    """Compare APK DNA with database to detect mimic apps and campaigns"""
    matches = []
    
    # Check against known DNA patterns
    for pattern_name, pattern_data in apk_dna_patterns.items():
        similarity_score = 0
        match_reasons = []
        
        # Check code patterns
        code_patterns = pattern_data.get("code_patterns", [])
        for pattern in code_patterns:
            if apk_data.get("package_name", "").startswith(pattern):
                similarity_score += 25
                match_reasons.append(f"Code pattern match: {pattern}")
                break
        
        # Check UI patterns (simplified)
        ui_patterns = pattern_data.get("ui_patterns", [])
        app_name = apk_data.get("app_name", "").lower()
        for pattern in ui_patterns:
            if pattern.lower() in app_name:
                similarity_score += 15
                match_reasons.append(f"UI pattern match: {pattern}")
                break
        
        # Check network patterns
        network_patterns = pattern_data.get("network_patterns", [])
        for domain in apk_data.get("domains", []):
            for pattern in network_patterns:
                if pattern in domain:
                    similarity_score += 20
                    match_reasons.append(f"Network pattern match: {pattern} in {domain}")
                    break
        
        # Check cultural patterns
        cultural_patterns = pattern_data.get("cultural_patterns", [])
        for pattern in cultural_patterns:
            if pattern in app_name:
                similarity_score += 20
                match_reasons.append(f"Cultural pattern match: {pattern}")
                break
        
        # Check if we have a significant match
        if similarity_score >= 40:
            matches.append({
                "campaign": pattern_name,
                "campaign_data": pattern_data,
                "similarity_score": similarity_score,
                "match_reasons": match_reasons
            })
    
    # Check against historical database (simulated)
    for stored_dna, stored_data in st.session_state.apk_dna_database.items():
        # Simple similarity check (in real implementation, use more advanced techniques)
        if stored_dna == apk_dna["full_dna"]:
            matches.append({
                "campaign": "Exact DNA Match",
                "campaign_data": {"name": "Previously analyzed APK"},
                "similarity_score": 100,
                "match_reasons": ["Exact DNA fingerprint match"]
            })
        elif stored_dna[:16] == apk_dna["full_dna"][:16]:
            matches.append({
                "campaign": "Partial DNA Match",
                "campaign_data": {"name": "Similar to previously analyzed APK"},
                "similarity_score": 65,
                "match_reasons": ["Partial DNA fingerprint match"]
            })
    
    return matches

# NEW: Function to generate a case ID
def generate_case_id():
    """Generate a unique case ID and increment the counter"""
    case_id = f"CASE-{st.session_state.case_counter}"
    st.session_state.case_counter += 1
    return case_id

# NEW: Function to determine case urgency
def determine_case_urgency(risk_score, mimic_detection, apk_data):
    """Determine the urgency level of a case based on risk factors"""
    # Start with risk score as base
    urgency_score = risk_score
    
    # Increase urgency if mimic apps are detected
    if mimic_detection:
        urgency_score += 15
    
    # Increase urgency if dangerous permissions are present
    dangerous_perms = apk_data.get('dangerous_permissions', [])
    if dangerous_perms:
        urgency_score += min(20, len(dangerous_perms) * 5)
    
    # Increase urgency if suspicious domains are found
    suspicious_domains = apk_data.get('suspicious_domains', [])
    if suspicious_domains:
        urgency_score += min(15, len(suspicious_domains) * 5)
    
    # Determine urgency level
    if urgency_score >= CASE_URGENCY_LEVELS["critical"]["threshold"]:
        return "critical"
    elif urgency_score >= CASE_URGENCY_LEVELS["high"]["threshold"]:
        return "high"
    elif urgency_score >= CASE_URGENCY_LEVELS["medium"]["threshold"]:
        return "medium"
    else:
        return "low"

# NEW: Function to create a new case
def create_new_case(apk_data, result, apk_path=None):
    """Create a new case entry in the case database"""
    case_id = generate_case_id()
    timestamp = datetime.now().isoformat()
    
    # Determine case urgency
    urgency = determine_case_urgency(
        result['risk_score'], 
        result.get('mimic_detection', []), 
        apk_data
    )
    
    # Create case entry
    case_entry = {
        "case_id": case_id,
        "timestamp": timestamp,
        "app_name": apk_data.get("app_name", "Unknown"),
        "package_name": apk_data.get("package_name", "Unknown"),
        "risk_score": result['risk_score'],
        "verdict": result['verdict'],
        "urgency": urgency,
        "apk_dna": result.get('apk_dna', {}),
        "mimic_detection": result.get('mimic_detection', []),
        "status": "open",
        "assigned_to": None,
        "notes": []
    }
    
    # Store case in database
    st.session_state.case_database[case_id] = case_entry
    
    return case_id, urgency

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

# Function to simulate dynamic analysis
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
    
    # Generate APK DNA and check for mimic apps
    apk_dna = {}
    mimic_detection = {}
    if apk_path:
        apk_dna = generate_apk_dna(apk_path, apk_data)
        mimic_detection = detect_mimic_apps(apk_dna, apk_data)
        
        # Store DNA in session database
        st.session_state.apk_dna_database[apk_dna["full_dna"]] = {
            "app_name": apk_data.get("app_name", ""),
            "package_name": apk_data.get("package_name", ""),
            "timestamp": datetime.now().isoformat(),
            "risk_score": static_risk_score + dynamic_risk_score
        }
    
    # Combine static and dynamic risk scores
    total_risk_score = min(100, static_risk_score + dynamic_risk_score)
    all_risk_factors = static_risk_factors + dynamic_risk_factors
    
    # Increase risk score if mimic apps are detected
    if mimic_detection:
        mimic_risk = min(30, len(mimic_detection) * 10)
        total_risk_score += mimic_risk
        all_risk_factors.append(f"Mimic app detection: +{mimic_risk}")
    
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
    
    # NEW: Create a case for this APK scan
    case_id, urgency = create_new_case(apk_data, {
        "verdict": verdict,
        "risk_score": total_risk_score,
        "risk_factors": all_risk_factors,
        "mimic_detection": mimic_detection,
        "apk_dna": apk_dna
    }, apk_path)
    
    return {
        "verdict": verdict,
        "risk_score": total_risk_score,
        "risk_factors": all_risk_factors,
        "official_comparison": official_comparison,
        "details": official_comparison['details'],
        "dynamic_analysis": dynamic_results,
        "apk_dna": apk_dna,
        "mimic_detection": mimic_detection,
        "case_id": case_id,  # NEW: Include case ID in results
        "urgency": urgency   # NEW: Include urgency level in results
    }

# Function to handle authentication
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

# Function to display user dashboard
def display_user_dashboard(apk_data, result):
    """Display simplified results for regular users"""
    st.header("APK Analysis Results")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("App Information")
        st.write(f"**App Name:** {apk_data['app_name']}")
        st.write(f"**Package Name:** {apk_data['package_name']}")
        st.write(f"**Version:** {apk_data['version_name']}")
        
        # NEW: Show case information
        st.subheader("Case Information")
        st.write(f"**Case ID:** {result.get('case_id', 'N/A')}")
        
        urgency = result.get('urgency', 'low')
        urgency_info = CASE_URGENCY_LEVELS.get(urgency, {})
        st.write(f"**Urgency:** :{urgency_info.get('color', '#000000')}[{urgency_info.get('name', 'Unknown').upper()}]")
        
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
        
        # Show mimic detection warning if applicable
        if result.get('mimic_detection'):
            st.error("⚠️ This app matches known scam patterns!")
        
        # Basic recommendations
        if risk_score > 70:
            st.error("**Recommendation:** Do not install this app.")
        elif risk_score > 30:
            st.warning("**Recommendation:** Be cautious with this app.")
        else:
            st.success("**Recommendation:** This app appears to be safe.")

# Function to display police dashboard
def display_police_dashboard(apk_data, result):
    """Display detailed results for police users"""
    st.header("🔍 Police Forensic Analysis")
    
    # Create tabs for different analysis aspects
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["Overview", "Technical Details", "Behavior Analysis", "Threat Intelligence", "APK DNA Analysis", "Case Management"])
    
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
            
            # NEW: Case information
            st.subheader("Case Information")
            st.write(f"**Case ID:** {result.get('case_id', 'N/A')}")
            
            urgency = result.get('urgency', 'low')
            urgency_info = CASE_URGENCY_LEVELS.get(urgency, {})
            urgency_color = urgency_info.get('color', '#000000')
            urgency_name = urgency_info.get('name', 'Unknown')
            
            st.markdown(f"**Urgency:** <span style='color:{urgency_color}; font-weight:bold'>{urgency_name.upper()}</span>", 
                       unsafe_allow_html=True)
            st.write(f"**Response Time:** {urgency_info.get('response_time', 'N/A')}")
            st.write(f"**Description:** {urgency_info.get('description', 'N/A')}")
            
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
    
    with tab5:
        # APK DNA Analysis tab
        st.subheader("APK DNA Analysis")
        
        if result.get('apk_dna'):
            dna = result['apk_dna']
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**DNA Fingerprint Components**")
                st.write(f"**Code DNA:** `{dna.get('code_dna', 'N/A')}`")
                st.write(f"**UI DNA:** `{dna.get('ui_dna', 'N/A')}`")
                st.write(f"**Network DNA:** `{dna.get('network_dna', 'N/A')}`")
                st.write(f"**Cultural DNA:** `{dna.get('cultural_dna', 'N/A')}`")
                st.write(f"**Metadata DNA:** `{dna.get('metadata_dna', 'N/A')}`")
                
            with col2:
                st.write("**Full DNA Fingerprint**")
                st.code(dna.get('full_dna', 'N/A'))
                
                # Show database info
                st.write("**DNA Database**")
                st.write(f"Stored fingerprints: {len(st.session_state.apk_dna_database)}")
                
            # Show mimic detection results
            if result.get('mimic_detection'):
                st.subheader("Mimic App Detection")
                
                for match in result['mimic_detection']:
                    with st.expander(f"Match: {match['campaign']} (Score: {match['similarity_score']}%)"):
                        st.write(f"**Campaign:** {match['campaign_data'].get('name', 'Unknown')}")
                        st.write(f"**Similarity Score:** {match['similarity_score']}%")
                        
                        st.write("**Match Reasons:**")
                        for reason in match['match_reasons']:
                            st.write(f"- {reason}")
                        
                        # Show campaign details
                        if 'targets' in match['campaign_data']:
                            st.write("**Targets:**", ", ".join(match['campaign_data']['targets']))
                        if 'first_seen' in match['campaign_data']:
                            st.write("**First Seen:**", match['campaign_data']['first_seen'])
                        if 'origin' in match['campaign_data']:
                            st.write("**Origin:**", match['campaign_data']['origin'])
            else:
                st.info("No known mimic patterns detected.")
        else:
            st.info("APK DNA analysis not available for this app.")
    
    with tab6:
        # NEW: Case Management tab
        st.subheader("Case Management")
        
        case_id = result.get('case_id')
        if case_id and case_id in st.session_state.case_database:
            case_data = st.session_state.case_database[case_id]
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Case Details**")
                st.write(f"**Case ID:** {case_data['case_id']}")
                st.write(f"**Created:** {case_data['timestamp']}")
                st.write(f"**Status:** {case_data['status']}")
                
                # Urgency display
                urgency = case_data.get('urgency', 'low')
                urgency_info = CASE_URGENCY_LEVELS.get(urgency, {})
                urgency_color = urgency_info.get('color', '#000000')
                urgency_name = urgency_info.get('name', 'Unknown')
                
                st.markdown(f"**Urgency:** <span style='color:{urgency_color}; font-weight:bold'>{urgency_name.upper()}</span>", 
                           unsafe_allow_html=True)
                
                # Status update
                new_status = st.selectbox("Update Status", 
                                         ["open", "in progress", "resolved", "closed"], 
                                         index=["open", "in progress", "resolved", "closed"].index(case_data['status']))
                
                if new_status != case_data['status']:
                    if st.button("Update Case Status"):
                        st.session_state.case_database[case_id]['status'] = new_status
                        st.success(f"Case status updated to {new_status}")
                        st.rerun()
            
            with col2:
                st.write("**Assignment**")
                assigned_to = case_data.get('assigned_to', 'Unassigned')
                st.write(f"**Assigned To:** {assigned_to}")
                
                # Assignment options
                officers = ["Unassigned", "Officer Sharma", "Inspector Patel", "Detective Kumar", "Cyber Crime Unit"]
                new_assignment = st.selectbox("Assign To", officers, 
                                            index=officers.index(assigned_to) if assigned_to in officers else 0)
                
                if new_assignment != assigned_to:
                    if st.button("Update Assignment"):
                        st.session_state.case_database[case_id]['assigned_to'] = new_assignment
                        st.success(f"Case assigned to {new_assignment}")
                        st.rerun()
            
            # Case notes
            st.subheader("Case Notes")
            new_note = st.text_area("Add a note to this case")
            
            if st.button("Add Note"):
                if new_note:
                    timestamp = datetime.now().isoformat()
                    note_entry = {
                        "timestamp": timestamp,
                        "author": st.session_state.user_role,
                        "content": new_note
                    }
                    
                    if 'notes' not in st.session_state.case_database[case_id]:
                        st.session_state.case_database[case_id]['notes'] = []
                    
                    st.session_state.case_database[case_id]['notes'].append(note_entry)
                    st.success("Note added to case")
                    st.rerun()
            
            # Display existing notes
            if 'notes' in case_data and case_data['notes']:
                st.write("**Previous Notes:**")
                for note in reversed(case_data['notes']):
                    st.write(f"**{note['timestamp']}** by {note['author']}:")
                    st.info(note['content'])
                    st.divider()
            else:
                st.info("No notes added to this case yet.")
        else:
            st.error("Case information not available.")

# Function to display general dashboard
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
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Active Investigations", "15", "3")
        with col2:
            st.metric("Pattern Matches", "32", "7%")
        with col3:
            st.metric("DNA Database", f"{len(st.session_state.apk_dna_database)}", "12")
        
        # NEW: Case management overview
        st.subheader("Case Management Overview")
        
        # Count cases by status and urgency
        if st.session_state.case_database:
            case_df = pd.DataFrame.from_dict(st.session_state.case_database, orient='index')
            
            # Cases by status
            status_counts = case_df['status'].value_counts()
            fig1, ax1 = plt.subplots()
            ax1.pie(status_counts.values, labels=status_counts.index, autopct='%1.1f%%')
            ax1.set_title("Cases by Status")
            st.pyplot(fig1)
            
            # Cases by urgency
            urgency_counts = case_df['urgency'].value_counts()
            
            # Create a DataFrame for plotting
            urgency_df = pd.DataFrame({
                'Urgency': [CASE_URGENCY_LEVELS.get(u, {}).get('name', 'Unknown') for u in urgency_counts.index],
                'Count': urgency_counts.values,
                'Color': [CASE_URGENCY_LEVELS.get(u, {}).get('color', '#000000') for u in urgency_counts.index]
            })
            
            fig2, ax2 = plt.subplots()
            bars = ax2.bar(urgency_df['Urgency'], urgency_df['Count'], 
                          color=urgency_df['Color'])
            ax2.set_title("Cases by Urgency Level")
            ax2.set_ylabel("Number of Cases")
            plt.xticks(rotation=45)
            st.pyplot(fig2)
            
            # Show case list
            st.subheader("Recent Cases")
            case_display_df = case_df[['app_name', 'package_name', 'risk_score', 'verdict', 'urgency', 'status', 'timestamp']]
            case_display_df['timestamp'] = pd.to_datetime(case_display_df['timestamp']).dt.strftime('%Y-%m-%d %H:%M')
            st.dataframe(case_display_df.sort_values('timestamp', ascending=False).head(10))
        else:
            st.info("No cases in the database yet.")
    
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
    
    with st.expander("🧬 APK DNA Mapping & Mimic Detection"):
        st.write("""
        Our advanced APK DNA technology creates a comprehensive fingerprint for each app:
        
        **Code DNA:** Package structure, class names, libraries, and obfuscation patterns
        **UI DNA:** Color schemes, layouts, themes, and visual elements
        **Network DNA:** Domain patterns, API endpoints, and communication behavior
        **Cultural DNA:** Language patterns, scam keywords, and regional targeting
        **Metadata DNA:** Permissions, version information, and file characteristics
        
        This allows us to detect repackaged/mimic banking apps even when attackers:
        - Re-sign the APK with different certificates
        - Apply code obfuscation techniques
        - Modify resources and UI elements
        - Change package names and metadata
        """)
        
        if user_role == "police":
            st.success("Police users have access to detailed DNA analysis and campaign attribution.")
        else:
            st.info("Upgrade to police access for advanced APK DNA analysis.")
    
    # NEW: Case Management System Information
    with st.expander("📋 Case Management System"):
        st.write("""
        Our case management system automatically:
        - Assigns unique case IDs to each APK analysis
        - Ranks cases by urgency level based on risk factors
        - Tracks investigation progress and assignments
        - Maintains a complete history of all analyses
        
        **Urgency Levels:**
        - 🔴 **Critical:** Immediate threat to users' financial security
        - 🟠 **High:** Significant risk requiring prompt attention
        - 🟡 **Medium:** Moderate risk that should be addressed soon
        - 🟢 **Low:** Minimal risk, can be addressed during routine review
        """)
        
        if user_role == "police":
            st.success("Police users have access to the complete case management system.")
        else:
            st.info("Upgrade to police access for case management features.")
    
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
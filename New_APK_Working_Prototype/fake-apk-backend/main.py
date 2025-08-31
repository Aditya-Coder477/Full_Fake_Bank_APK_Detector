# main.py - Fake APK Detector Backend API
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import tempfile
import os
import sys
import json
from datetime import datetime
import pandas as pd
import numpy as np
import re
import hashlib
import zipfile
import tldextract
import whois
from urllib.parse import urlparse
import random
import time

# Create FastAPI app
app = FastAPI(title="Fake APK Detector API", version="1.0.0")

# Enable CORS for mobile app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to your app's domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Constants and configurations
DANGEROUS_PERMISSIONS = [
    "READ_SMS", "RECEIVE_SMS", "SEND_SMS", "RECEIVE_MMS", 
    "RECEIVE_BOOT_COMPLETED", "ACCESS_FINE_LOCATION", 
    "ACCESS_COARSE_LOCATION", "READ_CONTACTS", "READ_CALL_LOG",
    "WRITE_CONTACTS", "CALL_PHONE", "READ_PHONE_STATE"
]

FRAUD_KEYWORDS = {
    "english": {
        "cashback": {"score": 15, "explanation": "Promises of cashback are commonly used in scams to lure victims"},
        "bonus": {"score": 12, "explanation": "Bonus offers are frequently used in fake reward scams"},
        "reward": {"score": 10, "explanation": "Reward promises are often fake incentives in financial scams"},
        "win": {"score": 15, "explanation": "Claims of winning prizes are common in lottery scams"},
        "free": {"score": 10, "explanation": "Free offers are frequently used to trick users into scams"},
        "urgent": {"score": 8, "explanation": "Creates false urgency to bypass careful decision making"},
        "verify": {"score": 8, "explanation": "Often used in verification scams to steal credentials"},
        "lottery": {"score": 20, "explanation": "Lottery claims are among the most common financial scams"},
        "gift": {"score": 10, "explanation": "Fake gift offers are used to trick users"},
        "offer": {"score": 8, "explanation": "Special offers are commonly used in shopping scams"},
        "discount": {"score": 5, "explanation": "Too-good-to-be-true discounts often indicate scams"},
        "claim": {"score": 12, "explanation": "Urging users to claim something is a common scam tactic"},
        "limited": {"score": 7, "explanation": "Creates false scarcity to pressure users"},
        "time": {"score": 5, "explanation": "Time-limited offers create pressure to act without thinking"},
        "winner": {"score": 15, "explanation": "False winner announcements are common in scams"}
    }
}

# Load the official bank app database
def load_bank_database():
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
            'a1b2c3d4e5f67890abcd1234ef56789012345678',
            'b2c3d4e5f67890abcd1234ef5678901234567890',
            'c3d4e5f67890abcd1234ef5678901234567890ab',
            'd4e5f67890abcd1234ef5678901234567890abcd',
            'e5f67890abcd1234ef5678901234567890abcde',
            'f67890abcd1234ef5678901234567890abcdef',
            '7890abcd1234ef5678901234567890abcdef12',
            '890abcd1234ef5678901234567890abcdef123',
            '90abcd1234ef5678901234567890abcdef1234',
            '0abcd1234ef5678901234567890abcdef12345',
            'abcd1234ef5678901234567890abcdef123456',
            'bcd1234ef5678901234567890abcdef1234567',
            'cd1234ef5678901234567890abcdef12345678',
            'd1234ef5678901234567890abcdef123456789',
            '1234ef5678901234567890abcdef1234567890'
        ]
    }
    return pd.DataFrame(data)

# Initialize bank database
df = load_bank_database()

# Fake APK database
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

# Function to extract metadata from APK file
def extract_apk_metadata(apk_path):
    """Extract metadata from APK file - simplified version for demo"""
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
                "hash": "c3d4e5f67890abcd1234ef5678901234567890ab"
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
                "hash": "f1e2d3c4b5a69870fedc1234ba56789098765432"
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

# Function to detect fraud keywords in text
def detect_fraud_keywords(text):
    detected_keywords = []
    total_risk = 0
    
    if not text:
        return detected_keywords, total_risk
    
    text_lower = text.lower()
    
    for lang, keywords in FRAUD_KEYWORDS.items():
        for keyword, keyword_data in keywords.items():
            if keyword.lower() in text_lower:
                detected_keywords.append({
                    "keyword": keyword,
                    "language": lang,
                    "risk_score": keyword_data["score"],
                    "explanation": keyword_data["explanation"]
                })
                total_risk += keyword_data["score"]
    
    return detected_keywords, total_risk

# Function to simulate dynamic analysis
def simulate_dynamic_analysis(apk_path, apk_data):
    """Simulate dynamic analysis by generating behavioral patterns"""
    time.sleep(2)  # Simulate analysis time
    
    # Generate simulated behavioral data
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

# Function to generate APK DNA fingerprint
def generate_apk_dna(apk_path, apk_data):
    """Generate a simplified DNA fingerprint for the APK"""
    dna_fingerprint = {
        "code_dna": hashlib.sha256(apk_data.get("package_name", "").encode()).hexdigest()[:16],
        "ui_dna": hashlib.sha256(apk_data.get("app_name", "").encode()).hexdigest()[:16],
        "network_dna": hashlib.sha256(str(apk_data.get("domains", [])).encode()).hexdigest()[:16],
        "cultural_dna": hashlib.sha256(str(apk_data.get("app_name", "")).encode()).hexdigest()[:16],
        "metadata_dna": hashlib.sha256(str(apk_data.get("permissions", [])).encode()).hexdigest()[:16],
        "full_dna": hashlib.sha256((apk_data.get("package_name", "") + apk_data.get("app_name", "")).encode()).hexdigest()
    }
    
    return dna_fingerprint

# Function to detect mimic apps
def detect_mimic_apps(apk_dna, apk_data):
    """Compare APK DNA with database to detect mimic apps"""
    matches = []
    
    # Check against known patterns (simplified)
    known_patterns = {
        "red_rabbit": {
            "name": "Red Rabbit Gang",
            "targets": ["HDFC", "SBI", "ICICI"],
            "code_patterns": ["com.fake.", "com.clone.", "com.secure."],
        },
        "blue_fox": {
            "name": "Blue Fox Campaign",
            "targets": ["Paytm", "PhonePe", "Google Pay"],
            "code_patterns": ["com.payment.", "com.wallet.", "com.transfer."],
        }
    }
    
    package_name = apk_data.get("package_name", "")
    app_name = apk_data.get("app_name", "")
    
    for pattern_name, pattern_data in known_patterns.items():
        similarity_score = 0
        
        # Check code patterns
        code_patterns = pattern_data.get("code_patterns", [])
        for pattern in code_patterns:
            if package_name.startswith(pattern):
                similarity_score += 25
                break
        
        # Check if targets are in app name
        targets = pattern_data.get("targets", [])
        for target in targets:
            if target.lower() in app_name.lower():
                similarity_score += 15
                break
        
        if similarity_score >= 25:
            matches.append({
                "campaign": pattern_name,
                "campaign_data": pattern_data,
                "similarity_score": similarity_score,
                "match_reasons": [f"Pattern match: {pattern_name}"]
            })
    
    return matches

# Function to compare with official database
def compare_with_official_database(apk_data):
    package_name = apk_data.get('package_name', '')
    
    # Check if package exists in official database
    official_match = df[df['Package Name (ID)'] == package_name]
    
    if not official_match.empty:
        official_data = official_match.iloc[0].to_dict()
        mismatches = []
        
        return {
            "is_official": True,
            "official_data": official_data,
            "mismatches": mismatches,
            "details": "Official banking app"
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
        
        return {
            "is_official": False,
            "is_known_fake": False,
            "details": "Unknown app - not in official database"
        }

# Function to calculate risk score
def calculate_risk_score(apk_data, official_comparison):
    risk_score = 0
    risk_factors = []
    
    # Base score based on official comparison
    if official_comparison['is_official']:
        risk_score += 10
    elif official_comparison.get('is_known_fake', False):
        risk_score += 90
        risk_factors.append("Known fake app: +90")
    else:
        risk_score += 40
        risk_factors.append("Unknown app: +40")
    
    # Check dangerous permissions
    dangerous_perms = apk_data.get('dangerous_permissions', [])
    perm_risk = min(30, len(dangerous_perms) * 5)
    risk_score += perm_risk
    if perm_risk > 0:
        risk_factors.append(f"Dangerous permissions: +{perm_risk}")
    
    # Check for fraud keywords in app name
    app_name = apk_data.get('app_name', '')
    keywords, keyword_risk = detect_fraud_keywords(app_name)
    risk_score += keyword_risk
    if keyword_risk > 0:
        risk_factors.append(f"Fraud keywords in name: +{keyword_risk}")
    
    # Check for suspicious domains
    suspicious_domains = apk_data.get('suspicious_domains', [])
    domain_risk = min(25, len(suspicious_domains) * 8)
    risk_score += domain_risk
    if domain_risk > 0:
        risk_factors.append(f"Suspicious domains: +{domain_risk}")
    
    return min(100, risk_score), risk_factors

# Function to scan APK
def scan_apk(apk_data, apk_path=None):
    # Compare with official database
    official_comparison = compare_with_official_database(apk_data)
    
    # Calculate static risk score
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
    
    # Combine static and dynamic risk scores
    total_risk_score = min(100, static_risk_score + dynamic_risk_score)
    all_risk_factors = static_risk_factors + dynamic_risk_factors
    
    # Increase risk score if mimic apps are detected
    if mimic_detection:
        mimic_risk = min(30, len(mimic_detection) * 10)
        total_risk_score += mimic_risk
        all_risk_factors.append(f"Mimic app detection: +{mimic_risk}")
    
    # Determine verdict
    if official_comparison['is_official'] and not official_comparison.get('mismatches', []):
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
        "dynamic_analysis": dynamic_results,
        "apk_dna": apk_dna,
        "mimic_detection": mimic_detection,
        "fraud_keywords": detect_fraud_keywords(apk_data.get('app_name', ''))[0]
    }

# Function to scan URLs for malicious content
def scan_url_for_malicious_content(url, source="whatsapp"):
    """Scan URLs from WhatsApp/SMS for malicious content"""
    try:
        # Simulate API call delay
        time.sleep(1.0)
        
        # Analyze URL for suspicious patterns
        suspicious_domains = ['.xyz', '.top', '.club', '.loan', '.win', '.bid', '.stream', '.download']
        suspicious_keywords = ['bank', 'pay', 'upi', 'cash', 'reward', 'offer', 'free', 'gift', 'loan']
        
        url_lower = url.lower()
        is_suspicious = any(domain in url_lower for domain in suspicious_domains)
        
        # Additional checks
        if not is_suspicious:
            is_suspicious = any(keyword in url_lower for keyword in suspicious_keywords)
        
        # Check URL length (very long URLs are often suspicious)
        if len(url) > 75:
            is_suspicious = True
        
        # Generate risk score
        risk_score = 75 if is_suspicious else 15
        
        return {
            "safe": not is_suspicious,
            "risk_score": risk_score,
            "suspicious_reason": "Suspicious domain detected" if is_suspicious else "No threats detected",
            "recommendation": "Do not download" if is_suspicious else "Proceed with caution",
            "source": source
        }
        
    except Exception as e:
        return {
            "safe": False,
            "risk_score": 85,
            "error": str(e)
        }

# Function to verify bank account
def verify_bank_account(account_number, ifsc_code, bank_name):
    """Verify bank account details - simulated version"""
    try:
        # Simulate API call delay
        time.sleep(1.5)
        
        # Mock response based on common patterns
        ifsc_prefix = ifsc_code[:4].upper() if ifsc_code else ""
        valid_banks = ["HDFC", "SBI", "ICICI", "AXIS", "KOTAK", "YES", "BOB", "PNB"]
        
        is_valid = any(bank in bank_name.upper() for bank in valid_banks) if bank_name else False
        is_active = random.random() > 0.1  # 90% chance of active account
        
        return {
            "valid": is_valid,
            "active": is_active,
            "account_holder_name": "Simulated Account Holder" if is_valid else None,
            "response_code": "00" if is_valid else "01",
            "message": "Account verification successful" if is_valid else "Invalid account details"
        }
        
    except Exception as e:
        return {
            "valid": False,
            "active": False,
            "error": str(e)
        }

# API Routes
@app.post("/analyze-apk")
async def analyze_apk(file: UploadFile = File(...)):
    """
    Analyze an uploaded APK file
    """
    if not file.filename.endswith('.apk'):
        raise HTTPException(status_code=400, detail="File must be an APK")
    
    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=".apk") as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name
    
    try:
        # Extract metadata from APK
        metadata = extract_apk_metadata(tmp_path)
        
        # Perform analysis
        result = scan_apk(metadata, tmp_path)
        
        # Add additional analysis
        result["fraud_keywords"] = detect_fraud_keywords(metadata.get("app_name", ""))[0]
        result["dynamic_analysis"] = simulate_dynamic_analysis(tmp_path, metadata)
        result["apk_dna"] = generate_apk_dna(tmp_path, metadata)
        result["mimic_detection"] = detect_mimic_apps(result["apk_dna"], metadata)
        
        return JSONResponse({
            "success": True,
            "result": result,
            "metadata": metadata,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return JSONResponse({
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }, status_code=500)
    finally:
        # Clean up
        os.unlink(tmp_path)

@app.post("/analyze-url")
async def analyze_url(url_data: dict):
    """
    Analyze a URL for potential threats (from WhatsApp/SMS)
    """
    try:
        url = url_data.get("url", "")
        source = url_data.get("source", "unknown")
        
        result = scan_url_for_malicious_content(url, source)
        
        return JSONResponse({
            "success": True,
            "result": result,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return JSONResponse({
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }, status_code=500)

@app.post("/verify-bank-account")
async def verify_bank_account_api(account_data: dict):
    """
    Verify bank account details
    """
    try:
        account_number = account_data.get("account_number", "")
        ifsc_code = account_data.get("ifsc_code", "")
        bank_name = account_data.get("bank_name", "")
        
        result = verify_bank_account(account_number, ifsc_code, bank_name)
        
        return JSONResponse({
            "success": True,
            "result": result,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return JSONResponse({
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }, status_code=500)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# Run the application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
import axios from 'axios';
import RNFS from 'react-native-fs';

// Configuration - easily switch between mock and real API
const USE_MOCK_DATA = true; // Set to false when backend is ready
const API_BASE_URL = 'http://localhost:8000'; // Change to your backend URL when ready

// Mock service functions
const mockAnalyzeAPK = async (fileUri) => {
  // Simulate API delay
  await new Promise(resolve => setTimeout(resolve, 2000));
  
  // Generate realistic mock data based on your Streamlit app's output format
  const riskScore = Math.random() * 100;
  let verdict = "✅ Likely Legit";
  if (riskScore > 70) verdict = "❌ Likely Fake";
  else if (riskScore > 30) verdict = "⚠️ Suspicious";
  
  return {
    success: true,
    result: {
      verdict: verdict,
      risk_score: Math.round(riskScore),
      risk_factors: [
        `Suspicious permission pattern: +${Math.round(riskScore/4)}`,
        `Certificate validation: +${Math.round(riskScore/3)}`,
        `Fraud keywords detected: +${Math.round(riskScore/5)}`
      ],
      metadata: {
        app_name: "Example Banking App",
        package_name: "com.example.bank.app",
        version_name: "1.0.0",
        version_code: "100",
        permissions: ["INTERNET", "READ_SMS", "ACCESS_FINE_LOCATION"],
        dangerous_permissions: ["READ_SMS", "ACCESS_FINE_LOCATION"],
        file_size: 42.5
      },
      fraud_keywords: [
        { keyword: "cashback", language: "english", risk_score: 15, explanation: "Promises of cashback are commonly used in scams" },
        { keyword: "reward", language: "english", risk_score: 10, explanation: "Reward promises are often fake incentives" }
      ],
      dynamic_analysis: {
        behaviors: {
          network_activity: [
            { type: "HTTP_REQUEST", destination: "api.suspicious.com", frequency: 12, data_sent: 2048 }
          ],
          permission_usage: [
            { permission: "READ_SMS", frequency: 8, context: "RUNTIME" }
          ]
        },
        risk_score: 25
      },
      apk_dna: {
        code_dna: "a1b2c3d4e5f67890",
        ui_dna: "b2c3d4e5f67890ab",
        network_dna: "c3d4e5f67890abcd",
        cultural_dna: "d4e5f67890abcde",
        metadata_dna: "e5f67890abcdef12",
        full_dna: "a1b2c3d4e5f67890abcd1234ef56789012345678"
      },
      mimic_detection: riskScore > 60 ? [
        {
          campaign: "red_rabbit",
          campaign_data: { name: "Red Rabbit Gang" },
          similarity_score: Math.round(riskScore - 20),
          match_reasons: ["Code pattern match: com.fake.", "Cultural pattern match: cashback"]
        }
      ] : [],
      case_id: `CASE-${Math.floor(1000 + Math.random() * 9000)}`,
      urgency: riskScore > 80 ? "critical" : riskScore > 60 ? "high" : riskScore > 30 ? "medium" : "low"
    },
    timestamp: new Date().toISOString()
  };
};

const mockAnalyzeURL = async (url, source) => {
  await new Promise(resolve => setTimeout(resolve, 1500));
  
  const isSuspicious = url.includes('.xyz') || url.includes('.top') || url.includes('cashback');
  const riskScore = isSuspicious ? 75 : 15;
  
  return {
    success: true,
    result: {
      safe: !isSuspicious,
      risk_score: riskScore,
      suspicious_reason: isSuspicious ? "Suspicious domain detected" : "No threats detected",
      recommendation: isSuspicious ? "Do not download" : "Proceed with caution",
      url: url,
      source: source
    },
    timestamp: new Date().toISOString()
  };
};

const mockVerifyBankAccount = async (accountData) => {
  await new Promise(resolve => setTimeout(resolve, 1000));
  
  const isValid = accountData.account_number && accountData.ifsc_code && accountData.bank_name;
  
  return {
    success: true,
    result: {
      valid: isValid,
      active: isValid,
      account_holder_name: isValid ? "Verified Account Holder" : null,
      message: isValid ? "Account verification successful" : "Invalid account details"
    },
    timestamp: new Date().toISOString()
  };
};

// Real API functions (will be implemented later)
const realAnalyzeAPK = async (fileUri) => {
  try {
    // Read file as base64
    const fileData = await RNFS.readFile(fileUri, 'base64');
    const fileName = fileUri.split('/').pop();
    
    // Send to backend
    const response = await axios.post(`${API_BASE_URL}/api/v1/analyze-apk`, {
      file: fileData,
      filename: fileName
    }, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
    
    return response.data;
  } catch (error) {
    console.error('APK analysis error:', error);
    throw new Error(error.response?.data?.error || 'Failed to analyze APK');
  }
};

const realAnalyzeURL = async (url, source) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/api/v1/analyze-url`, {
      url,
      source
    });
    
    return response.data;
  } catch (error) {
    console.error('URL analysis error:', error);
    throw new Error(error.response?.data?.error || 'Failed to analyze URL');
  }
};

const realVerifyBankAccount = async (accountData) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/api/v1/verify-bank-account`, accountData);
    return response.data;
  } catch (error) {
    console.error('Bank verification error:', error);
    throw new Error(error.response?.data?.error || 'Failed to verify bank account');
  }
};

// Export the appropriate functions based on configuration
export const analyzeAPK = USE_MOCK_DATA ? mockAnalyzeAPK : realAnalyzeAPK;
export const analyzeURL = USE_MOCK_DATA ? mockAnalyzeURL : realAnalyzeURL;
export const verifyBankAccount = USE_MOCK_DATA ? mockVerifyBankAccount : realVerifyBankAccount;

// Helper function to switch between modes (useful for testing)
export const setApiMode = (useMockData) => {
  // This would need a more sophisticated implementation in a real app
  console.warn('API mode cannot be changed dynamically in this implementation. ' +
               'Set USE_MOCK_DATA constant to change mode.');
};

// Export configuration for informational purposes
export const apiConfig = {
  useMockData: USE_MOCK_DATA,
  apiBaseUrl: API_BASE_URL,
  isMockMode: USE_MOCK_DATA
};

// Mock service that simulates your backend responses
export const analyzeAPK = async (fileUri) => {
  // Simulate API delay
  await new Promise(resolve => setTimeout(resolve, 2000));
  
  // Return mock data that matches your expected backend response format
  return {
    success: true,
    result: {
      verdict: "⚠️ Suspicious",
      risk_score: 65,
      risk_factors: [
        "Suspicious permission pattern: +20",
        "Unknown certificate: +25",
        "Fraud keywords detected: +20"
      ],
      metadata: {
        app_name: "HDFC Bank UPI Cashback",
        package_name: "com.fake.hdfc.bank",
        version_name: "1.0.0",
        permissions: ["INTERNET", "READ_SMS", "RECEIVE_SMS", "ACCESS_FINE_LOCATION"],
        dangerous_permissions: ["READ_SMS", "RECEIVE_SMS", "ACCESS_FINE_LOCATION"]
      },
      fraud_keywords: [
        { keyword: "cashback", language: "english", risk_score: 15 },
        { keyword: "reward", language: "english", risk_score: 10 }
      ]
    },
    timestamp: new Date().toISOString()
  };
};

export const analyzeURL = async (url, source) => {
  await new Promise(resolve => setTimeout(resolve, 1500));
  
  return {
    success: true,
    result: {
      safe: false,
      risk_score: 75,
      suspicious_reason: "Suspicious TLD",
      recommendation: "Do not download",
      url: url,
      source: source
    },
    timestamp: new Date().toISOString()
  };
};

export const verifyBankAccount = async (accountData) => {
  await new Promise(resolve => setTimeout(resolve, 1000));
  
  return {
    success: true,
    result: {
      valid: true,
      active: true,
      account_holder_name: "John Doe",
      message: "Account verification successful"
    },
    timestamp: new Date().toISOString()
  };
};
// src/config/config.js
const Config = {
  API_BASE_URL: 'http://192.168.1.100:8000', // Replace with your local IP
  ENVIRONMENT: 'development',
  
  // Feature flags
  FEATURES: {
    APK_ANALYSIS: true,
    URL_SCANNING: true,
    BANK_VERIFICATION: true,
    UPI_VERIFICATION: true,
    OFFLINE_MODE: false,
  },
  
  // API endpoints
  ENDPOINTS: {
    ANALYZE_APK: '/analyze-apk',
    ANALYZE_URL: '/analyze-url',
    VERIFY_BANK: '/verify-bank-account',
    HEALTH: '/health',
  },
};

export default Config;
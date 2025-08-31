// src/services/apiService.js
import axios from 'axios';
import Config from '../config/config';
import { Platform } from 'react-native';

// Create axios instance
const api = axios.create({
  baseURL: Config.API_BASE_URL,
  timeout: 30000, // 30 second timeout
});

// APK analysis function
export const analyzeAPK = async (fileUri) => {
  try {
    // For React Native, we need to create a FormData object
    const formData = new FormData();
    formData.append('file', {
      uri: fileUri,
      type: 'application/vnd.android.package-archive',
      name: 'app.apk',
    });

    // Send to backend
    const response = await api.post(Config.ENDPOINTS.ANALYZE_APK, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    
    return response.data;
  } catch (error) {
    console.error('APK analysis error:', error);
    throw new Error(error.response?.data?.error || 'Failed to analyze APK');
  }
};

// URL analysis function
export const analyzeURL = async (url, source = 'unknown') => {
  try {
    const response = await api.post(Config.ENDPOINTS.ANALYZE_URL, {
      url,
      source
    });
    
    return response.data;
  } catch (error) {
    console.error('URL analysis error:', error);
    throw new Error(error.response?.data?.error || 'Failed to analyze URL');
  }
};

// Bank verification function
export const verifyBankAccount = async (accountData) => {
  try {
    const response = await api.post(Config.ENDPOINTS.VERIFY_BANK, accountData);
    return response.data;
  } catch (error) {
    console.error('Bank verification error:', error);
    throw new Error(error.response?.data?.error || 'Failed to verify bank account');
  }
};

// Health check function
export const healthCheck = async () => {
  try {
    const response = await api.get(Config.ENDPOINTS.HEALTH);
    return response.data;
  } catch (error) {
    console.error('Health check error:', error);
    throw new Error('Backend is not available');
  }
};

export default api;
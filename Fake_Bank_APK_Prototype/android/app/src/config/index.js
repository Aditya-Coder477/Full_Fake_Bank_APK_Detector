// src/config/index.js
import { APP_ENV, API_BASE_URL, USE_MOCK_DATA, ENABLE_ANALYTICS, DEBUG_MODE } from '@env';

export const Config = {
  environment: APP_ENV || 'development',
  api: {
    baseUrl: API_BASE_URL || 'http://localhost:8000',
    timeout: 30000,
  },
  features: {
    useMockData: USE_MOCK_DATA === 'true',
    enableAnalytics: ENABLE_ANALYTICS === 'true',
    debugMode: DEBUG_MODE === 'true',
  },
  app: {
    name: 'Fake APK Detector',
    version: '1.0.0',
  },
};

// Helper function to check environment
export const isDevelopment = () => Config.environment === 'development';
export const isProduction = () => Config.environment === 'production';
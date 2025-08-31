// app.config.js - in project root
const IS_DEV = process.env.NODE_ENV === 'development';

export default {
  name: 'Fake APK Detector',
  version: '1.0.0',
  extra: {
    environment: process.env.APP_ENV || 'development',
    apiBaseUrl: process.env.API_BASE_URL || 'http://localhost:8000',
    useMockData: process.env.USE_MOCK_DATA !== 'false',
    enableAnalytics: process.env.ENABLE_ANALYTICS === 'true',
    debugMode: process.env.DEBUG_MODE === 'true',
  },
};
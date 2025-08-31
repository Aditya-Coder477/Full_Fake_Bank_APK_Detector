// App configuration with environment support
export const AppConfig = {
  // Current environment
  environment: __DEV__ ? 'development' : 'production',
  
  // Feature flags
  features: {
    useMockData: true, // Will be false when backend is ready
    enableAnalytics: true,
    crashReporting: true,
  },
  
  // API configuration
  api: {
    baseUrl: 'https://your-future-backend.com/api', // Placeholder for now
    timeout: 30000,
    retryAttempts: 3,
  },
  
  // App settings
  settings: {
    maxFileSize: 100 * 1024 * 1024, // 100MB
    supportedApkVersions: ['Android 5.0+'],
  }
};

// Method to update config when backend is ready
export const updateConfigForBackend = (backendUrl) => {
  AppConfig.features.useMockData = false;
  AppConfig.api.baseUrl = backendUrl;
  console.log('Configuration updated for backend:', backendUrl);
};
import { AppConfig } from '../config/AppConfig';

// Mock analytics service that will work with or without backend
export const AnalyticsService = {
  // Track screen views
  trackScreenView: (screenName) => {
    console.log(`Screen viewed: ${screenName}`);
    if (AppConfig.features.enableAnalytics) {
      // Here you would integrate with Firebase Analytics, Mixpanel, etc.
      // For now, just log to console
      if (!AppConfig.features.useMockData) {
        // Send to real analytics when backend is connected
        // api.post('/analytics/screen-view', { screen: screenName });
      }
    }
  },
  
  // Track APK analysis events
  trackAnalysis: (result) => {
    const eventData = {
      risk_score: result.risk_score,
      verdict: result.verdict,
      timestamp: new Date().toISOString()
    };
    
    console.log('APK analysis event:', eventData);
    
    if (AppConfig.features.enableAnalytics && !AppConfig.features.useMockData) {
      // Send to real analytics when backend is connected
      // api.post('/analytics/apk-analysis', eventData);
    }
  },
  
  // Track errors
  trackError: (error, context) => {
    console.error(`Error in ${context}:`, error);
    
    if (AppConfig.features.crashReporting) {
      // Integrate with crash reporting tools like Sentry, Crashlytics
      if (!AppConfig.features.useMockData) {
        // Send to real error tracking when backend is connected
        // api.post('/analytics/error', { error: error.message, context });
      }
    }
  }
};
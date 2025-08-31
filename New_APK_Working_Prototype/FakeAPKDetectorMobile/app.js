// App.js (main entry point)
import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import { Provider as PaperProvider } from 'react-native-paper';

// Import screens
import HomeScreen from './src/screens/HomeScreen';
import APKAnalysisScreen from './src/screens/APKAnalysisScreen';
import URLScannerScreen from './src/screens/URLScannerScreen';
import BankVerificationScreen from './src/screens/BankVerificationScreen';
import UPIVerificationScreen from './src/screens/UPIVerificationScreen';
import ResultsScreen from './src/screens/ResultsScreen';

const Stack = createStackNavigator();

const App = () => {
  return (
    <PaperProvider>
      <NavigationContainer>
        <Stack.Navigator initialRouteName="Home">
          <Stack.Screen 
            name="Home" 
            component={HomeScreen}
            options={{ title: 'Fake APK Detector' }}
          />
          <Stack.Screen 
            name="APKAnalysis" 
            component={APKAnalysisScreen}
            options={{ title: 'APK Analysis' }}
          />
          <Stack.Screen 
            name="URLScanner" 
            component={URLScannerScreen}
            options={{ title: 'URL Scanner' }}
          />
          <Stack.Screen 
            name="BankVerification" 
            component={BankVerificationScreen}
            options={{ title: 'Bank Verification' }}
          />
          <Stack.Screen 
            name="UPIVerification" 
            component={UPIVerificationScreen}
            options={{ title: 'UPI Verification' }}
          />
          <Stack.Screen 
            name="Results" 
            component={ResultsScreen}
            options={{ title: 'Analysis Results' }}
          />
        </Stack.Navigator>
      </NavigationContainer>
    </PaperProvider>
  );
};

export default App;
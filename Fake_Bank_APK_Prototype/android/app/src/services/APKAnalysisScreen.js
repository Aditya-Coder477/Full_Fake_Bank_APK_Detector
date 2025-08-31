import React, { useState } from 'react';
import { View, StyleSheet, Alert, ScrollView } from 'react-native';
import { Button, ProgressBar, Text, Card, ActivityIndicator } from 'react-native-paper';
import DocumentPicker from 'react-native-document-picker';
import { analyzeAPK } from '../services/apiService';

const APKAnalysisScreen = ({ navigation }) => {
  const [isLoading, setIsLoading] = useState(false);

  const handleAPKUpload = async () => {
    try {
      const res = await DocumentPicker.pick({
        type: [DocumentPicker.types.allFiles],
      });

      setIsLoading(true);
      const result = await analyzeAPK(res.uri);
      
      navigation.navigate('Results', { 
        result: result,
        analysisType: 'APK',
        fileName: res.name
      });

    } catch (err) {
      if (DocumentPicker.isCancel(err)) {
        // User cancelled the picker
      } else {
        Alert.alert('Error', 'Failed to analyze APK: ' + err.message);
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <ScrollView style={styles.container}>
      <Card style={styles.card}>
        <Card.Content>
          <Text variant="titleLarge">APK File Analysis</Text>
          <Text variant="bodyMedium" style={styles.description}>
            Upload an APK file to analyze it for security threats. 
            The app will check for suspicious patterns, fake signatures, 
            and compare against known banking apps.
          </Text>
        </Card.Content>
      </Card>

      <Button 
        mode="contained" 
        onPress={handleAPKUpload}
        disabled={isLoading}
        style={styles.button}
        icon="file-upload"
      >
        {isLoading ? 'Analyzing...' : 'Select APK File'}
      </Button>

      {isLoading && (
        <Card style={styles.card}>
          <Card.Content>
            <ActivityIndicator animating={true} />
            <Text style={styles.analyzingText}>Analyzing APK file...</Text>
          </Card.Content>
        </Card>
      )}

      <Card style={styles.card}>
        <Card.Content>
          <Text variant="titleMedium">What we analyze:</Text>
          <Text>• APK metadata and certificates</Text>
          <Text>• Signature verification</Text>
          <Text>• Permission analysis</Text>
          <Text>• Fraud keyword detection</Text>
          <Text>• Known scam pattern matching</Text>
        </Card.Content>
      </Card>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 16,
  },
  card: {
    marginBottom: 16,
  },
  button: {
    marginVertical: 16,
  },
  description: {
    marginVertical: 8,
  },
  analyzingText: {
    textAlign: 'center',
    marginTop: 8,
  }
});

export default APKAnalysisScreen;
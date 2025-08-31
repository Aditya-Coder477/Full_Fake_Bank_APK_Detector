// src/screens/APKAnalysisScreen.js
import React, { useState } from 'react';
import { View, StyleSheet, Alert, ScrollView } from 'react-native';
import { Button, ProgressBar, Text, Card } from 'react-native-paper';
import DocumentPicker from 'react-native-document-picker';
import { analyzeAPK } from '../services/apiService';

const APKAnalysisScreen = ({ navigation }) => {
  const [isLoading, setIsLoading] = useState(false);
  const [progress, setProgress] = useState(0);

  const handleAPKUpload = async () => {
    try {
      const res = await DocumentPicker.pick({
        type: [DocumentPicker.types.allFiles],
      });

      setIsLoading(true);
      setProgress(0.3);

      // Analyze the APK
      const result = await analyzeAPK(res.uri);
      setProgress(1.0);

      // Navigate to results screen
      navigation.navigate('Results', { 
        result: result,
        analysisType: 'APK'
      });

    } catch (err) {
      if (DocumentPicker.isCancel(err)) {
        // User cancelled the picker
      } else {
        Alert.alert('Error', 'Failed to analyze APK: ' + err.message);
      }
    } finally {
      setIsLoading(false);
      setProgress(0);
    }
  };

  return (
    <ScrollView style={styles.container}>
      <Card style={styles.card}>
        <Card.Content>
          <Text variant="titleLarge">APK File Analysis</Text>
          <Text variant="bodyMedium" style={styles.description}>
            Upload an APK file to analyze it for security threats, fake signatures, 
            and potential malware. Our system will check against known banking apps 
            and detect suspicious patterns.
          </Text>
        </Card.Content>
      </Card>

      {isLoading && (
        <Card style={styles.card}>
          <Card.Content>
            <Text>Analyzing APK...</Text>
            <ProgressBar progress={progress} style={styles.progress} />
          </Card.Content>
        </Card>
      )}

      <Button 
        mode="contained" 
        onPress={handleAPKUpload}
        disabled={isLoading}
        style={styles.button}
        icon="file-upload"
      >
        Select APK File
      </Button>

      <Card style={styles.card}>
        <Card.Content>
          <Text variant="titleMedium">What we analyze:</Text>
          <Text>• APK metadata and certificates</Text>
          <Text>• Signature verification</Text>
          <Text>• Permission analysis</Text>
          <Text>• Fraud keyword detection</Text>
          <Text>• Known scam pattern matching</Text>
          <Text>• Bank app database comparison</Text>
        </Card.Content>
      </Card>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 10,
  },
  card: {
    marginBottom: 15,
  },
  button: {
    marginVertical: 15,
    padding: 5,
  },
  progress: {
    marginTop: 10,
    height: 10,
  },
  description: {
    marginVertical: 10,
  }
});

export default APKAnalysisScreen;
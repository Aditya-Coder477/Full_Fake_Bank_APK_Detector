// src/screens/URLScannerScreen.js
import React, { useState } from 'react';
import { View, StyleSheet, Alert, ScrollView } from 'react-native';
import { TextInput, Button, Card, Text } from 'react-native-paper';
import { analyzeURL } from '../services/apiService';

const URLScannerScreen = ({ navigation }) => {
  const [url, setUrl] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleScanURL = async () => {
    if (!url) {
      Alert.alert('Error', 'Please enter a URL');
      return;
    }

    try {
      setIsLoading(true);
      const result = await analyzeURL(url, 'manual');
      
      navigation.navigate('Results', {
        result: result,
        analysisType: 'URL'
      });
    } catch (error) {
      Alert.alert('Error', error.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <ScrollView style={styles.container}>
      <Card style={styles.card}>
        <Card.Content>
          <Text variant="titleLarge">URL Scanner</Text>
          <Text variant="bodyMedium">
            Enter a URL to check for malicious content, phishing attempts, or scam websites.
          </Text>
        </Card.Content>
      </Card>

      <TextInput
        label="URL to scan"
        value={url}
        onChangeText={setUrl}
        style={styles.input}
        placeholder="https://example.com"
        keyboardType="url"
      />

      <Button
        mode="contained"
        onPress={handleScanURL}
        loading={isLoading}
        disabled={isLoading}
        style={styles.button}
      >
        Scan URL
      </Button>

      <Card style={styles.card}>
        <Card.Content>
          <Text variant="titleMedium">What we check:</Text>
          <Text>• Suspicious domain patterns</Text>
          <Text>• Newly registered domains</Text>
          <Text>• Known phishing patterns</Text>
          <Text>• SSL certificate validity</Text>
          <Text>• Redirect chains and final destination</Text>
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
  input: {
    marginBottom: 15,
  },
  button: {
    marginBottom: 20,
  },
});

export default URLScannerScreen;
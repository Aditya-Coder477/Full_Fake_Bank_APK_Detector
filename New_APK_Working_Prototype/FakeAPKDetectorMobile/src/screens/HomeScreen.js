// src/screens/HomeScreen.js
import React from 'react';
import { View, StyleSheet, ScrollView } from 'react-native';
import { Card, Title, Paragraph, Button, Text } from 'react-native-paper';

const HomeScreen = ({ navigation }) => {
  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <Text variant="headlineMedium" style={styles.title}>
          Fake APK Detector
        </Text>
        <Text variant="bodyMedium" style={styles.subtitle}>
          Protect yourself from fake banking apps and financial scams
        </Text>
      </View>

      <Card style={styles.card}>
        <Card.Content>
          <Title>APK Analysis</Title>
          <Paragraph>Upload and analyze APK files for security threats</Paragraph>
        </Card.Content>
        <Card.Actions>
          <Button 
            mode="contained" 
            onPress={() => navigation.navigate('APKAnalysis')}
            style={styles.button}
          >
            Analyze APK
          </Button>
        </Card.Actions>
      </Card>

      <Card style={styles.card}>
        <Card.Content>
          <Title>URL Scanner</Title>
          <Paragraph>Scan URLs from WhatsApp, SMS, or other sources</Paragraph>
        </Card.Content>
        <Card.Actions>
          <Button 
            mode="contained" 
            onPress={() => navigation.navigate('URLScanner')}
            style={styles.button}
          >
            Scan URL
          </Button>
        </Card.Actions>
      </Card>

      <Card style={styles.card}>
        <Card.Content>
          <Title>Bank Verification</Title>
          <Paragraph>Verify bank account details</Paragraph>
        </Card.Content>
        <Card.Actions>
          <Button 
            mode="contained" 
            onPress={() => navigation.navigate('BankVerification')}
            style={styles.button}
          >
            Verify Account
          </Button>
        </Card.Actions>
      </Card>

      <Card style={styles.card}>
        <Card.Content>
          <Title>UPI Verification</Title>
          <Paragraph>Check UPI IDs for suspicious patterns</Paragraph>
        </Card.Content>
        <Card.Actions>
          <Button 
            mode="contained" 
            onPress={() => navigation.navigate('UPIVerification')}
            style={styles.button}
          >
            Verify UPI
          </Button>
        </Card.Actions>
      </Card>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 10,
    backgroundColor: '#f5f5f5',
  },
  header: {
    alignItems: 'center',
    marginVertical: 20,
    padding: 10,
  },
  title: {
    fontWeight: 'bold',
    color: '#2196F3',
    marginBottom: 5,
  },
  subtitle: {
    textAlign: 'center',
    color: '#666',
  },
  card: {
    marginBottom: 15,
    elevation: 3,
  },
  button: {
    marginVertical: 5,
  },
});

export default HomeScreen;
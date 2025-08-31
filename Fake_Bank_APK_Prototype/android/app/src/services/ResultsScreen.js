import React from 'react';
import { View, StyleSheet, ScrollView } from 'react-native';
import { Card, Text, Chip, Divider, Button } from 'react-native-paper';

const ResultsScreen = ({ route, navigation }) => {
  const { result, analysisType, fileName } = route.params;
  
  if (!result || !result.success) {
    return (
      <View style={styles.container}>
        <Text>Error analyzing file. Please try again.</Text>
        <Button onPress={() => navigation.goBack()}>Go Back</Button>
      </View>
    );
  }

  const analysisResult = result.result;
  const riskScore = analysisResult.risk_score || 0;
  
  // Determine risk level
  let riskLevel = 'Low';
  let riskColor = '#4CAF50';
  
  if (riskScore >= 70) {
    riskLevel = 'High';
    riskColor = '#F44336';
  } else if (riskScore >= 30) {
    riskLevel = 'Medium';
    riskColor = '#FF9800';
  }

  return (
    <ScrollView style={styles.container}>
      <Card style={styles.card}>
        <Card.Content>
          <Text variant="titleLarge">Analysis Results</Text>
          <Text variant="bodyMedium">Type: {analysisType}</Text>
          {fileName && <Text variant="bodyMedium">File: {fileName}</Text>}
          
          <View style={styles.riskContainer}>
            <Text variant="titleMedium">Risk Assessment:</Text>
            <View style={[styles.riskIndicator, { backgroundColor: riskColor }]}>
              <Text style={styles.riskScoreText}>{riskScore}/100</Text>
              <Text style={styles.riskLevelText}>{riskLevel} Risk</Text>
            </View>
          </View>
          
          <Chip 
            icon={riskScore < 30 ? "check-circle" : riskScore < 70 ? "alert-circle" : "close-circle"}
            style={[styles.verdictChip, { backgroundColor: riskColor }]}
            textStyle={{ color: 'white' }}
          >
            Verdict: {analysisResult.verdict}
          </Chip>
        </Card.Content>
      </Card>

      {analysisResult.metadata && (
        <Card style={styles.card}>
          <Card.Content>
            <Text variant="titleMedium">App Information</Text>
            <Text>Name: {analysisResult.metadata.app_name}</Text>
            <Text>Package: {analysisResult.metadata.package_name}</Text>
            <Text>Version: {analysisResult.metadata.version_name}</Text>
          </Card.Content>
        </Card>
      )}

      {analysisResult.risk_factors && analysisResult.risk_factors.length > 0 && (
        <Card style={styles.card}>
          <Card.Content>
            <Text variant="titleMedium">Risk Factors</Text>
            {analysisResult.risk_factors.map((factor, index) => (
              <Text key={index} style={styles.riskFactor}>• {factor}</Text>
            ))}
          </Card.Content>
        </Card>
      )}

      <Card style={styles.card}>
        <Card.Content>
          <Text variant="titleMedium">Recommendations</Text>
          {riskScore < 30 ? (
            <Text>This app appears to be safe. You can proceed with installation.</Text>
          ) : riskScore < 70 ? (
            <Text>Be cautious with this app. Review permissions and consider alternatives.</Text>
          ) : (
            <Text>Do not install this app. It appears to be fake or malicious.</Text>
          )}
        </Card.Content>
      </Card>

      <Button 
        mode="contained" 
        onPress={() => navigation.navigate('Home')}
        style={styles.button}
      >
        Analyze Another File
      </Button>
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
  riskContainer: {
    marginVertical: 16,
  },
  riskIndicator: {
    padding: 16,
    borderRadius: 8,
    alignItems: 'center',
    marginVertical: 8,
  },
  riskScoreText: {
    color: 'white',
    fontSize: 24,
    fontWeight: 'bold',
  },
  riskLevelText: {
    color: 'white',
    fontSize: 16,
  },
  verdictChip: {
    marginTop: 16,
    alignSelf: 'flex-start',
  },
  riskFactor: {
    marginVertical: 4,
  },
  button: {
    marginVertical: 16,
  }
});

export default ResultsScreen;
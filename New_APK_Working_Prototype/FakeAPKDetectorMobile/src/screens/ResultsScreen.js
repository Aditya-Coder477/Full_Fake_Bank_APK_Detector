// src/screens/ResultsScreen.js
import React from 'react';
import { View, StyleSheet, ScrollView } from 'react-native';
import { Card, Text, Chip, ProgressBar, Divider } from 'react-native-paper';

const ResultsScreen = ({ route }) => {
  const { result, analysisType } = route.params;
  
  if (!result || !result.success) {
    return (
      <View style={styles.container}>
        <Text>Error analyzing file. Please try again.</Text>
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
          
          <View style={styles.riskContainer}>
            <Text variant="titleMedium">Risk Assessment:</Text>
            <View style={styles.riskScoreContainer}>
              <ProgressBar 
                progress={riskScore / 100} 
                color={riskColor}
                style={styles.progressBar}
              />
              <Text style={[styles.riskScore, { color: riskColor }]}>
                {riskScore}/100 ({riskLevel} Risk)
              </Text>
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

      {analysisResult.fraud_keywords && analysisResult.fraud_keywords.length > 0 && (
        <Card style={styles.card}>
          <Card.Content>
            <Text variant="titleMedium">Fraud Keywords Detected</Text>
            {analysisResult.fraud_keywords.slice(0, 5).map((keyword, index) => (
              <Chip key={index} style={styles.keywordChip} mode="outlined">
                {keyword.keyword} ({keyword.language})
              </Chip>
            ))}
            {analysisResult.fraud_keywords.length > 5 && (
              <Text>+ {analysisResult.fraud_keywords.length - 5} more keywords</Text>
            )}
          </Card.Content>
        </Card>
      )}

      {analysisResult.mimic_detection && analysisResult.mimic_detection.length > 0 && (
        <Card style={styles.card}>
          <Card.Content>
            <Text variant="titleMedium">Mimic App Detection</Text>
            {analysisResult.mimic_detection.map((detection, index) => (
              <View key={index} style={styles.mimicItem}>
                <Text variant="bodyMedium">{detection.campaign}</Text>
                <Text variant="bodySmall">Similarity: {detection.similarity_score}%</Text>
                <Divider style={styles.divider} />
              </View>
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
  riskContainer: {
    marginVertical: 15,
  },
  riskScoreContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 5,
  },
  progressBar: {
    flex: 1,
    height: 10,
    marginRight: 10,
  },
  riskScore: {
    fontWeight: 'bold',
    fontSize: 16,
  },
  verdictChip: {
    marginTop: 10,
    alignSelf: 'flex-start',
  },
  keywordChip: {
    margin: 2,
  },
  mimicItem: {
    marginVertical: 5,
  },
  divider: {
    marginVertical: 5,
  }
});

export default ResultsScreen;
import React, { useState } from 'react';
import { View, StyleSheet } from 'react-native';
import { TextInput, Button, Card, Text } from 'react-native-paper';

const FeedbackForm = () => {
  const [feedback, setFeedback] = useState('');
  const [submitted, setSubmitted] = useState(false);

  const submitFeedback = async () => {
    // For now, just store locally
    console.log('User feedback:', feedback);
    setSubmitted(true);
    
    // When backend is ready:
    // await api.post('/feedback', { message: feedback });
    
    setTimeout(() => setSubmitted(false), 3000);
  };

  if (submitted) {
    return (
      <Card style={styles.card}>
        <Card.Content>
          <Text>Thank you for your feedback!</Text>
        </Card.Content>
      </Card>
    );
  }

  return (
    <Card style={styles.card}>
      <Card.Content>
        <Text variant="titleMedium">We'd love your feedback!</Text>
        <Text variant="bodySmall">
          This app is currently using mock data. Real APK analysis coming soon!
        </Text>
        
        <TextInput
          label="Your feedback"
          value={feedback}
          onChangeText={setFeedback}
          multiline
          numberOfLines={4}
          style={styles.input}
        />
        
        <Button 
          mode="contained" 
          onPress={submitFeedback}
          disabled={!feedback.trim()}
        >
          Submit Feedback
        </Button>
      </Card.Content>
    </Card>
  );
};
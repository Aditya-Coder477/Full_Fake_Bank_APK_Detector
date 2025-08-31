import { analyzeAPK } from '../services/apiService';
import { render, fireEvent, waitFor } from '@testing-library/react-native';
import APKAnalysisScreen from '../screens/APKAnalysisScreen';

// Mock the document picker
jest.mock('react-native-document-picker', () => ({
  pick: jest.fn(() => Promise.resolve({ uri: 'test.apk', name: 'test.apk' })),
  types: { allFiles: 'allFiles' }
}));

// Mock navigation
const mockNavigate = jest.fn();
const mockNavigation = { navigate: mockNavigate };

describe('APK Analysis Screen', () => {
  it('should analyze APK and show results', async () => {
    const { getByText, queryByText } = render(
      <APKAnalysisScreen navigation={mockNavigation} />
    );

    // Trigger file selection
    fireEvent.press(getByText('Select APK File'));
    
    // Wait for analysis to complete
    await waitFor(() => {
      expect(mockNavigate).toHaveBeenCalledWith('Results', expect.anything());
    });
  });

  it('should display loading state during analysis', async () => {
    const { getByText, queryByText } = render(
      <APKAnalysisScreen navigation={mockNavigation} />
    );

    // Initially no loading indicator
    expect(queryByText('Analyzing APK file...')).toBeNull();
    
    // Trigger analysis
    fireEvent.press(getByText('Select APK File'));
    
    // Should show loading state
    expect(getByText('Analyzing...')).toBeTruthy();
  });
});
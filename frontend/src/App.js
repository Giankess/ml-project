import React, { useState } from 'react';
import { 
  Container, 
  Box, 
  Typography, 
  Button, 
  Paper,
  CircularProgress,
  TextField
} from '@mui/material';
import { useDropzone } from 'react-dropzone';
import axios from 'axios';

function App() {
  const [file, setFile] = useState(null);
  const [documentId, setDocumentId] = useState(null);
  const [loading, setLoading] = useState(false);
  const [feedback, setFeedback] = useState('');
  const [analysis, setAnalysis] = useState(null);

  const onDrop = async (acceptedFiles) => {
    const uploadedFile = acceptedFiles[0];
    setFile(uploadedFile);
    setLoading(true);

    try {
      const formData = new FormData();
      formData.append('file', uploadedFile);

      const response = await axios.post('http://localhost:8000/upload', formData);
      setDocumentId(response.data.document_id);
      
      // Analyze the document
      const analysisResponse = await axios.post(`http://localhost:8000/analyze/${response.data.document_id}`);
      setAnalysis(analysisResponse.data);
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  const { getRootProps, getInputProps } = useDropzone({
    onDrop,
    accept: {
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx']
    },
    multiple: false
  });

  const handleAcceptSuggestions = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`http://localhost:8000/download/${documentId}?clean=true`);
      // Handle the download of the clean document
      window.location.href = response.data.file_path;
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmitFeedback = async () => {
    setLoading(true);
    try {
      const response = await axios.post(`http://localhost:8000/feedback/${documentId}`, {
        feedback: feedback
      });
      setAnalysis(response.data.new_analysis);
      setFeedback('');
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="md">
      <Box sx={{ my: 4 }}>
        <Typography variant="h3" component="h1" gutterBottom align="center">
          NDA Validator
        </Typography>

        <Paper 
          {...getRootProps()} 
          sx={{ 
            p: 3, 
            mb: 3, 
            textAlign: 'center',
            cursor: 'pointer',
            backgroundColor: '#f5f5f5'
          }}
        >
          <input {...getInputProps()} />
          <Typography>
            {file ? `Selected file: ${file.name}` : 'Drag and drop an NDA document here, or click to select'}
          </Typography>
        </Paper>

        {loading && (
          <Box sx={{ display: 'flex', justifyContent: 'center', my: 2 }}>
            <CircularProgress />
          </Box>
        )}

        {analysis && (
          <Box sx={{ mt: 3 }}>
            <Typography variant="h5" gutterBottom>
              Analysis Results
            </Typography>
            
            {analysis.clauses.map((clause, index) => (
              <Paper key={index} sx={{ p: 2, mb: 2 }}>
                <Typography variant="subtitle1" color="error">
                  Original: {clause.original}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Issue: {clause.issue}
                </Typography>
                <Typography variant="subtitle1" color="primary">
                  Suggestion: {clause.suggestion}
                </Typography>
              </Paper>
            ))}

            <Box sx={{ mt: 3 }}>
              <TextField
                fullWidth
                multiline
                rows={4}
                label="Feedback"
                value={feedback}
                onChange={(e) => setFeedback(e.target.value)}
                sx={{ mb: 2 }}
              />
              
              <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center' }}>
                <Button 
                  variant="contained" 
                  color="primary"
                  onClick={handleSubmitFeedback}
                  disabled={!feedback}
                >
                  Submit Feedback
                </Button>
                
                <Button 
                  variant="contained" 
                  color="success"
                  onClick={handleAcceptSuggestions}
                >
                  Accept Suggestions
                </Button>
              </Box>
            </Box>
          </Box>
        )}
      </Box>
    </Container>
  );
}

export default App; 
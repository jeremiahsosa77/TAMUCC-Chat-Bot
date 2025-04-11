import React, { useState, useEffect, useRef } from 'react';
import { 
  Box, 
  Container, 
  Paper, 
  Typography, 
  TextField, 
  Button, 
  IconButton,
  CircularProgress,
  ThemeProvider,
  createTheme
} from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import axios from 'axios';

const theme = createTheme({
  palette: {
    primary: {
      main: '#500000', // TAMU-CC maroon
    },
    secondary: {
      main: '#003C71', // TAMU-CC blue
    },
  },
});

function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async () => {
    if (!input.trim()) return;

    const userMessage = {
      text: input,
      isUser: true,
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await axios.post('http://localhost:8000/api/message', {
        text: input,
        user_id: 1 // In a real app, this would be the actual user ID
      });

      const botMessage = {
        text: response.data.response.text,
        isUser: false,
        timestamp: new Date().toISOString()
      };

      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage = {
        text: "Sorry, I'm having trouble processing your request. Please try again later.",
        isUser: false,
        timestamp: new Date().toISOString()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <ThemeProvider theme={theme}>
      <Container maxWidth="md" sx={{ height: '100vh', display: 'flex', flexDirection: 'column', py: 2 }}>
        <Typography variant="h4" component="h1" gutterBottom align="center" color="primary">
          TAMU-CC Chatbot
        </Typography>
        
        <Paper 
          elevation={3} 
          sx={{ 
            flex: 1, 
            display: 'flex', 
            flexDirection: 'column',
            overflow: 'hidden',
            mb: 2
          }}
        >
          <Box sx={{ flex: 1, overflow: 'auto', p: 2 }}>
            {messages.map((message, index) => (
              <Box
                key={index}
                sx={{
                  display: 'flex',
                  justifyContent: message.isUser ? 'flex-end' : 'flex-start',
                  mb: 2
                }}
              >
                <Paper
                  sx={{
                    p: 2,
                    maxWidth: '70%',
                    backgroundColor: message.isUser ? 'primary.main' : 'secondary.main',
                    color: 'white'
                  }}
                >
                  <Typography variant="body1">{message.text}</Typography>
                  <Typography variant="caption" sx={{ display: 'block', mt: 1, opacity: 0.7 }}>
                    {new Date(message.timestamp).toLocaleTimeString()}
                  </Typography>
                </Paper>
              </Box>
            ))}
            {loading && (
              <Box sx={{ display: 'flex', justifyContent: 'flex-start', mb: 2 }}>
                <CircularProgress size={20} />
              </Box>
            )}
            <div ref={messagesEndRef} />
          </Box>
          
          <Box sx={{ p: 2, borderTop: 1, borderColor: 'divider' }}>
            <Box sx={{ display: 'flex', gap: 1 }}>
              <TextField
                fullWidth
                variant="outlined"
                placeholder="Type your message..."
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={handleKeyPress}
                disabled={loading}
                multiline
                maxRows={4}
              />
              <IconButton 
                color="primary" 
                onClick={handleSendMessage}
                disabled={loading || !input.trim()}
              >
                <SendIcon />
              </IconButton>
            </Box>
          </Box>
        </Paper>
      </Container>
    </ThemeProvider>
  );
}

export default App; 
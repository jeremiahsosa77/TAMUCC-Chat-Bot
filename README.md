# TAMU-CC AI Chatbot

A comprehensive AI chatbot designed specifically for Texas A&M University - Corpus Christi students, faculty, and visitors. This virtual assistant provides accurate information about campus resources, events, academic information, and student services while maintaining contextual awareness in conversations.

## Features

- Natural language understanding of university-specific queries
- Context-aware conversations
- Comprehensive knowledge base of TAMU-CC information
- Secure user authentication and data management
- Responsive web interface
- Feedback and improvement mechanisms

## Technical Stack

- Backend: Python with FastAPI
- Database: PostgreSQL
- NLP: Hugging Face Transformers
- Frontend: JavaScript/React
- Containerization: Docker

## Project Structure

```
tamu-cc-chatbot/
├── backend/              # FastAPI backend
│   ├── api/             # API endpoints
│   ├── core/            # Core functionality
│   ├── models/          # Database models
│   └── services/        # Business logic
├── frontend/            # React frontend
├── nlp/                 # NLP components
├── docker/              # Docker configuration
└── tests/               # Test suite
```

## Setup and Installation

1. Clone the repository
2. Create a virtual environment: `python -m venv venv`
3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Unix/MacOS: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Set up environment variables in `.env`
6. Initialize the database
7. Start the development server: `uvicorn backend.main:app --reload`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

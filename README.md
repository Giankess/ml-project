# NDA Validator AI Assistant

An AI-powered NDA validation system that helps users analyze and improve their Non-Disclosure Agreements.

## Features

- Upload and analyze NDA documents
- AI-powered clause analysis and suggestions
- Redline version generation
- Feedback integration
- Clean document generation
- Learning from user feedback

## Project Structure

```
nda-validator/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── models/
│   │   └── services/
│   ├── tests/
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   └── services/
│   └── Dockerfile
├── docker-compose.yml
└── README.md
```

## Setup

1. Clone the repository
2. Install Docker and Docker Compose
3. Run `docker-compose up --build`

## Development

### Backend
- FastAPI
- Python 3.9+
- LangChain
- python-docx

### Frontend
- React
- Material-UI
- Axios

## License

MIT 
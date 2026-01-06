# RecoverAI-Coach

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A personalized AI-powered chatbot that provides recovery advice by analyzing Whoop data, leveraging NVIDIA NeMo and LlamaIndex technologies.

## Features

- Real-time Whoop data integration
- Personalized recovery recommendations
- Multi-domain advice (nutrition, strength training, mindset)
- Interactive chat interface
- Data visualization dashboard
- Support for multiple LLM providers (OpenAI, Anthropic, Google, Groq, NVIDIA, Ollama)

## Prerequisites

- Python 3.8+
- Node.js 16+
- npm 8+
- MongoDB Atlas account
- Whoop account with API access
- API keys for at least one LLM provider

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/phizzog/RecoverAI-Coach.git
cd RecoverAI-Coach
```

### 2. Backend Setup

Create and activate a virtual environment:

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

Install Python dependencies:

```bash
pip install -r requirements.txt
```

### 3. Frontend Setup

In the root directory:

```bash
npm install
```

### 4. Environment Configuration

Copy the example environment file and configure your credentials:

```bash
cp backend/.env.example backend/.env
```

Edit `backend/.env` with your:
- Whoop credentials
- LLM API keys (at least one required)
- MongoDB Atlas connection URIs
- Other configuration options

See the `.env.example` file for detailed descriptions of each variable.

### 5. Database Setup

You'll need three MongoDB Atlas collections for the vector embeddings:
- Nutrition database
- Strength training database
- Mindset database

Configure the connection URIs in your `.env` file.

## Running the Application

### 1. Start the Embedding Services (Optional)

If using local vector search, start the embedding services:

```bash
# Terminal 1
cd "NeMo Retriever"
python nutrition_embed.py  # Port 5001

# Terminal 2
python strength_embed.py   # Port 5002

# Terminal 3
python mindset_embed.py    # Port 5003
```

### 2. Start the Backend Server

From the backend directory:

```bash
python app.py
```

The Flask server will start on port 5050.

### 3. Start the Frontend Development Server

From the root directory:

```bash
npm start
```

The application will be available at http://localhost:3000

## Configuration

### Environment Variables

Key environment variables (see `.env.example` for full list):

| Variable | Description |
|----------|-------------|
| `WHOOP_USERNAME` | Your Whoop account username |
| `WHOOP_PASSWORD` | Your Whoop account password |
| `OPENAI_API_KEY` | OpenAI API key |
| `ANTHROPIC_API_KEY` | Anthropic API key |
| `MONGODB_ATLAS_URI_*` | MongoDB connection strings |
| `FLASK_DEBUG` | Enable debug mode (true/false) |
| `CORS_ORIGINS` | Allowed CORS origins |

### Frontend Configuration

The frontend API URL can be configured via environment variable:

```bash
REACT_APP_API_URL=http://localhost:5050 npm start
```

## Project Structure

```
RecoverAI-Coach/
├── backend/
│   ├── app.py              # Flask application
│   ├── llm_backend.py      # LLM integration
│   ├── whoop_processor.py  # Whoop data processing
│   └── requirements.txt    # Python dependencies
├── src/
│   ├── components/         # React components
│   ├── services/           # API services
│   └── App.js              # Main React app
├── NeMo Retriever/
│   ├── nutrition_embed.py  # Nutrition vector service
│   ├── strength_embed.py   # Strength vector service
│   └── mindset_embed.py    # Mindset vector service
└── package.json            # Node.js dependencies
```

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## Security

For security concerns, please see [SECURITY.md](SECURITY.md).

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

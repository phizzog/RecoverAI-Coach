# Sports Recovery Chatbot

A personalized AI-powered chatbot that provides recovery advice by analyzing Whoop data, leveraging NVIDIA NeMo and LlamaIndex technologies.

## Features

- Real-time Whoop data integration
- Personalized recovery recommendations
- Multi-domain advice (nutrition, strength training, mindset)
- Interactive chat interface
- Data visualization dashboard

## Prerequisites

- Python 3.8+
- Node.js 16+
- npm 8+
- MongoDB
- NVIDIA GPU (recommended)

## Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd sports-recovery-chatbot
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

**Required Python packages:**
- flask
- flask-cors
- python-dotenv
- pandas
- whoop
- langchain
- langchain-community
- langchain-core
- langchain-openai
- langchain-anthropic
- langchain-google-genai
- langchain-groq
- pydantic
- requests

### 3. Frontend Setup

In the root directory:

```bash
npm install
```

This will install the required React dependencies defined in package.json.

### 4. Environment Configuration

Create a `.env` file in the backend directory with the following variables:

```env
# LLM API Keys
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
GOOGLE_API_KEY=your_google_api_key
GROQ_API_KEY=your_groq_api_key

# Whoop Authentication
WHOOP_USERNAME=your_whoop_username
WHOOP_PASSWORD=your_whoop_password

# Database URLs
NUTRITION_DB_URL=your_nutrition_db_url
STRENGTH_DB_URL=your_strength_db_url
MINDSET_DB_URL=your_mindset_db_url
```

### 5. Database Setup

Ensure your MongoDB instances are running for:
- Nutrition database (port 5001)
- Strength training database (port 5002)
- Mindset database (port 5003)

## Running the Application

### 1. Start the Backend Server

From the backend directory:

```bash
# Terminal 1
python app.py
```

The Flask server will start on port 5050.

### 2. Start the Frontend Development Server

From the root directory:

```bash
# Terminal 2
npm start
```

The application should now be running at http://localhost:3000
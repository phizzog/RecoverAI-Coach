# Contributing to RecoverAI-Coach

Thank you for your interest in contributing to RecoverAI-Coach! This document provides guidelines and instructions for contributing.

## Getting Started

### Prerequisites

- Python 3.8+
- Node.js 16+
- npm 8+
- MongoDB Atlas account (or local MongoDB instance)
- API keys for LLM providers (OpenAI, Anthropic, Google, Groq, or NVIDIA)

### Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/RecoverAI-Coach.git
   cd RecoverAI-Coach
   ```

2. **Set up the backend**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and database URLs
   ```

4. **Set up the frontend**
   ```bash
   cd ..
   npm install
   ```

5. **Run the application**
   ```bash
   # Terminal 1: Backend
   cd backend && python app.py

   # Terminal 2: Frontend
   npm start
   ```

## How to Contribute

### Reporting Bugs

- Check existing issues to avoid duplicates
- Use the bug report template if available
- Include steps to reproduce, expected behavior, and actual behavior
- Include your environment details (OS, Python version, Node version)

### Suggesting Features

- Open an issue describing the feature
- Explain the use case and benefits
- Be open to discussion and feedback

### Pull Requests

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Make your changes
4. Test your changes locally
5. Commit with clear, descriptive messages
6. Push to your fork
7. Open a pull request against `main`

### Code Style

**Python:**
- Follow PEP 8 guidelines
- Use meaningful variable and function names
- Add docstrings to functions and classes

**JavaScript/React:**
- Use ES6+ syntax
- Follow React best practices
- Use meaningful component and variable names

### Commit Messages

- Use present tense ("Add feature" not "Added feature")
- Use imperative mood ("Move cursor to..." not "Moves cursor to...")
- Keep the first line under 72 characters
- Reference issues when applicable

## Questions?

Feel free to open an issue for any questions about contributing.

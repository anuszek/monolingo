# Monolingo - AI Language Tutor Setup Guide

This app is an AI-powered English language tutor for Polish speakers, built with React (frontend) and Flask (backend).

## Project Structure

```
monolingo/
├── src/                  # React frontend (TypeScript + Vite + MUI)
├── mati/                 # Flask backend (Python)
└── ...
```

## Prerequisites

- **Node.js** (v18 or higher) - for frontend
- **Python** (3.8 or higher) - for backend
- **OpenAI API Key** - get one from https://platform.openai.com/
- **Tesseract OCR** (for image OCR features) - install from https://github.com/tesseract-ocr/tesseract and make sure the tesseract executable is on your PATH

## Setup Instructions

### 1. Backend Setup (Flask)

```powershell
# Navigate to the backend folder
cd mati

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
.\venv\Scripts\Activate.ps1

# Install dependencies (requirements file is in the mati/ folder)
pip install -r requirements.txt

# Create a .env file with your OpenAI API key. In PowerShell you can run:
# Set-Content -Path .env -Value 'OPENAI_API_KEY=your_api_key_here'
# Or copy the example and edit it manually:
# copy .env.example .env

# Run the Flask server
python app.py
```

The backend will start on `http://localhost:5000`

### 2. Frontend Setup (React)

```powershell
# Navigate back to the root folder
cd ..

# Install dependencies
npm install

# Create .env file (optional - for custom API URL)
# copy .env.example .env and edit VITE_API_URL if needed

# Run the development server
npm run dev
```

The frontend will start on `http://localhost:5173`

### 3. Access the App

Open your browser and go to: `http://localhost:5173`

You should see the Monolingo interface. Type a message and the AI will respond!

## Available Scripts

### Frontend

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

### Backend

- `python app.py` - Start Flask server (from mati/ folder)

## Environment Variables

### Frontend (.env)

```
VITE_API_URL=http://localhost:5000
```

### Backend (mati/.env)

```
OPENAI_API_KEY=your_openai_api_key_here
```

## Features

- ✅ Real-time chat with AI tutor
- ✅ English learning assistance with Polish explanations
- ✅ Conversation history
- ✅ Modern Material-UI design
- ✅ Responsive layout

## Troubleshooting

### Backend not connecting?

- Make sure Flask server is running on port 5000
- Check if OPENAI_API_KEY is set in `mati/.env`
- Verify CORS is enabled in Flask

### Frontend errors?

- Run `npm install` to ensure all dependencies are installed
- Clear browser cache and reload
- Check browser console for errors

## Optional: Voice & OCR features

Voice and OCR functionality are now integrated into the main Flask backend in `mati/`.

- OCR (image -> text) requires Tesseract (see prerequisites above).
- Server-side TTS (agent -> speech) and OCR endpoints are available under `mati/app.py`.

If you still have an `XD/` folder from earlier experiments it is deprecated — the same capabilities were merged into `mati/` and you do not need to run `XD` separately.

## Technologies Used

- **Frontend**: React 19, TypeScript, Vite, Material-UI
- **Backend**: Flask, Python, OpenAI API
- **Styling**: CSS, Material-UI components

# Monolingo - Quick Start

## Running the Application

### Terminal 1 - Backend (Flask)

```powershell
cd mati
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

### Terminal 2 - Frontend (React)

```powershell
npm install
npm run dev
```

Then open http://localhost:5173

The backend runs on port 5000, frontend on port 5173.
Make sure your OpenAI API key is set in `mati/.env`

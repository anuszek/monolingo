# Start both frontend and backend servers

Write-Host "Starting Monolingo..." -ForegroundColor Green

# Check if backend .env exists
if (!(Test-Path "mati\.env")) {
  Write-Host "Error: mati\.env not found!" -ForegroundColor Red
  Write-Host "Please create mati\.env with your OPENAI_API_KEY" -ForegroundColor Yellow
  Write-Host "Example: OPENAI_API_KEY=sk-..." -ForegroundColor Yellow
  exit 1
}

# Start backend in a new window
Write-Host "Starting Flask backend..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd mati; if (!(Test-Path 'venv')) { python -m venv venv }; .\venv\Scripts\Activate.ps1; pip install -r requirements.txt -q; python app.py"

# Wait a bit for backend to start
Start-Sleep -Seconds 3

# Start frontend
Write-Host "Starting React frontend..." -ForegroundColor Cyan
npm install
npm run dev

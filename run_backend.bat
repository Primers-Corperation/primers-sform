@echo off
echo.
echo =============================================
echo   SOVEREIGN INTELLIGENCE PLATFORM
echo   Local Development Mode
echo =============================================
echo.

cd backend
pip install -r requirements.txt --quiet

echo [OK] Dependencies verified
echo [STARTING] Backend on http://localhost:8000
echo.

python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

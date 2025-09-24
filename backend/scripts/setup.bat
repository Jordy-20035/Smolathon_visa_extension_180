@echo off
echo 🚀 Setting up ЦОДД backend...

REM Load environment variables from .env file
if exist .env (
    for /f "usebackq tokens=1,2 delims==" %%A in (".env") do (
        set %%A=%%B
    )
)

echo 📦 Running database migrations...
alembic upgrade head

echo 📊 Seeding initial data...
python scripts\init_db.py

echo ✅ Setup completed!
echo 🌐 Backend will be available at: http://localhost:8000
echo 📚 API documentation: http://localhost:8000/docs
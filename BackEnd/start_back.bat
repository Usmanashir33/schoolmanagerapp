@echo off
title School Manager - All Services

echo ===============================
echo Starting School Manager Services
echo ===============================

REM Optional: activate virtual environment
call SchoolEnv\Scripts\activate

REM Reduce TensorFlow noise (optional)
set TF_ENABLE_ONEDNN_OPTS=0

echo.
echo [1/4] Starting Redis...
start "Redis" cmd /k "redis-server"

echo.
echo [2/4] Starting Django Server...
start "Django" cmd /k "python manage.py runserver 8001"

echo.
echo [3/4] Starting Celery Worker (AI optimized)...
start "Celery Worker" cmd /k "celery -A SchoolManagerProj worker --loglevel=info --concurrency=1"

echo.
echo [4/4] Starting Celery Beat (scheduler)...
start "Celery Beat" cmd /k "celery -A SchoolManagerProj beat --loglevel=info"

echo.
echo ===============================
echo All services started successfully
echo ===============================
pause
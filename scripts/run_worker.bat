@echo off
:: Sovereign Node - Daily Worker Execution Script
:: This script ensures the command prompt is running in the correct directory before executing python.

echo [Sovereign Node] Initializing Predator Worker...
cd /d "C:\Users\GranT\OneDrive\Masaüstü\tradepanel"

:: Run the python script
python run_worker.py

echo [Sovereign Node] Worker execution finished.

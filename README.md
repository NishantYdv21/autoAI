# AutoAI Prototype 🚗

A prototype app for automotive predictive maintenance, featuring:
- Admin dashboard for fleet monitoring and maintenance tracking
- User portal for vehicle status, maintenance scheduling and chatbot support

## Quick Start (Windows PowerShell)

1. Setup a Python virtual environment and install dependencies:
```powershell
python -m venv env
.\env\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Run the Flask app:
```powershell
$env:FLASK_APP = "app.py"
$env:FLASK_ENV = "development"  # enables debug mode
flask run
```

3. Open http://localhost:5000 in your browser

## Test Accounts

Admin:
- Username: admin
- Password: admin123

User:
- Register new user OR
- Use a registered vehicle number from `users.json`

## Features

Admin Dashboard:
- Active vehicle monitoring
- Vehicle health tracking
- Fleet uptime metrics
- Risk prediction visualization
- Service scheduling overview

User Portal:
- Vehicle maintenance status
- Chatbot support for common issues
- Service scheduling
- Delivery tracking

## Development

Running tests:
```powershell
pytest tests/
```

## Project Structure

```
├── app.py              # Flask application
├── users.json          # User/vehicle database (demo)
├── requirements.txt    # Python dependencies
├── static/            # Static assets (JS/CSS)
├── templates/         # HTML templates
└── tests/            # Test files
```

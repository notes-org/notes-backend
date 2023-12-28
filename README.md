## Local development

### Prerequisites
- Python 3.10+
- PostgreSQL 14+

### Set up your environment
Navigate to the project directory:
```bash
cd notes/
```

Create and activate a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```

Install the requirements:
```bash
pip install -r requirements_dev.txt
```

Create a file named `.env` and define the following environment variables:
```env
POSTGRES_SERVER = localhost
POSTGRES_USER = YOUR_POSTGRES_USER
POSTGRES_PASSWORD = YOUR_POSTGRES_USER_PASSWORD
POSTGRES_DB = YOUR_POSTGRES_DB_NAME

BACKEND_CORS_ORIGINS = ["*"]
```

Apply the database migrations:
```bash
alembic upgrade head
```

Run the Uvicorn server:
```bash
uvicorn app.main:app --reload
```
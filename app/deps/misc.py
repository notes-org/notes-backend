from app.db.session import SessionLocal

def get_db() -> SessionLocal:
    """Get the database session then close it after the request is complete."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
import os
import random
import string
from datetime import datetime, timezone
from typing import Optional

from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, HttpUrl
from sqlalchemy import create_engine, Column, String, Integer, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker, Session

# Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/shortener.db")
SHORT_URL_LENGTH = int(os.getenv("SHORT_URL_LENGTH", 6))

# Initialize FastAPI app
app = FastAPI(title="URL Shortener API")

# Add CORS middleware for cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database setup
engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}  # Needed for SQLite
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class URL(Base):
    """
    SQLAlchemy model for storing URLs.
    """
    __tablename__ = "urls"

    id = Column(Integer, primary_key=True, index=True)
    original_url = Column(String, index=True)
    short_code = Column(String, unique=True, index=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    visits_count = Column(Integer, default=0)
    creator_ip = Column(String)
    creator_agent = Column(String)


# Create the database tables
Base.metadata.create_all(bind=engine)

# Pydantic models for request and response
class URLInput(BaseModel):
    url: HttpUrl


class URLOutput(BaseModel):
    short_url: str
    original_url: str
    visits_count: Optional[int] = 0

# Dependency to get a database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def generate_short_code(db: Session) -> str:
    """
    Generates a unique short code for URL shortening.
    """
    characters = string.ascii_letters + string.digits
    while True:
        code = ''.join(random.choices(characters, k=SHORT_URL_LENGTH))
        if not db.query(URL).filter(URL.short_code == code).first():
            return code


@app.post("/shorten", response_model=URLOutput)
async def create_short_url(url_input: URLInput, request: Request, db: Session = Depends(get_db)):
    """
    Endpoint to shorten a given URL.
    """
    # Check if the URL already exists in the database
    existing_url = db.query(URL).filter(URL.original_url == str(url_input.url)).first()
    if existing_url:
        return URLOutput(
            short_url=f"{request.base_url}{existing_url.short_code}",
            original_url=existing_url.original_url,
            visits_count=existing_url.visits_count
        )

    # Generate a unique short code
    short_code = generate_short_code(db)

    # Create a new URL record
    new_url = URL(
        original_url=str(url_input.url),
        short_code=short_code,
        creator_ip=request.client.host,
        creator_agent=request.headers.get("user-agent", "")
    )
    db.add(new_url)
    db.commit()
    db.refresh(new_url)

    return URLOutput(
        short_url=f"{request.base_url}{new_url.short_code}",
        original_url=new_url.original_url,
        visits_count=new_url.visits_count
    )


@app.get("/{short_code}")
async def redirect_to_url(short_code: str, db: Session = Depends(get_db)):
    """
    Redirect to the original URL using the short code.
    """
    url_record = db.query(URL).filter(URL.short_code == short_code).first()
    if not url_record:
        raise HTTPException(status_code=404, detail="URL not found")

    # Increment visit count
    url_record.visits_count += 1
    db.commit()

    return RedirectResponse(url=url_record.original_url)


@app.get("/stats/{short_code}", response_model=URLOutput)
async def get_url_stats(short_code: str, request: Request, db: Session = Depends(get_db)):
    """
    Get statistics for a shortened URL.
    """
    url_record = db.query(URL).filter(URL.short_code == short_code).first()
    if not url_record:
        raise HTTPException(status_code=404, detail="URL not found")

    return URLOutput(
        short_url=f"{request.base_url}{url_record.short_code}",
        original_url=url_record.original_url,
        visits_count=url_record.visits_count
    )

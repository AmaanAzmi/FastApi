import os
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from dotenv import load_dotenv
from google import genai
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

# Import database stuff
from database import SessionLocal, EmailReply, init_db

# Load environment variables
load_dotenv()

# Initialize FastAPI
app = FastAPI(title="AI Email Responder API")

# Initialize database on startup
@app.on_event("startup")
def startup_event():
    init_db()

# Configure Gemini client
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise RuntimeError("GEMINI_API_KEY not set in .env file")

client = genai.Client(api_key=api_key)

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Request/Response models
class EmailRequest(BaseModel):
    email_text: str
    tone: str = "formal"

class EmailResponse(BaseModel):
    id: int
    received_email: str
    tone: str
    reply: str
    created_at: datetime

@app.get("/")
def read_root():
    return {
        "message": "AI Email Responder API",
        "version": "2.0",
        "endpoints": ["/generate-reply", "/history", "/history/{id}"]
    }

@app.post("/generate-reply", response_model=EmailResponse)
def generate_reply_api(request: EmailRequest, db: Session = Depends(get_db)):
    """
    Generate an AI-powered email reply and store it in the database.
    
    - **email_text**: The email you want to reply to
    - **tone**: Either 'formal' or 'casual'
    """
    try:
        # Validate tone
        if request.tone not in ("formal", "casual"):
            raise HTTPException(status_code=400, detail="Tone must be 'formal' or 'casual'")
        
        # Build the prompt
        prompt = f"""
You are a polite, professional email assistant.

Write the reply in a {request.tone} tone. Follow these rules:
- Start with a short greeting.
- Answer the user's questions clearly.
- If something is unclear, ask 1-2 clarifying questions.
- End with a friendly sign-off.
- Keep the reply under 8 sentences.

EMAIL:
{request.email_text}
"""
        
        # Call Gemini API
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        
        # Save to database
        db_reply = EmailReply(
            email_text=request.email_text,
            tone=request.tone,
            reply_text=response.text
        )
        db.add(db_reply)
        db.commit()
        db.refresh(db_reply)
        
        # Return the response
        return EmailResponse(
            id=db_reply.id,
            received_email=db_reply.email_text,
            tone=db_reply.tone,
            reply=db_reply.reply_text,
            created_at=db_reply.created_at
        )
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error generating reply: {str(e)}")

@app.get("/history", response_model=List[EmailResponse])
def get_history(limit: int = 10, db: Session = Depends(get_db)):
    """
    Get the last N email replies from the database.
    
    - **limit**: Number of replies to return (default: 10)
    """
    replies = db.query(EmailReply).order_by(EmailReply.created_at.desc()).limit(limit).all()
    
    return [
        EmailResponse(
            id=reply.id,
            received_email=reply.email_text,
            tone=reply.tone,
            reply=reply.reply_text,
            created_at=reply.created_at
        )
        for reply in replies
    ]

@app.get("/history/{reply_id}", response_model=EmailResponse)
def get_reply_by_id(reply_id: int, db: Session = Depends(get_db)):
    """
    Get a specific email reply by ID.
    
    - **reply_id**: The ID of the reply to retrieve
    """
    reply = db.query(EmailReply).filter(EmailReply.id == reply_id).first()
    
    if not reply:
        raise HTTPException(status_code=404, detail="Reply not found")
    
    return EmailResponse(
        id=reply.id,
        received_email=reply.email_text,
        tone=reply.tone,
        reply=reply.reply_text,
        created_at=reply.created_at
    )

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "gemini_api_configured": bool(api_key),
        "database": "connected"
    }

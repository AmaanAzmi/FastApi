import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from google import genai

# Load environment variables
load_dotenv()

# Initialize FastAPI
app = FastAPI(title="AI Email Responder API")

# Configure Gemini client
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise RuntimeError("GEMINI_API_KEY not set in .env file")

client = genai.Client(api_key=api_key)

# Request model
class EmailRequest(BaseModel):
    email_text: str
    tone: str = "formal"

# Response model
class EmailResponse(BaseModel):
    received_email: str
    tone: str
    reply: str

@app.get("/")
def read_root():
    return {
        "message": "AI Email Responder API",
        "version": "1.0",
        "endpoints": ["/generate-reply"]
    }

@app.post("/generate-reply", response_model=EmailResponse)
def generate_reply_api(request: EmailRequest):
    """
    Generate an AI-powered email reply.
    
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
        
        # Return the response
        return EmailResponse(
            received_email=request.email_text,
            tone=request.tone,
            reply=response.text
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating reply: {str(e)}")

@app.get("/health")
def health_check():
    return {"status": "healthy", "gemini_api_configured": bool(api_key)}


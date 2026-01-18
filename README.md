# AI Email Responder API

A production-ready FastAPI backend that generates professional email replies using Google's Gemini AI.


## 🚀 Live Demo

**API URL**: https://fastapi-production-bb02.up.railway.app

**Interactive Docs**: https://fastapi-production-bb02.up.railway.app/docs

## 📋 Features

- Generate professional email replies using AI (Gemini 2.5 Flash)
- Choose tone: formal or casual
- RESTful API with automatic OpenAPI documentation
- Deployed on Railway with environment-based configuration
- Error handling and input validation

## 🛠️ Tech Stack

- **Framework**: FastAPI
- **AI**: Google Gemini API
- **Deployment**: Railway
- **Language**: Python 3.x

## 📡 API Endpoints

### `POST /generate-reply`

Generate an AI-powered email reply.

**Request Body:**
```json
{
  "email_text": "Your email content here",
  "tone": "formal"  // or "casual"
}

**Expected Response:**

json
{
  "received_email": "Your email content here",
  "tone": "formal",
  "reply": "AI-generated professional reply..."
}

How to Run Locally

1.Clone the repository

git clone https://github.com/AmaanAzmi/FastApi.git
cd FastApi

2.install dependencies

pip install -r requirements.txt

3. create .env file (google Gemini Api Kep)

GEMINI_API_KEY=your_api_key_here

4. Run the server

uvicorn api:app --reload

5. Open docs

http://127.0.0.1:8000/docs


from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
from app.services.document_service import DocumentService
from app.services.ai_service import AIService
from app.core.config import settings

app = FastAPI(title="NDA Validator API")

# Simple CORS configuration for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

document_service = DocumentService()
ai_service = AIService()

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """Upload an NDA document for analysis"""
    if not file.filename.endswith('.docx'):
        raise HTTPException(status_code=400, detail="Only .docx files are supported")
    
    return await document_service.process_upload(file)

@app.post("/analyze/{document_id}")
async def analyze_document(document_id: str):
    """Analyze the uploaded NDA document"""
    return await ai_service.analyze_document(document_id)

@app.post("/feedback/{document_id}")
async def submit_feedback(document_id: str, feedback: str):
    """Submit feedback for the analyzed document"""
    return await ai_service.process_feedback(document_id, feedback)

@app.get("/download/{document_id}")
async def download_document(document_id: str, clean: bool = False):
    """Download the processed document (redline or clean version)"""
    return await document_service.get_document(document_id, clean)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 
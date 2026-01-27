import asyncio
from concurrent.futures import ThreadPoolExecutor
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel
from weasyprint import HTML, CSS
from io import BytesIO
from api import pdf, email

app = FastAPI(title="PDF Generator API")
executor = ThreadPoolExecutor(max_workers=4)

# CORS for access of the client application
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:4173", "http://localhost:5174"],
    allow_methods=["POST"],
    allow_headers=["Content-Type"],
)

app.include_router(pdf.router)
app.include_router(email.router)

@app.get("/health")
async def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    """ To listen to clients the application needs uvicorn """
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)

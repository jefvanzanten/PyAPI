import asyncio
from concurrent.futures import ThreadPoolExecutor
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel
from weasyprint import HTML, CSS
from io import BytesIO

app = FastAPI(title="PDF Generator API")
executor = ThreadPoolExecutor(max_workers=4)

# CORS for access of the client application
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:4173", "http://localhost:5174"],
    allow_methods=["POST"],
    allow_headers=["Content-Type"],
)

class PDFRequest(BaseModel):
    html_content: str
    css: str | None = None
    filename: str = "document.pdf"


def _generate_pdf_sync(html_content: str, css: str | None) -> bytes:
    """
    Generate a PDF from HTML content with conditional CSS.

    - **html_content**: The content to convert to PDF
    - **css**: Optional CSS styling
    - **filename**: Name of the PDF file (default: document.pdf)
    """
    html = HTML(string=html_content)

    stylesheets = []
    if css:
        stylesheets.append(CSS(string=css))

    pdf_buffer = BytesIO()
    html.write_pdf(pdf_buffer, stylesheets=stylesheets)
    return pdf_buffer.getvalue()


@app.post("/pdf")
async def generate_pdf(request: PDFRequest) -> Response:
    """
    An asynchroneous function that runs the _generate_pdf_sync in a thread pool 
    so multiple users can use this html to pdf endpoint without waiting
    """
    try:
        loop = asyncio.get_event_loop()
        pdf_bytes = await loop.run_in_executor(
            executor,
            _generate_pdf_sync,
            request.html_content,
            request.css
        )

        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="{request.filename}"'
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")

@app.get("/health")
async def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    """ To listen to clients the application needs uvicorn """
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)

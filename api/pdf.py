from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
from weasyprint import HTML, CSS
from io import BytesIO
import asyncio
from concurrent.futures import ThreadPoolExecutor

router = APIRouter(prefix="/pdf", tags=["pdf"])
executor = ThreadPoolExecutor(max_workers=4)

class PDFRequest(BaseModel):
    html_content: str
    css: str | None = None
    filename: str = "document.pdf"

def _generate_pdf_sync(html_content: str, css: str | None) -> bytes:
    html = HTML(string=html_content)
    stylesheets = []
    if css:
        stylesheets.append(CSS(string=css))
    pdf_buffer = BytesIO()
    html.write_pdf(pdf_buffer, stylesheets=stylesheets)
    return pdf_buffer.getvalue()

@router.post("generate-pdf")
async def generate_pdf(request: PDFRequest) -> Response:
    try:
        loop = asyncio.get_event_loop()
        pdf_bytes = await loop.run_in_executor(
            executor, _generate_pdf_sync, request.html_content, request.css
        )
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{request.filename}"'}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")
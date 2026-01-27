from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
import resend
import os
from dotenv import load_dotenv

load_dotenv()

resend.api_key = os.getenv("RESEND_API_KEY")

class ContactForm(BaseModel):
    name: str
    email: EmailStr
    message: str

router = APIRouter(prefix="/email", tags=["email"])

@router.post("/send-email")
async def send_contact_email(form: ContactForm):
    try:
        resend.Emails.send({
            "from": "noreply@jefvanzanten.dev",
            "to": "j.van.zanten@gmail.com",
            "subject": f"Nieuw bericht van {form.name}",
            "html": f"<p><strong>Van:</strong> {form.name} ({form.email})</p><p>{form.message}</p>"
        })
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
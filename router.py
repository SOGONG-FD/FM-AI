from fastapi import APIRouter, Depends, HTTPException
import os
import google.generativeai as genai
from sqlalchemy.orm import Session

from database import SessionLocal
from models import Conversation

router = APIRouter()

# Google Gemini 설정
genai.configure(api_key=os.getenv("GEMINI_KEY"))
model = genai.GenerativeModel("gemini-2.0-flash")

# 데이터베이스 세션 가져오기
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
# 사용자의 질문을 받아 Gemini 응답 저장
@router.post("/chat/{user_id}")
async def chat(user_id: str, message: str, db: Session = Depends(get_db)):
    # Gemini API 호출
    response = model.generate_content(message)
    bot_reply = response.text

    # 대화 내용 저장
    new_conversation = Conversation(
        user_id=user_id,
        user_message=message,
        bot_response=bot_reply
    )
    db.add(new_conversation)
    db.commit()
    db.refresh(new_conversation)

    return {"user_message": message, "bot_response": bot_reply}


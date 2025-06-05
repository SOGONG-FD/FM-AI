from fastapi import APIRouter, Depends, HTTPException
import os
import google.generativeai as genai
from sqlalchemy.orm import Session
from dotenv import load_dotenv
from typing import List
from datetime import datetime

from database import SessionLocal
from models import Conversation

router = APIRouter()

# .env 파일에서 환경 변수 로드
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_KEY"))
model = genai.GenerativeModel("gemini-2.0-flash")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("AI/chat/{user_id}")
async def chat(user_id: str, message: str, db: Session = Depends(get_db)):
    try:
        # 증상 분석 및 식단 추천을 위한 프롬프트 구성
        prompt = f"""
당신은 친근하고 전문적인 의학 상담사입니다. 사용자의 증상을 듣고, 간단하게 설명해주며, 
도움이 될 수 있는 식단을 추천해주세요. 

다음과 같은 순서로 답변해주세요:

1. 먼저 사용자의 증상을 정리하고, 추가로 알아야 할 증상이 있다면 물어보세요.
2. 가능한 원인을 1-2가지 정도 간단히 설명해주세요.
3. 증상 완화에 도움이 될 수 있는 음식 2-3가지를 추천해주세요.
4. 마지막으로 의사 상담이 필요한 경우를 간단히 언급해주세요.

답변은 친근하고 대화체로 해주세요. 전문 용어는 최대한 피하고, 쉽게 설명해주세요.
이 정보는 참고용이며, 정확한 진단을 위해서는 의사와 상담이 필요하다는 점을 자연스럽게 언급해주세요.

사용자의 증상: {message}
"""

        response = model.generate_content(prompt)
        bot_reply = response.text

        new_conversation = Conversation(
            user_id=user_id, user_message=message, bot_response=bot_reply
        )
        db.add(new_conversation)
        db.commit()
        db.refresh(new_conversation)

        return {"user_message": message, "bot_response": bot_reply}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


# 대화 히스토리 조회 API
@router.get("AI/history/{user_id}")
async def get_chat_history(
    user_id: str, skip: int = 0, limit: int = 10, db: Session = Depends(get_db)
):
    try:
        # 사용자의 대화 히스토리 조회
        conversations = (
            db.query(Conversation)
            .filter(Conversation.user_id == user_id)
            .order_by(Conversation.timestamp.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

        # 결과가 없는 경우
        if not conversations:
            return {"message": "대화 기록이 없습니다.", "history": []}

        # 응답 형식 구성
        history = [
            {
                "id": conv.id,
                "user_message": conv.user_message,
                "bot_response": conv.bot_response,
                "timestamp": conv.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            }
            for conv in conversations
        ]

        return {"message": "대화 기록을 성공적으로 조회했습니다.", "history": history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

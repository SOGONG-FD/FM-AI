from fastapi import APIRouter, Depends, HTTPException
import os
import google.generativeai as genai
from sqlalchemy.orm import Session
from dotenv import load_dotenv
from typing import List
from datetime import datetime
import re

from database import SessionLocal
from models import Conversation

router = APIRouter()

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_KEY"))
model = genai.GenerativeModel("gemini-2.0-flash")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def clean_markdown(text):
    # 마크다운 기호 제거
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)  # **굵은 글씨** 제거
    text = re.sub(r"\*(.*?)\*", r"\1", text)  # *기울임체* 제거
    text = re.sub(r"#+\s", "", text)  # # 제목 제거
    text = re.sub(r"`(.*?)`", r"\1", text)  # `코드` 제거
    text = re.sub(r"\[(.*?)\]\(.*?\)", r"\1", text)  # [링크](url) 제거
    text = re.sub(r"---", "", text)  # 구분선 제거
    text = re.sub(r"```.*?```", "", text, flags=re.DOTALL)  # 코드 블록 제거
    return text


@router.post("/ai/chat/{user_id}")
async def chat(user_id: str, message: str, db: Session = Depends(get_db)):
    try:
        prompt = f"""
당신은 친근하고 전문적인 의학 상담사야. 사용자의 증상을 듣고, 간단하게 설명해주며, 
도움이 될 수 있는 식단을 추천해줘야해. 

다음과 같은 순서로 답변해줘:

1. 먼저 사용자의 증상을 정리하고, 추가로 알아야 할 증상이 있다면 물어봐.
2. 가능한 원인을 1-2가지 정도 간단히 설명해.
3. 증상 완화에 도움이 될 수 있는 음식 2-3가지를 추천해.
4. 마지막으로 의사 상담이 필요한 경우를 간단히 언급해.

답변은 친근하고 대화체로 해주고. 전문 용어는 최대한 피하고, 쉽게 설명해라.
이 정보는 참고용이며, 정확한 진단을 위해서는 의사와 상담이 필요하다는 점을 자연스럽게 언급해줘.

사용자의 증상: {message}
"""

        response = model.generate_content(prompt)
        bot_reply = clean_markdown(response.text)  # 마크다운 제거

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


@router.get("/ai/history/{user_id}")
async def get_chat_history(
    user_id: str, skip: int = 0, limit: int = 10, db: Session = Depends(get_db)
):
    try:
        conversations = (
            db.query(Conversation)
            .filter(Conversation.user_id == user_id)
            .order_by(Conversation.timestamp.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

        if not conversations:
            return {"message": "대화 기록이 없습니다.", "history": []}

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

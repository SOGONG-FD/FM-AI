from fastapi import FastAPI
from router import router
import uvicorn
from database import engine
from models import Base

app = FastAPI()
app.include_router(router)

# 데이터베이스 테이블 생성
Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

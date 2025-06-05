from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

# .env 파일 로드
load_dotenv()

# 데이터베이스 URL 가져오기
DB_URL = os.getenv("DATABASE_URL")

# SQLAlchemy 엔진 생성 (연결 설정 추가)
engine = create_engine(
    DB_URL,
    pool_recycle=3600,  # 1시간마다 연결 재생성
    pool_pre_ping=True,  # 연결 확인 후 사용
    pool_size=5,  # 연결 풀 크기
    max_overflow=10,  # 추가 연결 허용
    echo=True,  # SQL 쿼리 로깅
)

# 세션 생성
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base 클래스 생성
Base = declarative_base()

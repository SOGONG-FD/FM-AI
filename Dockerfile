# Python 3.11.1 버전 사용
FROM python:3.13.0

# 작업 디렉토리 설정
WORKDIR /code

# requirements.txt 복사 및 의존성 설치
COPY requirements.txt /code/
RUN pip install --no-cache-dir -r requirements.txt

# 프로젝트 파일 복사
COPY . /code/

# 포트 설정
EXPOSE 80

# 서버 실행
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]

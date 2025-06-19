# Python 슬림 이미지 기반
FROM python:3.10-slim

# 작업 디렉토리 생성
WORKDIR /app

# Python 코드와 라이브러리 목록 복사
COPY /src/kafka-producer/producers/bike_exporter.py .
COPY requirements.txt .

# 의존성 설치
RUN pip install --no-cache-dir -r requirements.txt

# Prometheus 메트릭 노출 포트
EXPOSE 9310

# 실행 커맨드
CMD ["python", "bike_exporter.py"]
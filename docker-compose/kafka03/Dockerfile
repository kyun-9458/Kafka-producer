FROM python:3.10-slim
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY bike_exporter.py .

# 로그를 바로바로 표준출력으로 내보내게 함
ENV PYTHONUNBUFFERED=1

EXPOSE 9310
CMD ["python", "-u", "bike_exporter.py"]   #  -u 옵션: 완전 언버퍼드

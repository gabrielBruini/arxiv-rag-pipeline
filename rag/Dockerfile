FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

COPY shared /shared
COPY rag /rag
RUN pip install --no-cache-dir -e "/shared[infra]" -e "/rag[redis]"

EXPOSE 8000

CMD ["uvicorn", "rag.main:app", "--host", "0.0.0.0", "--port", "8000"]

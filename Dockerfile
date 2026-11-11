FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY agents agents
COPY backend backend
COPY rag rag
COPY security security
COPY knowledge_base knowledge_base
COPY frontend frontend
COPY .streamlit .streamlit

ENV PYTHONUNBUFFERED=1
ENV HOST=0.0.0.0
EXPOSE 8000
CMD ["python", "-m", "backend.main"]

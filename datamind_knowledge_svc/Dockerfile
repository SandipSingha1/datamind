FROM python:3.11-slim
WORKDIR /app
COPY ../requirements.txt .
RUN pip install --no-cache-dir fastapi uvicorn neo4j langchain-neo4j \
    langfuse snowflake-connector-python python-dotenv httpx pydantic
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8002"]

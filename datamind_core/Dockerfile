FROM python:3.11-slim
WORKDIR /app
COPY ../requirements.txt .
RUN pip install --no-cache-dir fastapi uvicorn langgraph langchain langchain-community \
    langfuse langsmith snowflake-connector-python python-dotenv httpx pydantic pydantic-settings
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]

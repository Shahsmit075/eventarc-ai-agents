FROM python:3.11-slim
WORKDIR /app

# Force ADK to use Vertex AI instead of Gemini API
ENV GOOGLE_GENAI_USE_VERTEXAI=1

COPY requirements.txt .
# Install uvicorn explicitly since we use it in CMD
RUN pip install uvicorn -r requirements.txt

COPY . .

CMD ["uvicorn", "agent:a2a_app", "--host", "0.0.0.0", "--port", "8080"]
FROM python:3.11-slim
WORKDIR /app

# Force ADK to use Vertex AI instead of Gemini API
ENV GOOGLE_GENAI_USE_VERTEXAI=1

COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy flat local files into a subdirectory so 'adk web' can discover it
COPY . agents/customer_chat/

CMD ["adk", "web", "--host", "0.0.0.0", "--port", "8080", "agents"]
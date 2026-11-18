FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ARG GIT_COMMIT=local
ENV GIT_COMMIT=${GIT_COMMIT}
# Retrain on the latest dataset while building the image
RUN python train.py
EXPOSE 8000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]

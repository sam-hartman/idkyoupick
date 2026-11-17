FROM python:3.12-slim
WORKDIR /app
COPY serve.py index.html ./
ENV HOST=0.0.0.0
EXPOSE 8080
CMD ["python3", "serve.py", "8080"]

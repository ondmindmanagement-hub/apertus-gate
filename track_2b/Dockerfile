FROM python:3.12-slim
WORKDIR /app
COPY track_2b/src/ /app/src/
EXPOSE 8787
ENV HOST=0.0.0.0
ENV PORT=8787
CMD ["python3", "/app/src/server.py"]

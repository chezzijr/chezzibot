FROM python:3.12.11-alpine3.22
WORKDIR /app
COPY . .
RUN apk add ffmpeg git && \
    pip install -r requirements.txt
CMD python3 main.py

FROM python:3.11-slim

WORKDIR /app

COPY . .

RUN PIP_PROGRESS_BAR=off python -m pip install --upgrade pip==24.3.1

RUN PIP_PROGRESS_BAR=off pip install -r requirements.txt

COPY wait-for-it.sh /app/wait-for-it.sh
RUN chmod +x /app/wait-for-it.sh

CMD ["uvicorn", "app:app"]

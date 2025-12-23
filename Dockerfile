FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt
COPY . .

RUN chmod +x entrypoint.sh

EXPOSE 8008

# Use entrypoint script
CMD ["./entrypoint.sh"]

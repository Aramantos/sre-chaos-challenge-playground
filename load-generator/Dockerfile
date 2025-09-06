FROM python:3.9-slim

WORKDIR /app

COPY load_test.py .

RUN pip install requests

CMD ["python", "load_test.py", "http://web", "10"]

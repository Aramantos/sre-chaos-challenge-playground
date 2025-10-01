FROM python:3.9-slim

WORKDIR /app

COPY load_test.py .
COPY stress_test.py .

RUN pip install requests
RUN pip install python-dotenv

CMD ["python", "load_test.py", "http://url-anvil", "10"]

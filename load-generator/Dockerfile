FROM python:3.9-slim

WORKDIR /app

COPY load_test.py .
COPY stress_test.py .
COPY local_tracker_client.py .

RUN pip install requests
RUN pip install python-dotenv

CMD ["tail", "-f", "/dev/null"]
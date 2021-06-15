FROM python:3.8.10-slim-buster

WORKDIR /code

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY test_integration.py .

ENV REQUESTS_CA_BUNDLE=/etc/ssl/certs/az.pem

CMD ["python", "-m", "pytest"]

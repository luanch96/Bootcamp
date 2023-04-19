FROM python:3.9-alpine

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY . .

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE 1
# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED 1

# Run tests to check everything is fine
RUN pytest

#CMD python -m debugpy --wait-for-client --listen 0.0.0.0:5678 -m flask run --host=0.0.0.0
CMD python -m flask run --host=0.0.0.0
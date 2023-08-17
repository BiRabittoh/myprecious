FROM tecktron/python-waitress:slim

RUN pip install --upgrade pip

WORKDIR /app
COPY ./requirements.txt .
RUN pip install -r requirements.txt

COPY ./migrations ./migrations
COPY ./myprecious ./myprecious

ENV APP_MODULE=myprecious:app

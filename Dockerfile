FROM python:3.6.7-alpine

WORKDIR /usr/src/app

COPY ./requirements.txt /usr/src/app/requirements.txt

RUN apk add libressl-dev
RUN apk add libffi-dev

RUN apk add --update python3 python3-dev py-pip build-base
RUN pip3 install -r requirements.txt

COPY . /usr/src/app

#CMD python run.py
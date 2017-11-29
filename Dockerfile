FROM ubuntu:16.04

RUN mkdir -p /resplat
WORKDIR /resplat
ADD . /resplat


RUN sh jenkins/setup.sh

EXPOSE 80
ENTRYPOINT service apache2 start && python3


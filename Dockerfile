FROM ubuntu:16.04

RUN mkdir -p /resplat
WORKDIR /resplat
ADD . /resplat


RUN sh jenkins/apt_setup.sh
RUN sh jenkins/apache_setup.sh

EXPOSE 443
CMD ["python3"]

FROM ubuntu

RUN apt-get update && apt-get -y install curl python-setuptools python-dev g++

ADD dist/fastscore-cli-dev.tar.gz .
RUN cd fastscore-cli-dev && python setup.py install
CMD fastscore

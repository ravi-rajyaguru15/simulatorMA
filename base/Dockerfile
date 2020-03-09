#FROM git.uni-due.de:6666/embedded-systems/docker-images/keras-python3:latest-gpu
FROM python:3.7

COPY requirements.txt ./requirements.txt
RUN pip3 install -r ./requirements.txt --disable-pip-version-check

RUN apt-get update
RUN apt-get install -y openssh-server
COPY authorized_keys /root/.ssh/authorized_keys

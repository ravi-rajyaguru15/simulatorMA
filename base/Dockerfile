#FROM git.uni-due.de:6666/embedded-systems/docker-images/keras-python3:latest-gpu
FROM python:3.7

COPY requirements.txt ./requirements.txt
RUN pip3 install -r ./requirements.txt --disable-pip-version-check
FROM git.uni-due.de:6666/embedded-systems/docker-images/keras-python3:latest-gpu

WORKDIR /app

#ENV PYTHONPATH "/app/src"

COPY ./sim ./sim

# install the dependencies
#RUN apt-get update # ;
#RUN apt-get install python3-pip python3-dev

#RUN apt-get install gcc

# COPY ./requirements.txt ./requirements.txt
# RUN pip3 install -r ./requirements.txt --disable-pip-version-check
ENTRYPOINT ["./sim/entrypoint.py"]
# ENTRYPOINT ["/usr/bin/python3", "/app/elasticNode.py", "loadann"]
# CMD ["sh", "-c", "/usr/bin/python /app/src/training.py.old"]
# CMD ["sh", "-c", "/usr/bin/python /app/src/training.py.old /cpu:0 10 10 100 128"]
FROM tensorflow/tensorflow

WORKDIR /app

#ENV PYTHONPATH "/app/src"

COPY ../src ./src

# install the dependencies
#RUN apt-get update # ;
#RUN apt-get install python3-pip python3-dev

#RUN apt-get install gcc

#RUN pip3 install -r ./requirements.txt # --disable-pip-version-check

# ENTRYPOINT ["/usr/bin/python3", "/app/elasticNode.py", "loadann"]
#CMD ["sh", "-c", "/usr/bin/python /app/src/training.py"]
#CMD ["sh", "-c", "/usr/bin/python /app/src/training.py /gpu:0 10 10 100 128"]
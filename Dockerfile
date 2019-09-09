FROM keras-python3

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
# CMD ["sh", "-c", "/usr/bin/python /app/src/training.py"]
# CMD ["sh", "-c", "/usr/bin/python /app/src/training.py /cpu:0 10 10 100 128"]
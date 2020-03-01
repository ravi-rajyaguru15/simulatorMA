#FROM git.uni-due.de:6666/embedded-systems/docker-images/keras-python3:latest-gpu
FROM git.uni-due.de:6666/embedded-systems/elastic-node/simulator/base:latest


#ENV PYTHONPATH "/app/src"

COPY sim /sim
COPY localConstants.py.server /sim/simulations/localConstants.py

# install the dependencies
#RUN apt-get update # ;
#RUN apt-get install -y python3-pip python3-dev

#RUN apt-get install gcc

#COPY ../base/requirements.txt ./requirements.txt
#RUN pip3 install -r ./requirements.txt --disable-pip-version-check
#ENTRYPOINT ["/sim/entrypoint.py"]
ENTRYPOINT ["python3", "/sim/entrypoint.py"]
#ENTRYPOINT["/usr/bin/python3", "/sim/entrypoint.py"]
# ENTRYPOINT ["/usr/bin/python3", "/app/elasticNode.py", "loadann"]
# CMD ["sh", "-c", "/usr/bin/python /app/src/training.py.old"]
# CMD ["sh", "-c", "/usr/bin/python /app/src/training.py.old /cpu:0 10 10 100 128"]

#WORKDIR /app

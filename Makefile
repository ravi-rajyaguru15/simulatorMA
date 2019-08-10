drone:
	DRONE_REPO_NAME=simulator DRONE_COMMIT_SHA=1 drone exec --trusted --include small_test

# training.py DEVICE HIDDEN_SIZE HIDDEN_DEPTH TRAINING_SIZE BATCH_SIZE
docker:
	docker build --no-cache ./ -t test
	docker run test
	
docker-gpu:
	docker build -f Dockerfile.gpu --no-cache ./ -t test
	docker run --runtime=nvidia test 

local:
	python3 src/training.py /cpu:0 100 1 10000 100 128
	
requirements:
	pip3 install -r requirements.txt

all:
	python3 training.py

# experiments:
jobsize:
	PYTHONPATH=$${PWD} python3 sim/experiments/jobSize.py
batchsize:
	PYTHONPATH=$${PWD} python3 sim/experiments/batchSize.py
fpgapowerplan:
	PYTHONPATH=$${PWD} python3 sim/experiments/fpgaPowerPlan.py
offloadingpolicy:
	PYTHONPATH=$${PWD} python3 sim/experiments/offloadingPolicies.py

sim:
	@echo "sim"
	PYTHONPATH=$${PWD} python3 sim/simulation.py

experiment:
	PYTHONPATH=$${PWD} python3 sim/experiments/offloadingPolicies.py

.PHONY: *
test: offloadingpolicy
	@echo "running test"
	# python sim.py
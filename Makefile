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

# # experiments:
# jobsize:
# 	python3 sim/experiments/jobSize.py
# batchsize:
# 	python3 sim/experiments/batchSize.py
# fpgapowerplan:
# 	python3 sim/experiments/fpgaPowerPlan.py
# offloadingpolicy:
# 	sim/experiments/offloadingPolicies.py
# sleeptime:
# 	python3 sim/experiments/sleepTime.py

# experiment:
# 	# PYTHONPATH=$${PWD} python3 sim/experiments/experiment.py
# 	python3 sim/experiments/experiment.py

.DEFAULT:
	python3 sim/experiments/$@.py

sim:
	@echo "sim"
	python3 sim/simulation.py

.PHONY: *
test: timeStability
	@echo $$DISPLAY
	@echo "running test"
	# python sim.py
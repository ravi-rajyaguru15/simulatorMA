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
	python src/training.py /cpu:0 100 1 10000 100 128
	
all:
	python training.py

test:
	python src/sim.py 0 2 0
	# python sim.py
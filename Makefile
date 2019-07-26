docker:
	docker build --no-cache ./ -t test
	docker run test
	docker run --runtime=nvidia

drone:
	DRONE_REPO_NAME=simulator DRONE_COMMIT_SHA=1 drone exec --trusted --include small_test

all:
	python training.py 
	# python sim.py
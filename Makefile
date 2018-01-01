drone:
	DRONE_REPO_NAME=simulator DRONE_COMMIT_SHA=1 drone exec --trusted

all:
	python training.py
	# python sim.py
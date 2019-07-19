drone:
	set DRONE_REPO_NAME:=simulator
	set DRONE_COMMIT_SHA:=1
	drone exec --trusted --include small_test

all:
	python training.py
	# python sim.py
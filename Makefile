drone:
	DRONE_REPO_NAME=simulator DRONE_COMMIT_SHA=1 drone exec --trusted --include small_test

dockerBasic:
	docker build ./basicDocker -t keras-python3

localdocker:
	./sim/entrypoint.py


NAME:=$(shell uname -r)
relpathwindows:=/mnt/c
relpathlinux:="$(pwd)"
docker: dockerBasic
	docker build --no-cache ./ -t test
	# echo name: $(NAME)
    ifneq (,$(findstring Microsoft,$(NAME)) )
		docker run -v $(relpathwindows)/output:/output test
    else
		docker run -v $(relpathlinux)/output:/output test
    endif
	
	
docker-gpu:
	docker build -f Dockerfile.gpu --no-cache ./ -t test
	docker run --runtime=nvidia test 

local:
	python3 src/training.py /cpu:0 100 1 10000 100 128
	
requirements:
	pip3 install -r requirements.txt

.DEFAULT:
	python3 sim/experiments/$@.py

sim:
	@echo "sim"
	python3 sim/simulation.py

testq:
	python3 sim/tictactoe.py

.PHONY: *
test: testq
	@echo $$DISPLAY
	@echo "running test"
	# python sim.py
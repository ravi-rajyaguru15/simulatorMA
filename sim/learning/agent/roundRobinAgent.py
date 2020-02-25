def updateOffloadingTarget():
	assert sharedClock is not None

	newTarget = False
	# decide if
	if offloadingDecision.previousUpdateTime is None:
		sim.debug.out("first round robin")
		# start at the beginning
		offloadingDecision.currentTargetIndex = 0
		newTarget = True
	elif sharedClock >= (offloadingDecision.previousUpdateTime + constants.ROUND_ROBIN_TIMEOUT):
		# print ("next round robin")
		offloadingDecision.currentTargetIndex += 1
		if offloadingDecision.currentTargetIndex >= len(offloadingDecision.options):
			# start from beginning again
			offloadingDecision.currentTargetIndex = 0
		newTarget = True

	# new target has been chosen:
	if newTarget:
		# indicate to old target to process batch immediately
		if offloadingDecision.target is not None:
			sim.debug.out("offloading target", offloadingDecision.target.offloadingDecision)
			# time.sleep(1)
			offloadingDecision.target.addSubtask(sim.subtask.batchContinue(node=offloadingDecision.target))

		offloadingDecision.previousUpdateTime = sharedClock.current
		offloadingDecision.target = offloadingDecision.options[offloadingDecision.currentTargetIndex]

		sim.debug.out("Round robin update: {}".format(offloadingDecision.target), 'r')



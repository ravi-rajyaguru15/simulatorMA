import numpy as np
import random
import matplotlib.pyplot as plt
import sys
import os 
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 
import rl.agents
import rl.memory
import keras
# import keras.utils

# %matplotlib inline
import sim.dqn as dqn
# import dqn

# import sim.memory
class scenario:
	# s0/0 - s1 - s2 - s3/1
	# -- s0/0 - s1 - s2/1
	def __init__(self):
		pass

	state = None
	def reset(self):
		# print('reset')
		self.state = 1
		return self.state

	action_space = np.array([0, 1]) # left, right
	observation_space = np.array([0, 1, 2, 3])

	def step(self, action):
		done = False
		if action == 0:
			nextState = self.state - 1
		else:
			nextState = self.state + 1

			
		reward = 0
		if nextState == 0 or nextState == 3:
			reward = 1 if (nextState == 3) else 0
			done = True

		self.state = nextState
		return nextState, reward, done
	

def forward(agent, env):
	# forward
	observation = [0 if i != env.state else 1 for i in range(len(env.observation_space))]
	q_values = agent.compute_q_values([observation])

	action = agent.policy.select_action(q_values=q_values)

	#Get new state and reward from environment
	nextState,reward,done = env.step(action)

	return nextState, reward, done, action
	
def backward(agent, env, oldState, reward, done, action):
	# backward
	observation = [0 if i != oldState else 1 for i in range(len(env.observation_space))]
	observationAfter = [0 if i != env.state else 1 for i in range(len(env.observation_space))]

	# Compute the q_values given state1, and extract the maximum for each sample in the batch.
	# We perform this prediction on the target_model instead of the model for reasons
	# outlined in Mnih (2015). In short: it makes the algorithm more stable.
	batch = np.array([np.array([np.array(observationAfter)])])
	target_q_values = agent.model.predict_on_batch(batch) # TODO: target_model
	q_batch = np.max(target_q_values, axis=1).flatten()
	
	targets = np.zeros((1, numActions))
	dummy_targets = np.zeros((1,))
	masks = np.zeros((1, numActions))

	# Compute r_t + gamma * max_a Q(s_t+1, a) and update the target targets accordingly,
	# but only for the affected output units (as given by action_batch).
	discounted_reward_batch = agent.gamma * q_batch
	# Set discounted reward to zero for all states that were terminal.
	discounted_reward_batch *= [0. if done else 1.] 
	# assert discounted_reward_batch.shape == reward_batch.shape
	R = reward + discounted_reward_batch
	targets[0, action] = R  # update action with estimated accumulated reward
	dummy_targets[0] = R
	masks[0, action] = 1.  # enable loss for this specific action

	targets = np.array(targets).astype('float32')
	masks = np.array(masks).astype('float32')


	# Finally, perform a single update on the entire batch. We use a dummy target since
	# the actual loss is computed in a Lambda layer that needs more complex input. However,
	# it is still useful to know the actual target to compute metrics properly.
	x = [np.array([[observation]])] + [targets, masks]
	y = [dummy_targets, targets]

	agent.trainable_model._make_train_function()
	metrics = agent.trainable_model.train_on_batch(x, y)
	metrics = metrics[1:3]
	metrics += agent.policy.metrics

	agent.step += 1
	agent.update_target_model_hard()

	return metrics

numStates = len(scenario.observation_space)
numActions = len(scenario.action_space)
# states
env = scenario() # gym.make('FrozenLake-v0')

# Next, we build a very simple model.
model = keras.models.Sequential()
model.add(keras.layers.Flatten(input_shape=(1,) + env.observation_space.shape))
print('input shape', (1,) + env.observation_space.shape)
model.add(keras.layers.Dense(4))
model.add(keras.layers.Activation('relu'))
model.add(keras.layers.Dense(16))
model.add(keras.layers.Activation('relu'))
# model.add(Dense(16))
# model.add(Activation('relu'))
model.add(keras.layers.Dense(numActions))
model.add(keras.layers.Activation('linear'))
print(model.summary())
# keras.utils.plot_model(model, show_shapes=True, expand_nested=True)

memory = rl.memory.SequentialMemory(limit=1000000, window_length=1) # window length?


# Select a policy. We use eps-greedy action selection, which means that a random action is selected
# with probability eps. We anneal eps from 1.0 to 0.1 over the course of 1M steps. This is done so that
# the agent initially explores the environment (high eps) and then gradually sticks to what it knows
# (low eps). We also set a dedicated eps value that is used during testing. Note that we set it to 0.05
# so that the agent still performs some random actions. This ensures that the agent cannot get stuck.
policy = rl.policy.LinearAnnealedPolicy(rl.policy.EpsGreedyQPolicy(), attr='eps', value_max=1., value_min=.01, value_test=.05, nb_steps=100)

agent = dqn.DQNAgent(model, enable_double_dqn=False, nb_actions=numActions, gamma=.99, memory=memory, policy=policy, nb_steps_warmup=2, train_interval=1, batch_size=1)
agent.compile(keras.optimizers.Adam(lr=.001), metrics=['mae'])
agent.training = True
print(agent.trainable_model.metrics_names)

print('initial weights:', agent.model.get_weights())


# Set learning parameters
y = .99
e = 0.1
num_episodes = int(1e3)
#create lists to contain total rewards and steps per episode
jList = []
rList = []
aList = []
eList = []
lossList = []
metricsList = []

for i in range(num_episodes):
	if i % 100 == 0:
		sys.stdout.write("\r{:.2f}".format(float(i) / num_episodes * 100))
	#Reset environment and get first new observation
	s = env.reset()
	rAll = 0
	done = False
	j = 0
	#The Q-Network
	while j < 99 and not done:
		j+=1
		
		oldState = env.state
		nextState, reward, done, action = forward(agent, env)
		metrics = backward(agent, env, oldState, reward, done, action)

		lossList.append(metrics[0])
		metricsList.append(metrics)
		aList.append(action)

		rAll += reward
	
	jList.append(j)
	rList.append(rAll)
print ("Percent of succesful episodes: {:.2f} %".format(sum(rList)/num_episodes * 100.0))

plt.figure(1)
plt.plot(jList)
plt.savefig('/output/jlist.png')
plt.figure(2)
plt.plot(rList)
plt.savefig('/output/rlist.png')
plt.figure(3)
plt.plot(lossList)
plt.savefig('/output/loss.png')



# plt.show()


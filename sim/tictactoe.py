import numpy as np

import os
# oldBackend = mpl.get_backend()
# print ("existing", oldBackend)
# if os.name != 'nt':
# 	try:
# 		mpl.use("pdf")
# 		# mpl.use("Qt4Agg")
# 	except ImportError:
# 		mpl.use(oldBackend)
# 		print ("Cannot import MPL backend")
import matplotlib.pyplot as plt
import sys
# os.environ['DISPLAY'] = "localhost:10.0"
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 
# import rl.agents
# import rl.memory
import rl
import rl.util
# import keras
# import keras.utils
import tensorflow as tf
print("GPU Available: ", tf.test.is_gpu_available())
import tensorflow.keras as keras
print(tf.__version__)

# %matplotlib inline
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
	


# import sim.memory
class singleStateScenario:
	# s0/0 - s1 - s2 - s3/1
	# -- s0/0 - s1 - s2/1
	def __init__(self):
		pass

	state = None
	def reset(self):
		# print('reset')
		self.state = 1/3.
		return self.state

	action_space = np.array([0, 1]) # left, right
	observation_space = np.array([0])

	def step(self, action):
		done = False
		if action == 0:
			nextState = self.state - 1/3.
		else:
			nextState = self.state + 1/3.

			
		reward = 0
		if nextState == 0 or nextState == 1.:
			reward = 1 if (nextState == 1.) else 0
			done = True

		self.state = nextState
		return nextState, reward, done
	

def forward(model, env):
	# forward
	# observation = [0 if i != env.state else 1 for i in range(len(env.observation_space))]
	observation = [env.state]
	q_values = model.predict(np.array(observation).reshape((1, 1, len(env.observation_space))))

	# # inspection model
	# inspect = keras.Model(inputs=model.input, outputs=model.get_layer(index=0).output)
	# # inspectOutput = inspect.predict(np.array(observation).reshape((1, 1, len(env.observation_space))))
	# print(observation)
	# print(np.array(observation).reshape((1, 1, len(env.observation_space))))
	# print(inspect.predict(np.array(observation).reshape((1, 1, len(env.observation_space)))))

	action = policy.select_action(q_values=q_values[0])

	#Get new state and reward from environment
	nextState,reward,done = env.step(action)

	return nextState, reward, done, action
	
def backward(model, trainable_model, env, oldState, reward, done, action):
	# backward
	observation = [0 if i != oldState else 1 for i in range(len(env.observation_space))]
	observationAfter = [0 if i != env.state else 1 for i in range(len(env.observation_space))]

	# Compute the q_values given state1, and extract the maximum for each sample in the batch.
	# We perform this prediction on the target_model instead of the model for reasons
	# outlined in Mnih (2015). In short: it makes the algorithm more stable.
	batch = np.array([np.array([np.array(observationAfter)])])
	target_q_values = model.predict_on_batch(batch) # TODO: target_model
	q_batch = np.max(target_q_values, axis=1).flatten()
	
	targets = np.zeros((1, numActions))
	dummy_targets = np.zeros((1,))
	masks = np.zeros((1, numActions))

	# Compute r_t + gamma * max_a Q(s_t+1, a) and update the target targets accordingly,
	# but only for the affected output units (as given by action_batch).
	discounted_reward_batch = gamma * q_batch
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

	trainable_model._make_train_function()
	metrics = trainable_model.train_on_batch(x, y)
	metrics = metrics[1:3]
	metrics += policy.metrics

	# agent.step += 1
	# agent.update_target_model_hard()

	return metrics

env = singleStateScenario() # gym.make('FrozenLake-v0')

# states
numStates = len(env.observation_space)
numActions = len(env.action_space)

# Next, we build a very simple model.
model = tf.keras.models.Sequential()
print (env.observation_space.shape)
model.add(tf.keras.layers.Flatten(input_shape=(1,) + env.observation_space.shape))
print('input shape', (1,) + env.observation_space.shape)
# model.add(keras.layers.Dense(4))
# model.add(keras.layers.Activation('relu'))
# model.add(keras.layers.Dense(16))
# model.add(keras.layers.Activation('relu'))
# model.add(Dense(16))
# model.add(Activation('relu'))
model.add(tf.keras.layers.Dense(numActions))
model.add(tf.keras.layers.Activation('linear'))
# model.summary()

# plt.figure(6, figsize=(10,10))
# keras.utils.plot_model(model, to_file='model.png', show_shapes=True, expand_nested=True, dpi=300)
# plt.imshow(mpl.image.imread('model.png'))
# plt.axis('off')
# memory = rl.memory.SequentialMemory(limit=1000000, window_length=1) # window length?


# Select a policy. We use eps-greedy action selection, which means that a random action is selected
# with probability eps. We anneal eps from 1.0 to 0.1 over the course of 1M steps. This is done so that
# the agent initially explores the environment (high eps) and then gradually sticks to what it knows
# (low eps). We also set a dedicated eps value that is used during testing. Note that we set it to 0.05
# so that the agent still performs some random actions. This ensures that the agent cannot get stuck.
# policy = rl.policy.LinearAnnealedPolicy(rl.policy.EpsGreedyQPolicy(), attr='eps', value_max=1., value_min=.01, value_test=.05, nb_steps=100)
policy = rl.policy.EpsGreedyQPolicy(eps=.1)

gamma=.99
# agent = dqn.DQNAgent(model, enable_double_dqn=False, nb_actions=numActions, gamma=.99, memory=memory, policy=policy, nb_steps_warmup=2, train_interval=1, batch_size=1)
optimizer = tf.keras.optimizers.Adam(lr=.001)
# agent.compile(, metrics=['mae'])
metrics = ['mae']
def clipped_masked_error(args):
	y_true, y_pred, mask = args
	loss = rl.util.huber_loss(y_true, y_pred, np.inf)# self.delta_clip)
	loss *= mask  # apply element-wise mask
	return tf.keras.backend.sum(loss, axis=-1)

# Create trainable model. The problem is that we need to mask the output since we only
# ever want to update the Q values for a certain action. The way we achieve this is by
# using a custom Lambda layer that computes the loss. This gives us the necessary flexibility
# to mask out certain parameters by passing in multiple inputs to the Lambda layer.
y_pred = model.output
y_true = keras.layers.Input(name='y_true', shape=(numActions,))
mask = keras.layers.Input(name='mask', shape=(numActions,))
loss_out = keras.layers.Lambda(clipped_masked_error, output_shape=(1,), name='loss')([y_true, y_pred, mask])
ins = [model.input] if type(model.input) is not list else model.input
trainable_model = keras.Model(inputs=ins + [y_true, mask], outputs=[loss_out, y_pred])
assert len(trainable_model.output_names) == 2
combined_metrics = {trainable_model.output_names[1]: metrics}
losses = [
	lambda y_true, y_pred: y_pred,  # loss is computed in Lambda layer
	lambda y_true, y_pred: keras.backend.zeros_like(y_pred),  # we only include this for the metrics
]
trainable_model.compile(optimizer=optimizer, loss=losses, metrics=combined_metrics)
# self.trainable_model = trainable_model
# agent.training = True
# print(trainable_model.metrics_names)
# print(trainable_model.summary())
# plt.figure(5, figsize=(25,25))
# keras.utils.plot_model(trainable_model, to_file='trainable_model.png', show_shapes=True, expand_nested=True, dpi=300)
# plt.imshow(mpl.image.imread('trainable_model.png'))
# plt.axis('off')

print('initial weights:', model.get_weights())


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
		# warnings.warn("short job!")
		j+=1
		
		oldState = env.state
		nextState, reward, done, action = forward(model, env)
		metrics = backward(model,trainable_model,  env, oldState, reward, done, action)

		lossList.append(metrics[0])
		metricsList.append(metrics)
		aList.append(action)

		rAll += reward
	
	jList.append(j)
	rList.append(rAll)
print ("Percent of succesful episodes: {:.2f} %".format(sum(rList)/num_episodes * 100.0))
import os
# print (os.environ["DISPLAY"])
if "DISPLAY" not in os.environ:
	os.environ["DISPLAY"] = "localhost:10.0"
	print("set display to", os.environ["DISPLAY"])
else:
    print ("Existing DISPLAY={}".format(os.environ["DISPLAY"]))
plt.figure(1)
plt.title('duration')
plt.plot(jList);
plt.savefig('/output/jlist.png')
plt.figure(2)
plt.title('rewards')
plt.plot(rList);
plt.savefig('/output/rlist.png')
plt.figure(3)
plt.title('loss')
plt.plot(lossList);
plt.savefig('/output/loss.png')
# plt.show()


# plt.show()

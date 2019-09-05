# import gym
import numpy as np
import random
import matplotlib.pyplot as plt
import rl.agents
import rl.memory
import keras
# %matplotlib inline

class scenario:
    # s0/0 - s1 - s2 - s3/1
    def __init__(self):
        pass

    state = None
    def reset(self):
        # print('reset')
        self.state = 1
        return self.state

    action_space = np.array([0, 1]) # left, right
    observation_space = np.array([0, 1, 2, 3])
    def action_space_sample(self):
        return np.random.choice(self.action_space)

    def step(self, action):
        done = False
        if action == 0:
            nextState = self.state - 1
        else:
            nextState = self.state + 1

            
        reward = 0
        if nextState == 0 or nextState == 3: 
            if nextState == 3:
                reward = 1
            else:
                reward = 0
            done = True

        self.state = nextState
        return nextState, reward, done
    

def forward(agent, env):
    # forward
    observation = [0 if i != env.state else 1 for i in range(len(env.observation_space))]
    # action = agent.forward(observation)
    # state = self.memory.get_recent_state(observation)
    q_values = agent.compute_q_values([observation])
    # print('q_values', agent.compute_q_values([observation]))
    action = agent.policy.select_action(q_values=q_values)
    # print('action', action)

    # a,allQ = sess.run([predict,Qout],feed_dict={inputs1:[[s]]})
    # if np.random.rand(1) < e:
    #     a[0] = env.action_space_sample()
    #Get new state and reward from environment
    nextState,reward,done = env.step(action)

    return nextState, reward, done, action
    # print(nextState, reward, done)
    
def backward(agent, env, oldState, reward, done, action):
    # backward
    # agent.backward(r, d)
    observation = [0 if i != oldState else 1 for i in range(len(env.observation_space))]
    observationAfter = [0 if i != env.state else 1 for i in range(len(env.observation_space))]

    # print(observationAfter)
    agent.step += 1    
    # Compute the q_values given state1, and extract the maximum for each sample in the batch.
    # We perform this prediction on the target_model instead of the model for reasons
    # outlined in Mnih (2015). In short: it makes the algorithm more stable.
    batch = np.array([np.array([np.array(observationAfter)])])
    # print(observationAfter, batch)
    target_q_values = agent.target_model.predict_on_batch(batch) # TODO: target_model
    # print(target_q_values)
    # target_q_values = agent.target_model.predict_on_batch([np.array(observationAfter)]) # TODO: target_model
    q_batch = np.max(target_q_values, axis=1).flatten()
    # print ("q_batch", q_batch)
    
    targets = np.zeros((1, numActions))
    dummy_targets = np.zeros((1,))
    masks = np.zeros((1, numActions))

    # Compute r_t + gamma * max_a Q(s_t+1, a) and update the target targets accordingly,
    # but only for the affected output units (as given by action_batch).
    discounted_reward_batch = agent.gamma * q_batch
    # print (discounted_reward_batch)
    # Set discounted reward to zero for all states that were terminal.
    discounted_reward_batch *= [0. if done else 1.] 
    # assert discounted_reward_batch.shape == reward_batch.shape
    R = reward + discounted_reward_batch
    # for idx, (target, mask, R, action) in enumerate(zip(targets, masks, Rs, action_batch)):
    targets[0, action] = R  # update action with estimated accumulated reward
    dummy_targets[0] = R
    masks[0, action] = 1.  # enable loss for this specific action
    targets = np.array(targets).astype('float32')
    masks = np.array(masks).astype('float32')

    

    # Finally, perform a single update on the entire batch. We use a dummy target since
    # the actual loss is computed in a Lambda layer that needs more complex input. However,
    # it is still useful to know the actual target to compute metrics properly.
    # observation = np.array(observation)
    # ins = [observation] if type(agent.model.input) is not list else observation
    x = [[[observation]]] + [targets, masks]
    y = [dummy_targets, targets]
    metrics = agent.trainable_model.train_on_batch(x, y)


    # if age.target_model_update >= 1 and self.step % self.target_model_update == 0:
    #     print ('4')

    agent.update_target_model_hard()
    
    # if r != 0:
    #     print(s1, r, d)
    #Obtain the Q' values by feeding the new state through our network
    # Q1 = sess.run(Qout,feed_dict={inputs1:[[s1]]})
    #Obtain maxQ' and set our target value for chosen action.
    # maxQ1 = np.max(Q1)
    # targetQ = allQ
    # targetQ[0,a[0]] = r + y*maxQ1
    # #Train our network using target and predicted Q values
    # _,W1 = sess.run([updateModel,W],feed_dict={inputs1:[[s]],nextQ:targetQ})


numStates = len(scenario.observation_space)
numActions = len(scenario.action_space)
# states
env = scenario() # gym.make('FrozenLake-v0')

# Next, we build a very simple model.
model = keras.models.Sequential()
model.add(keras.layers.Flatten(input_shape=(1,) + env.observation_space.shape))
print('input shape', (1,) + env.observation_space.shape)
model.add(keras.layers.Dense(16))
model.add(keras.layers.Activation('relu'))
model.add(keras.layers.Dense(16))
model.add(keras.layers.Activation('relu'))
# model.add(Dense(16))
# model.add(Activation('relu'))
model.add(keras.layers.Dense(numActions))
model.add(keras.layers.Activation('linear'))

memory = rl.memory.SequentialMemory(limit=1000000, window_length=1) # window length?


# Select a policy. We use eps-greedy action selection, which means that a random action is selected
# with probability eps. We anneal eps from 1.0 to 0.1 over the course of 1M steps. This is done so that
# the agent initially explores the environment (high eps) and then gradually sticks to what it knows
# (low eps). We also set a dedicated eps value that is used during testing. Note that we set it to 0.05
# so that the agent still performs some random actions. This ensures that the agent cannot get stuck.
policy = rl.policy.LinearAnnealedPolicy(rl.policy.EpsGreedyQPolicy(), attr='eps', value_max=1., value_min=.1, value_test=.05,
                              nb_steps=1000000)

agent = rl.agents.DQNAgent(model, nb_actions=numActions, gamma=.99, memory=memory, policy=policy, nb_steps_warmup=2, train_interval=1, batch_size=1)
agent.compile(keras.optimizers.Adam(lr=.00025), metrics=['mae'])
agent.training = True
# print(agent.get_config())

#These lines establish the feed-forward part of the network used to choose actions
# inputs1 = tf.placeholder(shape=[1,numStates],dtype=tf.float32)
# W = tf.Variable(tf.random_uniform([numStates,numActions],0,0.01))
# Qout = tf.matmul(inputs1,W)
# predict = tf.argmax(Qout,1)

#Below we obtain the loss by taking the sum of squares difference between the target and prediction Q values.
# nextQ = tf.placeholder(shape=[1,numActions],dtype=tf.float32)
# loss = tf.reduce_sum(tf.square(nextQ - Qout))
# trainer = tf.train.GradientDescentOptimizer(learning_rate=0.1)
# updateModel = trainer.minimize(loss)

# init = tf.global_variables_initializer()

# Set learning parameters
y = .99
e = 0.1
num_episodes = 5000
#create lists to contain total rewards and steps per episode
jList = []
rList = []
eList = []
if True:
# with tf.Session() as sess:
#     sess.run(init)
    for i in range(num_episodes):
        #Reset environment and get first new observation
        s = env.reset()
        rAll = 0
        d = False
        j = 0
        #The Q-Network
        while j < 99:
            # print('j', j)
            j+=1
            #Choose an action by greedily (with e chance of random action) from the Q-network
            # print('observation', observation)
            # print('state', agent.memory.get_recent_state(observation))
            
            oldState = env.state
            nextState, reward, done, action = forward(agent, env)
            backward(agent, env, oldState, reward, done, action)


            # return metrics

            
            rAll += reward
            # s = nextState
            if done == True:
                # perform one more because reasons
                oldState = env.state
                nextState, reward, done, action = forward(agent, env)
                backward(agent, env, oldState, 0, False, action)

                # agent.forward(observation)
                # agent.backward(0, terminal=False)
                #Reduce chance of random action as we train the model.
                # e = 1./((i/50) + 10)
                break
        jList.append(j)
        rList.append(rAll)
        # eList.append(e)
print ("Percent of succesful episodes: " + str(sum(rList)/num_episodes) + "%")

plt.figure(1)
plt.plot(jList)
plt.figure(2)
plt.plot(rList)
# plt.figure(3)
# plt.plot(eList)


# TensorFlow and tf.keras
import tensorflow as tf
from tensorflow import keras
import sys
import multiprocessing

GUI = False

# Helper libraries
import numpy as np
if GUI:
	import matplotlib.pyplot as plt
	import matplotlib.pyplot as pp
from random import random

from sim import sim
from result import result

from datetime import datetime

TEST_SIZE = 1000
SAMPLE_SIZE = 10
EPOCHS = 1
THREADS = multiprocessing.cpu_count()
optimisation = "latency"

def train():
	# print(tf.__version__)
	start = datetime.now()

	simulation = sim()
	results = list()

	all_samples = list()
	# training
	processes = list()
	q = multiprocessing.Manager().Queue()
	print 'training size', TRAINING_SIZE
	for i in range(THREADS):
		training_samples = list()
		for j in range(TRAINING_SIZE/THREADS):
			sample = random() * SAMPLE_SIZE +1
			training_samples.append(sample)

		p = multiprocessing.Process(target=sim.simulateBatch, args=(simulation, training_samples, optimisation, q, ))
		processes.append(p)

	print 'processes:', len(processes)
	print 
	print 
	print 
	for process in processes:
		process.start()

	for process in processes:
		process.join()

	print 'sim time:', (datetime.now() - start).total_seconds()
		# results.append(simulation.simulateAll(sample, optimisation))

	for i in range(q.qsize()):
		value = q.get()
		# print value
		all_samples.append(value[0])
		results.append(value[1])

	results = np.array(results)
	# print 'results:\n', results
	mins = np.argmin(results, axis=1)
	# print mins
	# print 'mins:', mins
	# training_labels = np.zeros_like(results)
	# # print training_labels
	# for i in range(len(mins)):
	# 	training_labels[i, mins[i]] = 1
	training_labels = np.array(mins)
	training_samples = np.array(all_samples)
	# print training_labels

	# test
	results = list()
	test_samples = list()
	for i in range(TEST_SIZE):
		sample = random() * SAMPLE_SIZE +1
		test_samples.append(sample)
		results.append(simulation.simulateAll(sample, optimisation, None))

	results = np.array(results)
	mins = np.argmin(results, axis=1)
	# print results.shape, mins.shape
	test_labels = np.array(mins)
	test_samples = np.array(test_samples)

 	# training_samples = np.array(training_samples).reshape(len(training_samples), 1)

	# fashion_mnist = keras.datasets.fashion_mnist
	# (train_images, train_labels), (test_images, test_labels) = fashion_mnist.load_data()
	# print train_images.shape, train_labels.shape
	# print train_labels

	# train_images = train_images / 255.0

	# test_images = test_images / 255.0

	# class_names = ['T-shirt/top', 'Trouser', 'Pullover', 'Dress', 'Coat', 
	#                'Sandal', 'Shirt', 'Sneaker', 'Bag', 'Ankle boot']
	# plt.figure(figsize=(10,10))
	# for i in range(25):
	#     plt.subplot(5,5,i+1)
	#     plt.xticks([])
	#     plt.yticks([])
	#     plt.grid(False)
	#     plt.imshow(train_images[i], cmap=plt.cm.binary)
	#     plt.xlabel(class_names[train_labels[i]])
	# plt.show()

	print "compiling model"
	model = keras.Sequential()
	model.add(keras.layers.Dense(HIDDEN_SIZE, input_shape=(1,), activation=tf.nn.relu))
	for i in range(HIDDEN_DEPTH):
		model.add(keras.layers.Dense(HIDDEN_SIZE, activation=tf.nn.relu))
	model.add(keras.layers.Dense(4, activation=tf.nn.softmax))


    # keras.layers.Flatten(input_shape=(28, 28)),
	    # keras.layers.Dense(16, activation=tf.nn.relu),


	model.compile(optimizer='adam', 
	              loss='sparse_categorical_crossentropy',
	              metrics=['accuracy'])

	print "fitting model"
	# print 'input', training_samples.shape
	# print 'output', training_labels.shape
	model.fit(training_samples, training_labels, epochs=EPOCHS, batch_size=BATCH_SIZE)
	# model.fit(train_images, train_labels, epochs=5)

	print "evaluating model..."
	test_loss, test_acc = model.evaluate(test_samples, test_labels)
	# test_loss, test_acc = model.evaluate(test_images, test_labels)

	print('Test accuracy:', test_acc)
	# print('samples:', test_samples)
	predictions = model.predict(test_samples)

	# print('labels', test_labels)
	# print('predictions', predictions)
	# print(predictions.shape)
	# print('maxs', np.argmax(predictions,axis=1)).

	if GUI:
		pp.hist(np.argmax(predictions, axis=1), bins=simulation.numOptions())
		pp.xticks(np.array(range(simulation.numOptions())), simulation.nameOptions())

		pp.show()
	elif False:
		# print (predictions)
		hist, edges = np.histogram(np.argmax(predictions, axis=1), bins=simulation.numOptions(), range=(-0.5, simulation.numOptions()-0.5))
		# print np.argmax(predictions, axis=1)
		# print range(simulation.numOptions())
		# print np.histogram(np.argmax(predictions, axis=1), bins=simulation.numOptions())
		# print (output)
		print (simulation.nameOptions())
		print (hist)
		print (edges)
		groundTruth = np.histogram(test_labels, bins=simulation.numOptions())
		print (groundTruth[0])

		scaled = 0
		diffs = (np.abs(hist - groundTruth[0]))
		print diffs
		print 1. - float(np.sum(diffs)) / TEST_SIZE / 2.



if __name__ == '__main__':
	if len(sys.argv) > 2:
		HIDDEN_SIZE = int(sys.argv[2])
		HIDDEN_DEPTH = int(sys.argv[3])
		TRAINING_SIZE = int(sys.argv[4])
		BATCH_SIZE = int(sys.argv[5])
		device = sys.argv[1]
	else:
		print 'using defaults'
		HIDDEN_SIZE = 4
		HIDDEN_DEPTH = 4
		TRAINING_SIZE = 100
		BATCH_SIZE = 16
		device = '/cpu:0'

	conf = tf.ConfigProto(allow_soft_placement=True, log_device_placement=False)
	conf.gpu_options.allow_growth=True
	with tf.Session(config=conf):
		with tf.device(device):
			train()


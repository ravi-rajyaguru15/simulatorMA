# TensorFlow and tf.keras
import tensorflow as tf
from tensorflow import keras
import sys
import os
import multiprocessing
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

GUI = False

# Helper libraries
import numpy as np
if GUI:
	import matplotlib.pyplot as plt
	import matplotlib.pyplot as pp
from random import random

sys.path.append("simulator/src")

from sim import sim
from result import result

from datetime import datetime

# TEST_SIZE = 1000
# SAMPLE_SIZE = 10
EPOCHS = 10
THREADS = multiprocessing.cpu_count()
optimisation = "latency"

<<<<<<< HEAD
def train():
    # setup configuration

=======
# def randomSample():
# 	return random() * SAMPLE_SIZE +1


def train():
    # setup configuration

>>>>>>> a709e2d035deb79304005b41c6c4a7e55897d63e
	conf = tf.ConfigProto(allow_soft_placement=True, log_device_placement=False)
	conf.gpu_options.allow_growth=True
	with tf.Session(config=conf) as sess:
		with tf.device(device):
			

			# print(tf.__version__)
			start = datetime.now()

<<<<<<< HEAD
			simulation = sim()
=======
			simulation = sim(NUM_END_DEVICES, NUM_ELASTIC_NODES)
			simulation.selectedOptions = [0, 1]
>>>>>>> a709e2d035deb79304005b41c6c4a7e55897d63e
			results = list()

			all_samples = list()
			# training
			processes = list()
<<<<<<< HEAD
			q = multiprocessing.Manager().Queue()
=======

>>>>>>> a709e2d035deb79304005b41c6c4a7e55897d63e
			print ('training size', TRAINING_SIZE)
			for i in range(THREADS):
				training_samples = list()
				for j in range(TRAINING_SIZE/THREADS):
<<<<<<< HEAD
					sample = random() * SAMPLE_SIZE +1
					training_samples.append(sample)

				p = multiprocessing.Process(target=sim.simulateBatch, args=(simulation, training_samples, optimisation, q, ))
=======
					sample = randomSample()
					training_samples.append(sample)

				p = multiprocessing.Process(target=sim.simulateBatch, args=(simulation, training_samples, optimisation, ))
>>>>>>> a709e2d035deb79304005b41c6c4a7e55897d63e
				processes.append(p)

			print ('processes:', len(processes))
			print ()
<<<<<<< HEAD
			print ()
			print ()
=======
>>>>>>> a709e2d035deb79304005b41c6c4a7e55897d63e
			for process in processes:
				process.start()

			for process in processes:
				process.join()

			print 'sim time:', (datetime.now() - start).total_seconds()
				# results.append(simulation.simulateAll(sample, optimisation))

<<<<<<< HEAD
			for i in range(q.qsize()):
				value = q.get()
=======
			for i in range(simulation.queue.qsize()):
				value = simulation.queue.get()
>>>>>>> a709e2d035deb79304005b41c6c4a7e55897d63e
				# print value
				all_samples.append(value[0])
				results.append(value[1])

			results = np.array(results)
<<<<<<< HEAD
=======
			# print 'results shape', results.shape
>>>>>>> a709e2d035deb79304005b41c6c4a7e55897d63e
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
<<<<<<< HEAD
			# print training_labels
=======
>>>>>>> a709e2d035deb79304005b41c6c4a7e55897d63e

			# test
			results = list()
			test_samples = list()
			for i in range(TEST_SIZE):
<<<<<<< HEAD
				sample = random() * SAMPLE_SIZE +1
=======
				sample = randomSample()
>>>>>>> a709e2d035deb79304005b41c6c4a7e55897d63e
				test_samples.append(sample)
				results.append(simulation.simulateAll(sample, optimisation, None))

			results = np.array(results)
			mins = np.argmin(results, axis=1)
			# print results.shape, mins.shape
			test_labels = np.array(mins)
			test_samples = np.array(test_samples)

<<<<<<< HEAD
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
=======
			print "compiling model"
			model = keras.Sequential()

			model.add(keras.layers.Dense(HIDDEN_SIZE, input_shape=(1,), activation=tf.nn.relu))
			for i in range(HIDDEN_DEPTH):
				model.add(keras.layers.Dense(HIDDEN_SIZE, activation=tf.nn.relu))
			# model.add(keras.layers.Dense(4, activation=tf.nn.softmax))
			model.add(keras.layers.Dense(simulation.numSelectedOptions(), activation=tf.nn.softmax))
>>>>>>> a709e2d035deb79304005b41c6c4a7e55897d63e


			# keras.layers.Flatten(input_shape=(28, 28)),
				# keras.layers.Dense(16, activation=tf.nn.relu),


			model.compile(optimizer='adam', 
						loss='sparse_categorical_crossentropy',
						metrics=['accuracy'])

			print "fitting model"
<<<<<<< HEAD
			# print 'input', training_samples.shape
			# print 'output', training_labels.shape
=======
			print 'input', training_samples.shape
			print 'output', training_labels.shape
>>>>>>> a709e2d035deb79304005b41c6c4a7e55897d63e
			model.fit(training_samples, training_labels, epochs=EPOCHS, batch_size=BATCH_SIZE)
			# model.fit(train_images, train_labels, epochs=5)

			print "evaluating model..."
			test_loss, test_acc = model.evaluate(test_samples, test_labels)
			# test_loss, test_acc = model.evaluate(test_images, test_labels)

			print('Test accuracy:', test_acc)
			# print('samples:', test_samples)
<<<<<<< HEAD
=======
			# print test_samdples
>>>>>>> a709e2d035deb79304005b41c6c4a7e55897d63e
			predictions = model.predict(test_samples)

			# print('labels', test_labels)
			# print('predictions', predictions)
			# print(predictions.shape)
			# print('maxs', np.argmax(predictions,axis=1)).

			if GUI:
				pp.hist(np.argmax(predictions, axis=1), bins=simulation.numOptions())
				pp.xticks(np.array(range(simulation.numOptions())), simulation.nameOptions())

				pp.show()
<<<<<<< HEAD
			elif False:
				# print (predictions)
				hist, edges = np.histogram(np.argmax(predictions, axis=1), bins=simulation.numOptions(), range=(-0.5, simulation.numOptions()-0.5))
=======
			elif True:
				# print (predictions)
				hist, edges = np.histogram(np.argmax(predictions, axis=1), bins=simulation.numSelectedOptions(), range=(-0.5, simulation.numSelectedOptions()-0.5))
>>>>>>> a709e2d035deb79304005b41c6c4a7e55897d63e
				# print np.argmax(predictions, axis=1)
				# print range(simulation.numOptions())
				# print np.histogram(np.argmax(predictions, axis=1), bins=simulation.numOptions())
				# print (output)
<<<<<<< HEAD
				print (simulation.nameOptions())
				print (hist)
				print (edges)
				groundTruth = np.histogram(test_labels, bins=simulation.numOptions())
=======
				print (simulation.selectedNameOptions())
				print "hist"
				print (hist)
				print (edges)
				groundTruth = np.histogram(test_labels, bins=simulation.numSelectedOptions())
				print "groundtruth"
>>>>>>> a709e2d035deb79304005b41c6c4a7e55897d63e
				print (groundTruth[0])

				scaled = 0
				diffs = (np.abs(hist - groundTruth[0]))
<<<<<<< HEAD
=======
				print "diffs"
>>>>>>> a709e2d035deb79304005b41c6c4a7e55897d63e
				print diffs
				print 1. - float(np.sum(diffs)) / TEST_SIZE / 2.

		sess.close()

if __name__ == '__main__':
<<<<<<< HEAD
=======
	NUM_END_DEVICES = 0
	NUM_ELASTIC_NODES = 2
>>>>>>> a709e2d035deb79304005b41c6c4a7e55897d63e
	if len(sys.argv) > 4:
		HIDDEN_SIZE = int(sys.argv[2])
		HIDDEN_DEPTH = int(sys.argv[3])
		TRAINING_SIZE = int(sys.argv[4])
		TEST_SIZE = int(sys.argv[5])
		BATCH_SIZE = int(sys.argv[6])
		device = sys.argv[1]
	else:
		print 'using defaults'
		HIDDEN_SIZE = 2500
		HIDDEN_DEPTH = 5
		TRAINING_SIZE = 100000
<<<<<<< HEAD
=======
		TEST_SIZE = 100
>>>>>>> a709e2d035deb79304005b41c6c4a7e55897d63e
		BATCH_SIZE = 256
		device = '/cpu:0'

	p = multiprocessing.Process(target=train)
	p.start()
	p.join()



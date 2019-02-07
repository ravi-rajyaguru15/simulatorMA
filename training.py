# TensorFlow and tf.keras
import tensorflow as tf
from tensorflow import keras

# Helper libraries
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.pyplot as pp
from random import random

from sim import sim
from result import result

GUI = False

TRAINING_SIZE = 100000
TEST_SIZE = 1000
SAMPLE_SIZE = 1000
optimisation = "latency"

if __name__ == '__main__':
	# print(tf.__version__)

	simulation = sim()
	results = list()

	# training
	training_samples = list()
	for i in range(TRAINING_SIZE):
		sample = random() * SAMPLE_SIZE +1
		training_samples.append(sample)
		results.append(simulation.simulateAll(sample, optimisation))

	results = np.array(results)
	# print 'results:\n', results
	mins = np.argmin(results, axis=1)
	# print 'mins:', mins
	# training_labels = np.zeros_like(results)
	# # print training_labels
	# for i in range(len(mins)):
	# 	training_labels[i, mins[i]] = 1
	training_labels = np.array(mins)
	training_samples = np.array(training_samples)
	# print training_labels

	# test
	results = list()
	test_samples = list()
	for i in range(TEST_SIZE):
		sample = random() * SAMPLE_SIZE +1
		test_samples.append(sample)
		results.append(simulation.simulateAll(sample, optimisation))

	results = np.array(results)
	mins = np.argmin(results, axis=1)
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

	model = keras.Sequential([
	    # keras.layers.Flatten(input_shape=(28, 28)),
	    keras.layers.Dense(4, input_shape=(1,), activation=tf.nn.relu),
	    # keras.layers.Dense(16, activation=tf.nn.relu),
	    keras.layers.Dense(4, activation=tf.nn.softmax)
	])

	model.compile(optimizer='adam', 
	              loss='sparse_categorical_crossentropy',
	              metrics=['accuracy'])

	print 'input', training_samples.shape
	print 'output', training_labels.shape
	model.fit(training_samples, training_labels, epochs=1)
	# model.fit(train_images, train_labels, epochs=5)

	test_loss, test_acc = model.evaluate(test_samples, test_labels)
	# test_loss, test_acc = model.evaluate(test_images, test_labels)

	print('Test accuracy:', test_acc)

	predictions = model.predict(test_samples)

	# print(predictions)
	# print(predictions.shape)
	# print(np.argmax(predictions,axis=1).shape)

	if GUI:
		pp.hist(np.argmax(predictions, axis=1), bins=range(simulation.numOptions()))
		pp.xticks(0.5 + np.array(range(simulation.numOptions())), simulation.nameOptions())

		pp.show()
	else:
		np.hist(np.argmax(predictions, axis=1), bins=range(simulation.numOptions()))



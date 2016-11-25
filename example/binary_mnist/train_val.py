import mxnet as mx
import logging
import numpy as np
import matplotlib.pyplot as plt

logging.getLogger().setLevel(logging.DEBUG)

def to4d(img):
	return img.reshape(img.shape[0], 1, 28, 28).astype(np.float32)/255

def prepair_data(train_img, val_img, train_lbl, val_lbl, batch_size):	
	train_iter = mx.io.NDArrayIter(to4d(train_img), train_lbl, batch_size, shuffle=True)
	val_iter = mx.io.NDArrayIter(to4d(val_img), val_lbl, batch_size)
	return train_iter, val_iter

def get_lenet():
	data = mx.symbol.Variable('data')
	# first conv layer
	conv1 = mx.sym.Convolution(data=data, kernel=(5,5), num_filter=20)
	tanh1 = mx.sym.Activation(data=conv1, act_type="tanh")
	pool1 = mx.sym.Pooling(data=tanh1, pool_type="max", kernel=(2,2), stride=(2,2))
	# second conv layer
	conv2 = mx.sym.Convolution(data=pool1, kernel=(5,5), num_filter=50)
	tanh2 = mx.sym.Activation(data=conv2, act_type="tanh")
	pool2 = mx.sym.Pooling(data=tanh2, pool_type="max", kernel=(2,2), stride=(2,2))
	# first fullc layer
	flatten = mx.sym.Flatten(data=pool2)
	fc1 = mx.symbol.FullyConnected(data=flatten, num_hidden=500)
	tanh3 = mx.sym.Activation(data=fc1, act_type="tanh")
	# second fullc
	fc2 = mx.sym.FullyConnected(data=tanh3, num_hidden=10)
	# softmax loss
	lenet = mx.sym.SoftmaxOutput(data=fc2, name='softmax')
	return lenet

def get_binary_lenet():
	data = mx.symbol.Variable('data')
	# first conv layer
	conv1 = mx.sym.Convolution(data=data, kernel=(5,5), num_filter=20)
	tanh1 = mx.sym.Activation(data=conv1, act_type="tanh")
	pool1 = mx.sym.Pooling(data=tanh1, pool_type="max", kernel=(2,2), stride=(2,2))
	# second conv layer
	conv2 = mx.sym.Convolution(data=pool1, kernel=(5,5), num_filter=50)
	tanh2 = mx.sym.Activation(data=conv2, act_type="tanh")
	pool2 = mx.sym.Pooling(data=tanh2, pool_type="max", kernel=(2,2), stride=(2,2))
	# first fullc layer
	flatten = mx.sym.Flatten(data=pool2)
	fc1 = mx.symbol.FullyConnected(data=flatten, num_hidden=500)
	tanh3 = mx.sym.Activation(data=fc1, act_type="tanh")
	# second fullc
	fc2 = mx.sym.FullyConnected(data=tanh3, num_hidden=10)
	# softmax loss
	lenet = mx.sym.SoftmaxOutput(data=fc2, name='softmax')
	return lenet


def train(train_img, val_img, train_lbl, val_lbl, batch_size, gpu_id=0):
	lenet = get_lenet()
	train_iter, val_iter = prepair_data(train_img, val_img, train_lbl, val_lbl, batch_size)

	model = mx.model.FeedForward(
		ctx = mx.gpu(gpu_id),     # use GPU 0 for training, others are same as before
		symbol = lenet,   		  # network structure    
		num_epoch = 10,     	  # number of data passes for training 
		learning_rate = 0.1)
	model.fit(
		X=train_iter,  			# training data
		eval_data=val_iter, 	# validation data
		batch_end_callback = mx.callback.Speedometer(batch_size, 200) # output progress for each 200 data batches
	) 
	return model

def val(model_prefix, epoch_num, train_img, val_img, train_lbl, val_lbl, batch_size):
	print('Preparing data for validation...')
	train_iter, val_iter = prepair_data(train_img, val_img, train_lbl, val_lbl, batch_size)
	print('Loading model...')
	model = mx.model.FeedForward.load(model_prefix, epoch_num)
	print('Evaluating...')
	print 'Validation accuracy: %f%%' % (model.score(val_iter)*100,)

def classify(val_img, model_prefix, epoch_num):
	model = mx.model.FeedForward.load(model_prefix, epoch_num)
	plt.imshow(val_img[0], cmap='Greys_r')
	plt.axis('off')
	plt.show()
	prob = model.predict(to4d(val_img[0:1]))[0]
	print 'Classified as %d with probability %f' % (prob.argmax(), max(prob))
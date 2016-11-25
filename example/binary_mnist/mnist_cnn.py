import numpy as np
import os
import urllib
import gzip
import struct
import sys
import cv2
import argparse
import mxnet as mx
import matplotlib.pyplot as plt

from train_val import train as mnist_train
from train_val import val as mnist_val
from train_val import classify as mnist_classify


def download_data(url, force_download=True): 
	fname = url.split("/")[-1]
	if force_download or not os.path.exists(fname):
		urllib.urlretrieve(url, fname)
	return fname

def read_data(label_url, image_url, download=False):
	if download: 
		label_url=download_data(label_url) 
	if download: 
		image_url = download_data(image_url)
	with gzip.open(label_url) as flbl:
		magic, num = struct.unpack(">II", flbl.read(8))
		label = np.fromstring(flbl.read(), dtype=np.int8)
	with gzip.open(image_url, 'rb') as fimg:
		magic, num, rows, cols = struct.unpack(">IIII", fimg.read(16))
		image = np.fromstring(fimg.read(), dtype=np.uint8).reshape(len(label), rows, cols)
	return (label, image)


def prepare_data():
	path='data/'
	downloadable=False
	data_dir = 'data'
	if not os.path.exists(data_dir):
		os.makedirs(data_dir)
	if not os.path.isfile(os.path.join(data_dir, 'train-labels-idx1-ubyte.gz')) or \
		not os.path.isfile(os.path.join(data_dir, 'train-images-idx3-ubyte.gz')) or \
		not os.path.isfile(os.path.join(data_dir, 't10k-labels-idx1-ubyte.gz')) or \
		not os.path.isfile(os.path.join(data_dir, 't10k-images-idx3-ubyte.gz')):
		path='http://yann.lecun.com/exdb/mnist/'
		downloadable=True

	(train_lbl, train_img) = read_data(
		path+'train-labels-idx1-ubyte.gz', path+'train-images-idx3-ubyte.gz', downloadable)
	(val_lbl, val_img) = read_data(
		path+'t10k-labels-idx1-ubyte.gz', path+'t10k-images-idx3-ubyte.gz', downloadable)
	return train_img, val_img, train_lbl, val_lbl

def check_data_visually(train_img, train_lbl):
	for i in range(10):
		plt.subplot(1,10,i+1)
		plt.imshow(train_img[i], cmap='Greys_r')
		plt.axis('off')
	plt.show()
	print('label: %s' % (train_lbl[0:10],))


def main(args):    
	#prepare data, download if necessary  
	train_img, val_img, train_lbl, val_lbl = prepare_data()
	#can be used for checking mnist data with respect to its label
	#check_data_visually(train_img, train_lbl)      
	batch_size = 100
	if not args.predict:
		model = mnist_train(train_img, val_img, train_lbl, val_lbl, batch_size, args.gpu_id)
		model.save(args.out_file)
	else:
		#mnist_val(args.model_prefix, args.epochs, train_img, val_img, train_lbl, val_lbl, batch_size)
		mnist_classify(val_img, args.model_prefix, args.epochs)

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='generate generate annotations file from data source')
	parser.add_argument('-model_prefix', dest='model_prefix', type=str, help="gives where to find the binary model file and .json file")
	parser.add_argument('-o', dest='out_file', type=str, default=None, help='path to save model')
	parser.add_argument('-gpu', dest='gpu_id', type=int, default=0, help='selected gpu device id')
	parser.add_argument('--predict', dest='predict', action='store_true',default=False, help='whether do the prediction, otherwise do the training')
	parser.add_argument('-epochs', dest='epochs', type=int, default=0, help='set the epoch number')

	args = parser.parse_args()
	main(args)
import os
import cv2
import requests
import pickle
import numpy as np
import tensorflow as tf
import tensorflow_hub as hub
from cv2.ximgproc import createSuperpixelSEEDS
from mplime.models import Model

# mobilenet
MODEL_URL = "https://tfhub.dev/google/imagenet/mobilenet_v2_140_224/classification/3"
# inception-v3
# MODEL_URL = "https://tfhub.dev/google/imagenet/inception_v3/classification/3"
LABEL_URL = "https://storage.googleapis.com/download.tensorflow.org/data/ImageNetLabels.txt"
PICKLE_NAME = "./labels.pkl"
IMAGE_PATH = "./two_duck.jpg"

class ImageClf(Model):
    def __init__(self, seg_width, seg_height):
        # make module
        g = tf.Graph()
        with g.as_default():
            module = hub.Module(MODEL_URL)
            self.img_shape = tuple(hub.get_expected_image_size(module))
            self.img_input = tf.placeholder(dtype=float,
                                            shape=[tf.Dimension(None),
                                                   tf.Dimension(self.img_shape[0]),
                                                   tf.Dimension(self.img_shape[1]),
                                                   tf.Dimension(3)])
            self.module_img = module(self.img_input)
            init_op = tf.group([tf.global_variables_initializer(), tf.tables_initializer()])
        g.finalize()

        # create session and initialize
        self.session = tf.Session(graph=g)
        self.session.run(init_op)

        # load or download label infomation
        self.label_info = None
        if os.path.exists(PICKLE_NAME):
            print("the pickle file has already existed!!")
            with open(PICKLE_NAME, "rb") as f:
                self.label_info = pickle.load(f)
        else:
            # download label data
            labels = requests.get(LABEL_URL)
            index_to_label = {i: label for i, label in enumerate(labels.text.split("\n"))}
            label_to_index = {label: i for i, label in enumerate(labels.text.split("\n"))}


            # save data
            self.label_info = {
                "idx2lab": index_to_label,
                "lab2idx": label_to_index
            }
            with open(PICKLE_NAME, "wb") as f:
                pickle.dump(self.label_info, f)

        # load image and segmentation
        self.original_img = cv2.imread(IMAGE_PATH)
        self.labels, self.num_labels = self.get_grid_labels(self.original_img,
                                                            seg_width,
                                                            seg_height)
        super(ImageClf, self).__init__()


    def get_grid_labels(self, img, W=10, H=10):
        height, width, channels = img.shape[:]
        if height % H == 0:
            h_step = height // H
        else:
            h_step = (height // H) + 1
        if width % W == 0:
            w_step = width // W
        else:
            w_step = (width // W) + 1 
        
        labels = np.zeros((height, width), dtype=np.int)
        idx = 0
        for i in range(H): 
            for j in range(W):
                labels[i*h_step:min((i+1)*h_step, height),
                       j*w_step:min((j+1)*w_step, width)] = idx
                idx += 1
        num_labels = idx
        return labels, num_labels

    
    def evaluate(e):
        # fill by black
        x = np.copy(self.original_img)
        for label in range(self.num_labels):
            if label not in e:
                x[self.labels==label] = tuple([0]*3)
        # reshape
        x = cv2.resize(x, self.img_shape)
        x = cv2.cvtColor(x, cv2.COLOR_BGR2RGB)
        x = np.asarray(x)
        x = cv2.normalize(x.astype('float'), None, 0, 1, cv2.NORM_MINMAX)
        # classify
        logits = self.session.run(self.module_img,
                                  feed_dict={self.img_input: x})
        softmax = tf.nn.softmax(logits, name=None)
        probs, classes = tf.nn.top_k(softmax, k=1, sorted=True, name=None)
        prob, cls_idx = sess.run(porbs[0][0]), sess.run(classes[0][0])
        if prob > 0.2:
            return prob, self.label_info["idx2lab"][cls_idx]
        else:
            return 0.0, None


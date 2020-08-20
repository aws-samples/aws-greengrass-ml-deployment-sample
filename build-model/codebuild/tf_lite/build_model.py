#!/usr/bin/env python3

import tensorflow as tf
import numpy as np
import urllib, json 

IMG_SIZE = 224
IMAGE_SHAPE = (IMG_SIZE,IMG_SIZE,3)

def get_model():
    classifier = tf.keras.applications.MobileNetV2(input_shape=IMAGE_SHAPE,
                                               include_top=True,
                                               weights='imagenet')
    converter = tf.lite.TFLiteConverter.from_keras_model(classifier)
    tflite_model = converter.convert()
    with tf.io.gfile.GFile('model.tflite', 'wb') as f:
        f.write(tflite_model)
if __name__ == "__main__":
    # execute only if run as a script
    get_model()


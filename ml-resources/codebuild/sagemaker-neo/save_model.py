import boto3
import tensorflow as tf

IMG_SIZE = 224
IMAGE_SHAPE = (IMG_SIZE,IMG_SIZE,3)

# start clean in case of rerunning this cell
tf.keras.backend.clear_session()

classifier = tf.keras.applications.MobileNetV2(input_shape=IMAGE_SHAPE,
                                               include_top=True,
                                               weights='imagenet')
classifier.save("model.h5",save_format='h5')

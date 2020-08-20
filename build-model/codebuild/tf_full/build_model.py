import tensorflow as tf

IMG_SIZE = 224
IMAGE_SHAPE = (IMG_SIZE,IMG_SIZE,3)
classifier = tf.keras.applications.MobileNetV2(input_shape=IMAGE_SHAPE,
                                               include_top=True,
                                               weights='imagenet')
classifier.save("saved_model")
import os
import json
import logging
import urllib.request
import greengrasssdk
import numpy as np
import tensorflow as tf
import PIL.Image as Image


logger = logging.getLogger()
iot_client = greengrasssdk.client('iot-data')

# where to find the machine learning resource
MODEL_DIR = "/models/image_classifier/"
# Which topic to use for output
DEFAULT_TOPIC_RESPONSE = 'gg_ml_sample/out'
# the parameter required in the input
IMAGE_PARAM = "image"
# the DEFAULT image size for the model
IMG_SIZE = 224
# The filesystem location where to store the image on the device
IMAGE_FILE = '/tmp/image.jpg'

# load model
classifier = tf.keras.models.load_model(MODEL_DIR + 'saved_model')

# load labels and remove background class which is not used by this model
with open(MODEL_DIR + 'ImageNetLabels.txt', 'r') as file:
    labels_txt = file.read()
labels = labels_txt.split("\n")
labels = labels[1:]

print("Image classifier initialized")


def classify_image(img_path):
    """
        Returns a classification label for a given image. img_path must be a local file path.
    """
    # download and prepare image for inference as required by MobileNetV3 pretrained model
    image = Image.open(img_path).resize((IMG_SIZE, IMG_SIZE))
    # normalize pixel values
    image = np.array(image)/255.0
    # add dimension to conform to model input
    image = image[np.newaxis, ...]
    output_data = classifier.predict(image)
    logger.debug("Output data shape: %s", output_data[0].shape)
    logger.debug("Output data: %s", output_data[0])
    predicted_class = np.argmax(output_data[0], axis=-1)
    logger.debug("Predicted class: %s", predicted_class)
    return labels[predicted_class]


def lambda_handler(event, context):
    logger.info("Received request %s", event)

    if not "image" in event:
        iot_client.publish(topic=DEFAULT_TOPIC_RESPONSE,
                           payload='{"Error": "No image URL/location in payload"}')
        return
    image = event["image"]
    if not image.startswith("http"):
        iot_client.publish(topic=DEFAULT_TOPIC_RESPONSE,
                           payload='{"Error": "Image parameter is not a URL. Please specify a valid image URL."}')
        return

    urllib.request.urlretrieve(image, IMAGE_FILE)
    result = classify_image(IMAGE_FILE)

    # send response
    payload = json.dumps(
        {
            "image": event["image"],
            "function": os.getenv('MY_FUNCTION_ARN'),
            "result": result
        }
    )
    logger.debug(
        'Publishing to %s , \n payload: %s', DEFAULT_TOPIC_RESPONSE, payload)
    iot_client.publish(topic=DEFAULT_TOPIC_RESPONSE, payload=payload)
    return

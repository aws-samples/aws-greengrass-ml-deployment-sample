
import sys
import os

resourcePath = os.getenv("AWS_GG_RESOURCE_PREFIX")
python_pkg_path = os.path.join(
    resourcePath, "models/image_classifier/dependencies")
sys.path.append(python_pkg_path)

print(f'Path to ML resource: {resourcePath}')
print(f'Path to ML resource  dependencies {python_pkg_path}')

import PIL.Image as Image
import tflite_runtime.interpreter as tflite
import numpy as np
import greengrasssdk
import urllib.request
import logging
import json

logger = logging.getLogger()
iot_client = greengrasssdk.client('iot-data')


# where to find the machine learning resource
MODEL_DIR = os.path.join(resourcePath, "models/image_classifier/")
# Which topic to use for output
DEFAULT_TOPIC_RESPONSE = 'gg_ml_sample/out'
# the parameter required in the input
IMAGE_PARAM = "image"
# the DEFAULT image size for the model
IMG_SIZE = 224


# load model
interpreter = tflite.Interpreter(
    model_path=MODEL_DIR + "model.tflite")
interpreter.allocate_tensors()

# load labels and remove background class which is not used by this model
with open(MODEL_DIR + 'ImageNetLabels.txt', 'r') as file:
    labels_txt = file.read()
labels = labels_txt.split("\n")
labels = labels[1:]

logger.info("Image classifier initialized")


def classify_image(img_path):
    """
        Returns a classification label for a given image. Image can be URL or local file.
    """
    image = Image.open(img_path).resize((IMG_SIZE, IMG_SIZE))
    image = np.array(image)/255.0
    image = image[np.newaxis, ...]

    # Get input and output tensors.
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()

    # Test the model on random input data.
    #input_shape = input_details[0]['shape']
    interpreter.set_tensor(input_details[0]['index'], image.astype('float32'))
    interpreter.invoke()

    output_data = interpreter.get_tensor(output_details[0]['index'])
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

    #image_url = "http://farm4.static.flickr.com/3021/2787796908_3eeb73f06b.jpg"
    # if it is a URL try to download the image
    if image.startswith("http"):
        filename = '/tmp/image.jpg'
        urllib.request.urlretrieve(image, filename)
        image = filename

    result = classify_image(image)
    # send response
    payload = json.dumps(
        {
            "image": event["image"],
            "result": result
        }
    )
    logger.debug(
        'Publishing to %s , \n payload: %s', DEFAULT_TOPIC_RESPONSE, payload)
    iot_client.publish(topic=DEFAULT_TOPIC_RESPONSE, payload=payload)
    return

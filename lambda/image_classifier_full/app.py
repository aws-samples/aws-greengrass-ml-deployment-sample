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


# load model
classifier = tf.keras.models.load_model(MODEL_DIR +'saved_model')

# load labels and remove background class which is not used by this model
with open(MODEL_DIR + 'ImageNetLabels.txt', 'r') as file:
    labels_txt = file.read()
labels = labels_txt.split("\n")
labels = labels[1:]

print("Image classifier initialized")


def classify_image(img_path):
    """
        Returns a classification label for a given image. Image can be URL or local file.
    """
    image = Image.open(img_path).resize((IMG_SIZE, IMG_SIZE))
    image = np.array(image)/255.0
    image = image[np.newaxis, ...]
    output_data = classifier.predict(image)
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

import json
import os
import logging
import time
from datetime import datetime
import greengrasssdk


logger = logging.getLogger()
iot_client = greengrasssdk.client('iot-data')


DEFAULT_TOPIC_RESPONSE = 'gg_ml_sample/out'
IMAGE_PARAM = "image"

def lambda_handler(event, context):
    logger.info("Received request %s", event)

    image = "bla.jpg"
    # send response
    payload = json.dumps(
        {
            "image": image,
            "result": "cat"
        }
    )
    logger.debug(
        'Publishing to %s , \n payload: %s', DEFAULT_TOPIC_RESPONSE, payload)
    iot_client.publish(topic=DEFAULT_TOPIC_RESPONSE, payload=payload)
    return


print("Tag Quality analyzer starting")

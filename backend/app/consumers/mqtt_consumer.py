"""
MQTT Consumer - Subscribes to IoT telemetry and stores in Redis
"""
import sys
sys.path.insert(0, '/app')

import paho.mqtt.client as mqtt
import json
import logging
import redis
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
MQTT_BROKER = os.getenv("MQTT_BROKER", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))
REGION = os.getenv("REGION", "region1")

# Connect to Redis
redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

device_count = 0

def on_connect(client, userdata, flags, rc):
    """Callback when connected to MQTT broker"""
    logger.info(f"Connected to MQTT broker with result code {rc}")
    client.subscribe("og/field/#")
    logger.info("Subscribed to og/field/#")

def on_message(client, userdata, msg):
    """Callback when message received"""
    global device_count
    try:
        payload = json.loads(msg.payload.decode())

        # Increment device counter
        device_count += 1
        redis_client.set("stats:active_devices", device_count)

        if device_count % 10000 == 0:
            logger.info(f"Processed {device_count} device messages, stored count in Redis")

    except Exception as e:
        logger.error(f"Error processing message: {e}")

def start_consumer():
    """Start MQTT consumer"""
    client = mqtt.Client(client_id=f"backend_consumer_{REGION}")
    client.on_connect = on_connect
    client.on_message = on_message

    logger.info(f"Connecting to MQTT broker at {MQTT_BROKER}:{MQTT_PORT}")
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_forever()

if __name__ == "__main__":
    start_consumer()

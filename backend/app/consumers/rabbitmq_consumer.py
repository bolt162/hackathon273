"""
RabbitMQ Consumer - Subscribes to user activity and stores in Redis
"""
import sys
sys.path.insert(0, '/app')

import pika
import json
import logging
import redis
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", 5672))
RABBITMQ_USER = os.getenv("RABBITMQ_USER", "admin")
RABBITMQ_PASS = os.getenv("RABBITMQ_PASS", "admin123")

# Connect to Redis
redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

def callback(ch, method, properties, body):
    """Callback when message received"""
    try:
        data = json.loads(body.decode())

        # Store user activity metrics
        metrics = data.get('metrics', {})
        redis_client.set("stats:active_users", metrics.get('active_users', 0))
        redis_client.set("stats:active_connections", metrics.get('active_connections', 0))
        redis_client.set("latest:user_activity", json.dumps(metrics))
        redis_client.set("latest:user_activity_full", json.dumps(data))

        logger.info(f"Updated user stats: {metrics.get('active_users', 0)} users, {metrics.get('active_connections', 0)} connections")

    except Exception as e:
        logger.error(f"Error processing message: {e}")

def start_consumer():
    """Start RabbitMQ consumer"""
    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
    parameters = pika.ConnectionParameters(
        host=RABBITMQ_HOST,
        port=RABBITMQ_PORT,
        credentials=credentials,
        heartbeat=600,
        blocked_connection_timeout=300
    )

    logger.info(f"Connecting to RabbitMQ at {RABBITMQ_HOST}:{RABBITMQ_PORT}")

    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()

    channel.queue_declare(queue='webapp_active_users', durable=True)
    channel.basic_consume(queue='webapp_active_users', on_message_callback=callback, auto_ack=True)

    logger.info("Started consuming from webapp_active_users queue")
    channel.start_consuming()

if __name__ == "__main__":
    start_consumer()

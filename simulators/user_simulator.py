"""
User Activity Simulator
Simulates active users and publishes to RabbitMQ
"""
import asyncio
import json
import random
import os
from datetime import datetime, timezone, timedelta
import pika
import time

REGIONS = ["US-WEST", "US-EAST", "US-CENTRAL", "EU-WEST", "EU-CENTRAL", "APAC", "SA-EAST"]
SITES = ["SFO-WEB-01", "NYC-WEB-01", "CHI-WEB-01", "LON-WEB-01", "FRA-WEB-01", "SIN-WEB-01", "SAO-WEB-01"]

FIRST_NAMES = ["alex", "maria", "chen", "john", "sarah", "raj", "emma", "carlos", "yuki", "omar"]
LAST_NAMES = ["smith", "garcia", "wang", "johnson", "brown", "patel", "davis", "rodriguez", "tanaka", "kim"]


class UserSimulator:
    def __init__(self, rabbitmq_host: str, rabbitmq_port: int, rabbitmq_user: str, rabbitmq_pass: str):
        self.rabbitmq_host = rabbitmq_host
        self.rabbitmq_port = rabbitmq_port
        self.rabbitmq_user = rabbitmq_user
        self.rabbitmq_pass = rabbitmq_pass
        self.connection = None
        self.channel = None
        self.active_users = []
        self.user_id_counter = 10000
        self.publish_count = 0

    def connect(self):
        """Connect to RabbitMQ with retry logic"""
        max_retries = 10
        for attempt in range(max_retries):
            try:
                credentials = pika.PlainCredentials(self.rabbitmq_user, self.rabbitmq_pass)
                parameters = pika.ConnectionParameters(
                    host=self.rabbitmq_host,
                    port=self.rabbitmq_port,
                    credentials=credentials,
                    heartbeat=600,
                    blocked_connection_timeout=300
                )
                self.connection = pika.BlockingConnection(parameters)
                self.channel = self.connection.channel()

                # Declare queue
                self.channel.queue_declare(queue='webapp_active_users', durable=True)

                print(f"Connected to RabbitMQ at {self.rabbitmq_host}:{self.rabbitmq_port}")
                return True

            except Exception as e:
                print(f"Connection attempt {attempt + 1}/{max_retries} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(5)
                else:
                    print("Failed to connect to RabbitMQ")
                    return False

    def generate_user(self) -> dict:
        """Generate a new user session"""
        self.user_id_counter += 1
        username = f"{random.choice(FIRST_NAMES)}_{random.choice(LAST_NAMES)[0]}"

        user = {
            "user_id": f"USR-{self.user_id_counter:05d}",
            "username": username,
            "session_id": f"SESS-{random.randint(100000, 999999):06X}",
            "login_time": (datetime.now(timezone.utc) - timedelta(minutes=random.randint(1, 120))).isoformat(),
            "ip_address": f"{random.randint(10, 192)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)}",
            "region": random.choice(REGIONS),
            "connection_status": random.choices(["active", "idle"], weights=[0.7, 0.3])[0]
        }
        return user

    def update_active_users(self, target_count: int):
        """Update the active users list with some churn"""
        # Remove some users (logout)
        if len(self.active_users) > 0:
            logout_count = random.randint(0, min(10, len(self.active_users) // 10))
            for _ in range(logout_count):
                if self.active_users:
                    self.active_users.pop(random.randint(0, len(self.active_users) - 1))

        # Add new users (login)
        while len(self.active_users) < target_count:
            self.active_users.append(self.generate_user())

        # Update connection status for existing users
        for user in self.active_users:
            if random.random() < 0.1:  # 10% chance to change status
                user["connection_status"] = random.choices(["active", "idle"], weights=[0.7, 0.3])[0]

    def generate_message(self) -> dict:
        """Generate a user activity message"""
        site_id = random.choice(SITES)

        # Calculate metrics based on active users
        active_count = sum(1 for u in self.active_users if u["connection_status"] == "active")

        message = {
            "message_id": f"MSG-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{self.publish_count:05d}",
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "site_id": site_id,
            "metrics": {
                "active_users": len(self.active_users),
                "active_connections": active_count,
                "server_cpu_pct": round(random.uniform(30.0, 90.0), 1),
                "server_memory_gb": round(random.uniform(10.0, 28.0), 1),
                "average_latency_ms": round(random.uniform(20.0, 150.0), 1)
            },
            "active_users_list": self.active_users[:50],  # Send first 50 for brevity
            "queue_metadata": {
                "topic": "webapp/active_users",
                "producer": "UserSimEngine",
                "priority": "normal",
                "retries": 0
            }
        }

        return message

    def publish_message(self, message: dict):
        """Publish message to RabbitMQ"""
        try:
            self.channel.basic_publish(
                exchange='',
                routing_key='webapp_active_users',
                body=json.dumps(message),
                properties=pika.BasicProperties(
                    delivery_mode=2,  # Make message persistent
                    content_type='application/json'
                )
            )
            self.publish_count += 1
            return True
        except Exception as e:
            print(f"Error publishing message: {e}")
            # Try to reconnect
            self.connect()
            return False

    async def run_simulation(self, interval_seconds: int = 5):
        """Run the user activity simulation"""
        if not self.connect():
            return

        print(f"\nStarting user activity simulation")
        print(f"Publishing every {interval_seconds} seconds\n")

        cycle = 0
        try:
            while True:
                cycle += 1

                # Simulate varying user count (200-500 users)
                target_users = random.randint(200, 500)
                self.update_active_users(target_users)

                # Generate and publish message
                message = self.generate_message()
                if self.publish_message(message):
                    print(f"Cycle {cycle}: Published activity - "
                          f"{message['metrics']['active_users']} users, "
                          f"{message['metrics']['active_connections']} active connections, "
                          f"CPU: {message['metrics']['server_cpu_pct']}%, "
                          f"Site: {message['site_id']}")

                await asyncio.sleep(interval_seconds)

        except KeyboardInterrupt:
            print("\n\nSimulation stopped by user")
        finally:
            if self.connection and not self.connection.is_closed:
                self.connection.close()
            print(f"Total messages published: {self.publish_count}")


async def main():
    rabbitmq_host = os.getenv("RABBITMQ_HOST", "localhost")
    rabbitmq_port = int(os.getenv("RABBITMQ_PORT", 5672))
    rabbitmq_user = os.getenv("RABBITMQ_USER", "admin")
    rabbitmq_pass = os.getenv("RABBITMQ_PASS", "admin123")
    interval = int(os.getenv("PUBLISH_INTERVAL_SECONDS", 5))

    simulator = UserSimulator(rabbitmq_host, rabbitmq_port, rabbitmq_user, rabbitmq_pass)
    await simulator.run_simulation(interval)


if __name__ == "__main__":
    asyncio.run(main())

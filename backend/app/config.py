"""
Configuration management for the SRE backend
"""
import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Region Configuration
    REGION: str = os.getenv("REGION", "region1")

    # Redis Configuration
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", 6379))

    # MQTT Configuration
    MQTT_BROKER: str = os.getenv("MQTT_BROKER", "localhost")
    MQTT_PORT: int = int(os.getenv("MQTT_PORT", 1883))

    # RabbitMQ Configuration
    RABBITMQ_HOST: str = os.getenv("RABBITMQ_HOST", "localhost")
    RABBITMQ_PORT: int = int(os.getenv("RABBITMQ_PORT", 5672))
    RABBITMQ_USER: str = os.getenv("RABBITMQ_USER", "admin")
    RABBITMQ_PASS: str = os.getenv("RABBITMQ_PASS", "admin123")

    # API Keys
    COHERE_API_KEY: str = os.getenv("COHERE_API_KEY", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")

    # Data paths
    DATA_PATH: str = os.getenv("DATA_PATH", "/data")

    # Application version
    APP_VERSION: str = f"v1.0.0057_{os.getenv('REGION', 'region1')}"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

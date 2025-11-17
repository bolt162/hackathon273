"""
Image embedding service using Cohere API
"""
import cohere
import base64
import os
from typing import List, Dict, Optional
from PIL import Image
import io
import logging
from app.config import settings
from app.services.redis_service import redis_service

logger = logging.getLogger(__name__)


class EmbeddingService:
    def __init__(self):
        self.cohere_client = None
        self.use_cohere = False

        if settings.COHERE_API_KEY:
            try:
                self.cohere_client = cohere.Client(settings.COHERE_API_KEY)
                self.use_cohere = True
                logger.info("Cohere client initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize Cohere: {e}")

    def generate_text_embedding(self, text: str) -> Optional[List[float]]:
        """Generate embedding for text"""
        if not self.use_cohere:
            # Return a dummy embedding if Cohere is not available
            logger.warning("Using dummy embeddings - Cohere API key not configured")
            return [0.1] * 1024

        try:
            response = self.cohere_client.embed(
                texts=[text],
                model='embed-english-v3.0',
                input_type='search_document'
            )
            return response.embeddings[0]
        except Exception as e:
            logger.error(f"Error generating text embedding: {e}")
            return None

    def generate_image_description(self, image_path: str) -> str:
        """
        Generate a textual description of an image
        For demo purposes, we'll use predefined descriptions based on image type
        In production, you'd use a vision model like GPT-4V or Cohere's multimodal model
        """
        try:
            # Extract device type from path
            if "Turbine" in image_path:
                descriptions = [
                    "Industrial turbine facility with large rotating equipment and control panels",
                    "Turbine installation site with engineers wearing hard hats inspecting equipment",
                    "Gas turbine power generation unit with monitoring systems and safety equipment"
                ]
            elif "ThermalEngine" in image_path:
                descriptions = [
                    "Thermal engine test facility with technicians monitoring temperature gauges",
                    "Industrial thermal power unit with workers in protective gear",
                    "Engine testing bay with engineers analyzing performance metrics"
                ]
            elif "ElectricalRotor" in image_path or "Electrical Rotor" in image_path:
                descriptions = [
                    "Electrical rotor assembly area with maintenance crew wearing safety helmets",
                    "High voltage rotor system with engineers conducting inspections",
                    "Motor control center with electrical engineers reviewing schematics"
                ]
            elif "ConnectedDevice" in image_path:
                descriptions = [
                    "Oil and gas wellhead site with connected IoT sensors and monitoring equipment",
                    "Field operations with workers installing pressure monitoring devices",
                    "Remote oil field with technicians wearing hard hats checking equipment"
                ]
            else:
                descriptions = ["Industrial equipment installation site"]

            # Use a hash of the filename to consistently return the same description
            import hashlib
            hash_val = int(hashlib.md5(image_path.encode()).hexdigest(), 16)
            return descriptions[hash_val % len(descriptions)]

        except Exception as e:
            logger.error(f"Error generating image description: {e}")
            return "Industrial site image"

    def process_image(self, image_path: str, site_id: str, device_type: str) -> Dict:
        """Process an image and store its embedding"""
        try:
            # Generate description
            description = self.generate_image_description(image_path)

            # Generate embedding from description
            embedding = self.generate_text_embedding(description)

            if embedding:
                # Store in Redis
                metadata = {
                    "image_path": image_path,
                    "site_id": site_id,
                    "device_type": device_type,
                    "description": description
                }

                key = f"{site_id}_{device_type}_{os.path.basename(image_path)}"
                redis_service.store_embedding(key, embedding, metadata)

                logger.info(f"Processed image: {image_path} -> {key}")
                return {
                    "key": key,
                    "description": description,
                    "embedding_size": len(embedding)
                }

            return None

        except Exception as e:
            logger.error(f"Error processing image {image_path}: {e}")
            return None

    def search_images(self, query: str, top_k: int = 5) -> List[Dict]:
        """Search for images using natural language query"""
        try:
            # Generate embedding for query
            query_embedding = self.generate_text_embedding(query)

            if not query_embedding:
                return []

            # Search in Redis
            results = redis_service.search_embeddings(query_embedding, top_k)

            return results

        except Exception as e:
            logger.error(f"Error searching images: {e}")
            return []

    def initialize_embeddings(self, data_path: str = "/data"):
        """Initialize embeddings for all images in the data directory"""
        try:
            image_folders = {
                "TurbineImages": "turbine",
                "ThermalEngines": "thermal_engine",
                "ElectricalRotors": "electrical_rotor",
                "OilAndGas": "connected_device"
            }

            site_mapping = {
                "turbine": "WY-ALPHA",
                "thermal_engine": "TX-EAGLE",
                "electrical_rotor": "NM-SAGE",
                "connected_device": "ND-RAVEN"
            }

            processed_count = 0

            for folder, device_type in image_folders.items():
                folder_path = os.path.join(data_path, folder)
                if os.path.exists(folder_path):
                    for filename in os.listdir(folder_path):
                        if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                            image_path = os.path.join(folder_path, filename)
                            site_id = site_mapping.get(device_type, "UNKNOWN")

                            result = self.process_image(image_path, site_id, device_type)
                            if result:
                                processed_count += 1

            logger.info(f"Initialized {processed_count} image embeddings")
            return processed_count

        except Exception as e:
            logger.error(f"Error initializing embeddings: {e}")
            return 0


# Singleton instance
embedding_service = EmbeddingService()

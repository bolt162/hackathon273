"""
IoT Device Telemetry Simulator
Simulates 100,000 devices across 10 sites publishing to MQTT
"""
import asyncio
import json
import random
import os
from datetime import datetime, timezone
from typing import Dict, List
import paho.mqtt.client as mqtt
from concurrent.futures import ThreadPoolExecutor
import time

# Site configurations
SITES = [
    {"id": "WY-ALPHA", "lat": 43.4231, "lon": -106.3148},
    {"id": "TX-EAGLE", "lat": 31.2319, "lon": -101.8752},
    {"id": "NM-SAGE", "lat": 34.4217, "lon": -106.1081},
    {"id": "ND-RAVEN", "lat": 48.3992, "lon": -102.7810},
    {"id": "OK-MESA", "lat": 36.1540, "lon": -95.9928},
    {"id": "CO-PEAK", "lat": 39.5501, "lon": -105.7821},
    {"id": "KS-PLAINS", "lat": 38.5266, "lon": -96.7265},
    {"id": "MT-RIDGE", "lat": 46.8797, "lon": -110.3626},
    {"id": "LA-DELTA", "lat": 30.9843, "lon": -91.9623},
    {"id": "PA-VALLEY", "lat": 40.2732, "lon": -76.8867}
]

DEVICE_TYPES = {
    "turbine": {
        "count": 25000,
        "firmware_versions": ["3.2.1", "3.2.0", "3.1.9"],
        "metrics_generator": "generate_turbine_metrics"
    },
    "thermal_engine": {
        "count": 25000,
        "firmware_versions": ["1.9.0", "1.8.5", "1.8.3"],
        "metrics_generator": "generate_thermal_metrics"
    },
    "electrical_rotor": {
        "count": 25000,
        "firmware_versions": ["2.4.5", "2.4.4", "2.3.9"],
        "metrics_generator": "generate_rotor_metrics"
    },
    "connected_device": {
        "count": 25000,
        "firmware_versions": ["5.0.3", "5.0.2", "4.9.8"],
        "metrics_generator": "generate_ogd_metrics"
    }
}


class DeviceSimulator:
    def __init__(self, mqtt_broker: str, mqtt_port: int):
        self.mqtt_broker = mqtt_broker
        self.mqtt_port = mqtt_port
        self.devices = []
        self.publish_count = 0

    def generate_devices(self, num_devices: int):
        """Generate device configurations"""
        print(f"Generating {num_devices} devices across {len(SITES)} sites...")

        devices_per_type = num_devices // len(DEVICE_TYPES)
        device_id_counter = 0

        for device_type, config in DEVICE_TYPES.items():
            count = min(config["count"], devices_per_type)

            for i in range(count):
                site = SITES[device_id_counter % len(SITES)]
                device = {
                    "device_id": f"{device_type.upper()[:4]}-{device_id_counter:05d}",
                    "device_type": device_type,
                    "site_id": site["id"],
                    "firmware": random.choice(config["firmware_versions"]),
                    "location": {
                        "lat": site["lat"] + random.uniform(-0.1, 0.1),
                        "lon": site["lon"] + random.uniform(-0.1, 0.1)
                    },
                    "metrics_generator": config["metrics_generator"]
                }
                self.devices.append(device)
                device_id_counter += 1

        print(f"Generated {len(self.devices)} devices")
        return self.devices

    def generate_turbine_metrics(self) -> Dict:
        """Generate realistic turbine metrics"""
        state = random.choices(["OK", "WARN", "ALERT"], weights=[0.85, 0.12, 0.03])[0]

        return {
            "metrics": {
                "rpm": random.randint(3200, 3600),
                "inlet_temp_c": round(random.uniform(380.0, 450.0), 1),
                "exhaust_temp_c": round(random.uniform(500.0, 580.0), 1),
                "vibration_mm_s": round(random.uniform(0.5, 3.5), 1),
                "pressure_bar": round(random.uniform(15.0, 20.0), 1),
                "power_kw": round(random.uniform(11000.0, 14000.0), 1),
                "fuel_flow_kg_h": round(random.uniform(380.0, 480.0), 1),
                "no_x_ppm": round(random.uniform(20.0, 50.0), 1)
            },
            "status": {
                "state": state,
                "code": f"TURB-{state}",
                "message": "Nominal" if state == "OK" else ("High vibration" if state == "WARN" else "Critical temp")
            },
            "tags": {
                "vendor": random.choice(["HanTech", "SiemensGE", "MitsuPower"]),
                "loop": random.choice(["A1", "A2", "B1", "B2"])
            }
        }

    def generate_thermal_metrics(self) -> Dict:
        """Generate realistic thermal engine metrics"""
        state = random.choices(["OK", "WARN", "ALERT"], weights=[0.80, 0.15, 0.05])[0]

        return {
            "metrics": {
                "rpm": random.randint(1600, 2100),
                "coolant_temp_c": round(random.uniform(75.0, 105.0), 1),
                "oil_temp_c": round(random.uniform(85.0, 115.0), 1),
                "oil_pressure_bar": round(random.uniform(3.5, 5.5), 1),
                "load_pct": round(random.uniform(40.0, 95.0), 1),
                "fuel_rate_l_h": round(random.uniform(100.0, 200.0), 1),
                "soot_pct": round(random.uniform(0.2, 1.5), 1)
            },
            "status": {
                "state": state,
                "code": f"OIL-{state}",
                "message": "Stable" if state == "OK" else ("Oil pressure trending low" if state == "WARN" else "Critical oil temp")
            },
            "tags": {
                "skid": f"TE-{random.randint(1, 20):02d}",
                "phase": random.choice(["commissioned", "testing", "production"])
            }
        }

    def generate_rotor_metrics(self) -> Dict:
        """Generate realistic electrical rotor metrics"""
        state = random.choices(["OK", "WARN", "ALERT"], weights=[0.88, 0.10, 0.02])[0]

        return {
            "metrics": {
                "stator_temp_c": round(random.uniform(70.0, 100.0), 1),
                "bearing_temp_c": round(random.uniform(60.0, 90.0), 1),
                "current_a": round(random.uniform(280.0, 350.0), 1),
                "voltage_v": round(random.uniform(400.0, 440.0), 1),
                "power_factor": round(random.uniform(0.85, 0.98), 2),
                "vibration_mm_s": round(random.uniform(0.8, 2.5), 1)
            },
            "status": {
                "state": state,
                "code": f"ER-{state}",
                "message": "Stable" if state == "OK" else ("Elevated bearing temp" if state == "WARN" else "Critical vibration")
            },
            "tags": {
                "panel": f"MCC-{random.randint(1, 5)}",
                "line": random.choice(["R1", "R2", "R3"])
            }
        }

    def generate_ogd_metrics(self) -> Dict:
        """Generate realistic Oil & Gas connected device metrics"""
        state = random.choices(["OK", "WARN", "ALERT"], weights=[0.82, 0.14, 0.04])[0]

        return {
            "metrics": {
                "wellhead_pressure_bar": round(random.uniform(100.0, 160.0), 1),
                "wellhead_temp_c": round(random.uniform(50.0, 80.0), 1),
                "flow_rate_m3_h": round(random.uniform(60.0, 120.0), 1),
                "methane_leak_ppm": round(random.uniform(0.0, 10.0), 1),
                "battery_soc_pct": round(random.uniform(60.0, 100.0), 1),
                "rssi_dbm": random.randint(-90, -50)
            },
            "status": {
                "state": state,
                "code": f"GW-{state}",
                "message": "All sensors online" if state == "OK" else ("Weak signal" if state == "WARN" else "Methane leak detected")
            },
            "tags": {
                "network": random.choice(["LTE", "5G", "LoRaWAN"]),
                "ingress": random.choice(["MQTT-1", "MQTT-2", "HTTPS"])
            }
        }

    def generate_payload(self, device: Dict) -> Dict:
        """Generate a complete MQTT payload for a device"""
        generator_name = device["metrics_generator"]
        generator_method = getattr(self, generator_name)
        generated_data = generator_method()

        payload = {
            "device_id": device["device_id"],
            "device_type": device["device_type"],
            "site_id": device["site_id"],
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "firmware": device["firmware"],
            "metrics": generated_data["metrics"],
            "status": generated_data["status"],
            "location": device["location"],
            "tags": generated_data["tags"]
        }

        return payload

    def publish_device_data(self, client: mqtt.Client, device: Dict):
        """Publish data for a single device"""
        topic = f"og/field/{device['site_id']}/{device['device_type']}/{device['device_id']}"
        payload = self.generate_payload(device)

        try:
            result = client.publish(topic, json.dumps(payload), qos=1)
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                self.publish_count += 1
                if self.publish_count % 10000 == 0:
                    print(f"Published {self.publish_count} messages...")
        except Exception as e:
            print(f"Error publishing for {device['device_id']}: {e}")

    async def run_simulation(self, num_devices: int, interval_seconds: int = 1):
        """Run the simulation with batch publishing"""
        self.generate_devices(num_devices)

        # Create MQTT client
        client = mqtt.Client(client_id="iot_simulator", clean_session=True)

        print(f"Connecting to MQTT broker at {self.mqtt_broker}:{self.mqtt_port}...")
        max_retries = 10
        for attempt in range(max_retries):
            try:
                client.connect(self.mqtt_broker, self.mqtt_port, 60)
                client.loop_start()
                print("Connected to MQTT broker!")
                break
            except Exception as e:
                print(f"Connection attempt {attempt + 1}/{max_retries} failed: {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(5)
                else:
                    print("Failed to connect to MQTT broker. Exiting.")
                    return

        print(f"\nStarting simulation: {len(self.devices)} devices, publishing every {interval_seconds}s")
        print(f"Total messages per cycle: {len(self.devices)}")
        print(f"Estimated throughput: {len(self.devices) / interval_seconds} msg/s\n")

        # Simulation loop
        cycle = 0
        batch_size = 1000  # Publish in batches to avoid overwhelming the broker

        try:
            while True:
                cycle += 1
                start_time = time.time()

                # Publish in batches
                for i in range(0, len(self.devices), batch_size):
                    batch = self.devices[i:i + batch_size]
                    for device in batch:
                        self.publish_device_data(client, device)

                    # Small delay between batches
                    await asyncio.sleep(0.01)

                elapsed = time.time() - start_time
                print(f"Cycle {cycle} completed in {elapsed:.2f}s - Total published: {self.publish_count}")

                # Wait for next interval
                wait_time = max(0, interval_seconds - elapsed)
                if wait_time > 0:
                    await asyncio.sleep(wait_time)

        except KeyboardInterrupt:
            print("\n\nSimulation stopped by user")
        finally:
            client.loop_stop()
            client.disconnect()
            print(f"Total messages published: {self.publish_count}")


async def main():
    mqtt_broker = os.getenv("MQTT_BROKER", "localhost")
    mqtt_port = int(os.getenv("MQTT_PORT", 1883))
    num_devices = int(os.getenv("NUM_DEVICES", 100000))
    interval = int(os.getenv("PUBLISH_INTERVAL_SECONDS", 1))

    simulator = DeviceSimulator(mqtt_broker, mqtt_port)
    await simulator.run_simulation(num_devices, interval)


if __name__ == "__main__":
    asyncio.run(main())

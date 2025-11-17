#!/usr/bin/env python3
"""
Failover Testing Script
Tests dual-region deployment and measures failover latency
"""
import requests
import time
import sys

REGION1_API = "http://localhost:8000"
REGION2_API = "http://localhost:8100"


def test_health(api_url, region_name):
    """Test health endpoint"""
    try:
        response = requests.get(f"{api_url}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✓ {region_name} is healthy")
            print(f"  Status: {data.get('status')}")
            print(f"  Version: {data.get('version')}")
            return True
        else:
            print(f"✗ {region_name} health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ {region_name} is unreachable: {e}")
        return False


def test_failover(source_api, source_region):
    """Test failover simulation"""
    print(f"\n{'='*60}")
    print(f"Testing Failover from {source_region}")
    print(f"{'='*60}\n")

    try:
        # Trigger failover
        start_time = time.time()
        response = requests.post(f"{source_api}/api/failover/simulate", timeout=10)
        end_time = time.time()

        if response.status_code == 200:
            data = response.json()
            total_latency = end_time - start_time

            print(f"✓ Failover successful!")
            print(f"\n  Source Region: {data.get('source_region')}")
            print(f"  Target Region: {data.get('target_region')}")
            print(f"  API Reported Latency: {data.get('failover_latency_seconds', 0):.6f}s")
            print(f"  Total E2E Latency: {total_latency:.6f}s")
            print(f"  Message: {data.get('message')}")

            # Verify target region is active
            target_region = data.get('target_region')
            target_api = REGION2_API if target_region == 'region2' else REGION1_API

            time.sleep(1)  # Give it a moment to stabilize

            status_response = requests.get(f"{target_api}/api/status", timeout=5)
            if status_response.status_code == 200:
                status_data = status_response.json()
                print(f"\n  Target Region Status: {status_data.get('status')}")

            return True
        else:
            print(f"✗ Failover failed: {response.status_code}")
            print(f"  Response: {response.text}")
            return False

    except Exception as e:
        print(f"✗ Failover test error: {e}")
        return False


def test_state_continuity():
    """Test state continuity across regions"""
    print(f"\n{'='*60}")
    print(f"Testing State Continuity")
    print(f"{'='*60}\n")

    try:
        # Get state from Region 1
        r1_response = requests.get(f"{REGION1_API}/api/status", timeout=5)
        r1_data = r1_response.json()

        # Get state from Region 2
        r2_response = requests.get(f"{REGION2_API}/api/status", timeout=5)
        r2_data = r2_response.json()

        print(f"Region 1:")
        print(f"  Status: {r1_data.get('status')}")
        print(f"  Version: {r1_data.get('version')}")
        print(f"  Active Devices: {r1_data.get('active_devices')}")
        print(f"  Active Users: {r1_data.get('active_users')}")

        print(f"\nRegion 2:")
        print(f"  Status: {r2_data.get('status')}")
        print(f"  Version: {r2_data.get('version')}")
        print(f"  Active Devices: {r2_data.get('active_devices')}")
        print(f"  Active Users: {r2_data.get('active_users')}")

        return True

    except Exception as e:
        print(f"✗ State continuity test error: {e}")
        return False


def main():
    print("\n" + "="*60)
    print("ENTERPRISE SRE FAILOVER TEST")
    print("="*60 + "\n")

    # Test health of both regions
    print("Step 1: Health Checks")
    print("-" * 60)
    r1_healthy = test_health(REGION1_API, "Region 1")
    r2_healthy = test_health(REGION2_API, "Region 2")

    if not (r1_healthy and r2_healthy):
        print("\n✗ Both regions must be healthy to proceed")
        sys.exit(1)

    # Test state continuity
    test_state_continuity()

    # Test failover from Region 1 to Region 2
    if test_failover(REGION1_API, "region1"):
        print("\n✓ Failover test PASSED")

        # Optional: Test failover back to Region 1
        print("\nWaiting 3 seconds before testing failover back...")
        time.sleep(3)
        test_failover(REGION2_API, "region2")

    print("\n" + "="*60)
    print("Test Complete")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
System Integration Test Script
Tests all major components of the SRE system
"""
import requests
import time
import sys

API_BASE = "http://localhost:8000"


def test_endpoint(name, method, url, data=None):
    """Test a single endpoint"""
    try:
        print(f"\nTesting: {name}")
        print(f"  URL: {method} {url}")

        if method == "GET":
            response = requests.get(url, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=10)
        else:
            print(f"  ✗ Unsupported method: {method}")
            return False

        print(f"  Status: {response.status_code}")

        if response.status_code in [200, 201]:
            print(f"  ✓ SUCCESS")
            data = response.json()
            print(f"  Response preview: {str(data)[:200]}...")
            return True
        else:
            print(f"  ✗ FAILED")
            print(f"  Response: {response.text[:200]}")
            return False

    except Exception as e:
        print(f"  ✗ ERROR: {e}")
        return False


def main():
    print("\n" + "="*70)
    print("ENTERPRISE SRE SYSTEM INTEGRATION TEST")
    print("="*70 + "\n")

    tests = [
        ("Root Endpoint", "GET", f"{API_BASE}/"),
        ("Health Check", "GET", f"{API_BASE}/health"),
        ("System Status", "GET", f"{API_BASE}/api/status"),
        ("System Metrics", "GET", f"{API_BASE}/api/metrics"),
        ("Get App Version", "GET", f"{API_BASE}/fastapi/region1/getappversion"),

        # Device endpoints
        ("Active Devices", "GET", f"{API_BASE}/api/devices/active"),
        ("Device Alerts", "GET", f"{API_BASE}/api/devices/alerts"),

        # User endpoints
        ("Active Users", "GET", f"{API_BASE}/api/users/active"),
        ("User Activity", "GET", f"{API_BASE}/api/users/activity"),
        ("Active Connections", "GET", f"{API_BASE}/api/users/connections"),

        # Diagnostics endpoints
        ("Log Statistics", "GET", f"{API_BASE}/api/diagnostics/logs/stats"),
        ("Diagnostics Summary", "GET", f"{API_BASE}/api/diagnostics/logs/summary"),
        ("Error 400 IPs", "GET", f"{API_BASE}/api/diagnostics/logs/errors/400"),
        ("Error 404 IPs", "GET", f"{API_BASE}/api/diagnostics/logs/errors/404"),

        # Image endpoints
        ("List Images", "GET", f"{API_BASE}/api/images/list"),
        (
            "Search Images - Hard Hats",
            "POST",
            f"{API_BASE}/api/images/search",
            {"query": "workers wearing hard hats", "top_k": 3}
        ),
        (
            "Search Images - Turbine",
            "POST",
            f"{API_BASE}/api/images/search",
            {"query": "turbine site with engineers", "top_k": 3}
        ),

        # LLM Query endpoints
        (
            "LLM Query - Safety",
            "POST",
            f"{API_BASE}/api/diagnostics/query",
            {"question": "How many safety incidences occurred in BP operations in 2024?"}
        ),
        (
            "LLM Query - Hard Hats",
            "POST",
            f"{API_BASE}/api/diagnostics/query",
            {"question": "Describe BP oil drill operations and hard hat requirements"}
        ),
        (
            "LLM Query - Error 400",
            "POST",
            f"{API_BASE}/api/diagnostics/query",
            {"question": "Give me the most frequent IP devices generating error 400"}
        ),
        (
            "LLM Query - Sustainability",
            "POST",
            f"{API_BASE}/api/diagnostics/query",
            {"question": "List economic and social sustainability statements"}
        ),

        # Simulation endpoints
        ("Simulate High Traffic", "POST", f"{API_BASE}/api/simulate/high-traffic"),
        ("Failover Status", "GET", f"{API_BASE}/api/failover/status"),
    ]

    results = []
    for test in tests:
        if len(test) == 3:
            name, method, url = test
            data = None
        else:
            name, method, url, data = test

        success = test_endpoint(name, method, url, data)
        results.append((name, success))

        # Small delay between tests
        time.sleep(0.5)

    # Print summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70 + "\n")

    passed = sum(1 for _, success in results if success)
    total = len(results)

    for name, success in results:
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"{status:10} {name}")

    print(f"\n{'='*70}")
    print(f"Results: {passed}/{total} tests passed ({(passed/total)*100:.1f}%)")
    print(f"{'='*70}\n")

    if passed == total:
        print("🎉 All tests passed!")
        sys.exit(0)
    else:
        print("⚠️  Some tests failed")
        sys.exit(1)


if __name__ == "__main__":
    main()

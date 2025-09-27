#!/usr/bin/env python3
"""Simple Docker container test that properly exits."""

import subprocess
import sys
import time

import requests


def run_cmd(cmd, timeout=30):
    """Run command with timeout."""
    try:
        result = subprocess.run(cmd, shell=True, timeout=timeout, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Command timed out"


def test_docker_container():
    """Test Docker container APIs."""
    print("🐳 Testing Docker Container - GitHub Native Structure")
    print("=" * 50)

    # Build Docker image
    print("📦 Building Docker image...")
    success, stdout, stderr = run_cmd("docker build -f docker/Dockerfile -t sth-test .", 120)
    if not success:
        print(f"❌ Build failed: {stderr}")
        return False
    print("✅ Docker image built")

    # Stop any existing container
    run_cmd("docker stop sth-test-container 2>/dev/null", 10)
    run_cmd("docker rm sth-test-container 2>/dev/null", 10)

    # Run container
    print("🚀 Starting container...")
    success, stdout, stderr = run_cmd(
        "docker run -d --name sth-test-container -p 8005:8000 sth-test", 30
    )
    if not success:
        print(f"❌ Container start failed: {stderr}")
        return False
    print("✅ Container started on port 8005")

    # Wait for startup
    print("⏳ Waiting for container startup...")
    time.sleep(15)

    # Test APIs
    print("🧪 Testing APIs...")
    base_url = "http://localhost:8005"

    # Detect API style (versioned vs unversioned) from root endpoint
    try:
        root_resp = requests.get(f"{base_url}/", timeout=10)
        root_data = root_resp.json() if root_resp.status_code == 200 else {}
        endpoints = root_data.get("endpoints", {}) if isinstance(root_data, dict) else {}
        health_path = endpoints.get("health", "/healthz")
        trending_path = endpoints.get("trending", "/trending?provider=mock&count=2")
        hashtag_template = endpoints.get("hashtag", "/hashtag/{tag}?provider=mock&count=1")
        providers_path = endpoints.get("providers", "/providers")
        compliance_path = endpoints.get("compliance", "/compliance")
        # Determine prefix for cache endpoints
        prefix = "/api/v1" if str(health_path).startswith("/api/v1") else ""
        hashtag_path = str(hashtag_template).replace("{tag}", "viral")
    except Exception:
        print("⚠️ Could not fetch root endpoint; defaulting to non-versioned paths.")
        prefix = ""
        health_path = "/healthz"
        trending_path = "/trending?provider=mock&count=2"
        hashtag_path = "/hashtag/viral?provider=mock&count=1"
        providers_path = "/providers"
        compliance_path = "/compliance"

    tests = [
        ("Health", "GET", f"{base_url}{health_path}"),
        ("Root", "GET", f"{base_url}/"),
        ("Trending", "GET", f"{base_url}{trending_path}"),
        ("Hashtag", "GET", f"{base_url}{hashtag_path}"),
        ("Providers", "GET", f"{base_url}{providers_path}"),
        ("Compliance", "GET", f"{base_url}{compliance_path}"),
        # Cache endpoints (work for both versioned and unversioned APIs)
        ("Cache Stats", "GET", f"{base_url}{prefix}/cache/stats"),
        ("Cache Clear", "DELETE", f"{base_url}{prefix}/cache/clear"),
    ]

    passed = 0
    for name, method, url in tests:
        try:
            if method == "GET":
                response = requests.get(url, timeout=10)
            elif method == "DELETE":
                response = requests.delete(url, timeout=10)
            else:
                print(f"⚠️ {name}: Unsupported method {method}")
                continue

            if 200 <= response.status_code < 300:
                print(f"✅ {name}: PASS")
                passed += 1
            else:
                print(f"❌ {name}: FAIL ({response.status_code})")
        except Exception as e:
            print(f"❌ {name}: FAIL ({str(e)[:30]}...)")

    # Cleanup
    print("🧹 Cleaning up...")
    run_cmd("docker stop sth-test-container", 10)
    run_cmd("docker rm sth-test-container", 10)

    # Results
    print(f"📊 Results: {passed}/{len(tests)} tests passed")
    if passed == len(tests):
        print("🎉 ALL TESTS PASSED! Container working perfectly!")
        return True
    else:
        print("❌ Some tests failed")
        # Show container logs for debugging
        ok, out, err = run_cmd("docker logs --tail 120 sth-test-container", 15)
        print("\n=== Container Logs (last 120 lines) ===")
        if ok:
            print(out)
        else:
            print(err or "<no logs available>")
        return False


if __name__ == "__main__":
    try:
        success = test_docker_container()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted")
        run_cmd("docker stop sth-test-container 2>/dev/null", 5)
        run_cmd("docker rm sth-test-container 2>/dev/null", 5)
        sys.exit(1)
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        sys.exit(1)

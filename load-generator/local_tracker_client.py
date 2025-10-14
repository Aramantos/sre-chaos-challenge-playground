import os
import requests
import json
import time
import datetime

class LocalTrackerClient:
    def __init__(self):
        self.tracking_url = os.getenv("TRACKING_SERVICE_URL")
        self.api_key = os.getenv("LOCAL_TRACKER_API_KEY", os.getenv("API_KEY"))
        self.user_id = os.getenv("LOCAL_TRACKER_USER_ID") or os.getenv("INFLUENCER_USER")
        self.schema_version = "1.0"

        if not self.tracking_url:
            print("Warning: TRACKING_SERVICE_URL environment variable not set. Tracking will be disabled.")
        if not self.api_key:
            print("Warning: LOCAL_TRACKER_API_KEY or API_KEY environment variable not set. Tracking will be unauthenticated.")
        if not self.user_id:
            print("Warning: LOCAL_TRACKER_USER_ID or INFLUENCER_USER environment variable not set. Defaulting user_id to 'anonymous'.")
            self.user_id = "anonymous"

    def send_metrics(self, challenge_type: str, metric_name: str, metrics_data: dict, session_id: str, retries=3, backoff_factor=0.5):
        if not self.tracking_url:
            print("Tracking disabled due to missing TRACKING_SERVICE_URL.")
            return False

        headers = {
            "Content-Type": "application/json",
        }
        if self.api_key:
            headers["x-api-key"] = self.api_key

        payload = {
            "schema_version": self.schema_version,
            "userId": self.user_id,
            "challengeType": challenge_type,
            "metricName": metric_name,
            "value": metrics_data.get("value", 1), # A default value, but detailed metrics are in runDetails
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "labels": metrics_data.get("labels", {"source": "tracking_client"}),
            "runDetails": {**metrics_data, "session_id": session_id} # Detailed metrics go here
        }

        for i in range(retries):
            try:
                response = requests.post(self.tracking_url, headers=headers, json=payload)
                response.raise_for_status() # Raise an exception for HTTP errors (4xx or 5xx)
                print(f"Tracking data sent to {self.tracking_url} - Status: {response.status_code}")
                try:
                    response_json = response.json()
                    print(f"Tracking service response: {response_json}")
                except json.JSONDecodeError:
                    print(f"Tracking service responded with non-JSON: {response.text}")
                return True
            except requests.exceptions.RequestException as e:
                print(f"Attempt {i+1}/{retries}: Failed to send tracking data to {self.tracking_url}: {e}")
                if i < retries - 1:
                    time.sleep(backoff_factor * (2 ** i)) # Exponential backoff
                else:
                    print("Max retries reached. Tracking data not sent.")
        return False

# Example Usage (for testing purposes, not part of the module itself)
if __name__ == "__main__":
    # Set dummy environment variables for local testing
    os.environ["TRACKING_SERVICE_URL"] = "http://localhost:3002/api/track"
    os.environ["API_KEY"] = "test-api-key"
    os.environ["INFLUENCER_USER"] = "test-user-from-client"

    client = LocalTrackerClient()

    sample_metrics = {
        "challengeType": "example-challenge",
        "metricName": "example_metric",
        "value": 100,
        "avg_latency_ms": 250.5,
        "rps": 50,
        "error_rate": 0.01,
        "total_requests": 1000,
        "duration_s": 20,
        "labels": {"env": "dev", "test_id": "xyz"}
    }

    print("\nSending sample metrics...")
    client.send_metrics(
        challenge_type=sample_metrics["challengeType"],
        metric_name=sample_metrics["metricName"],
        metrics_data=sample_metrics
    )

    # Test with missing URL
    del os.environ["TRACKING_SERVICE_URL"]
    print("\nTesting with missing TRACKING_SERVICE_URL...")
    client_no_url = LocalTrackerClient()
    client_no_url.send_metrics("test", "test_metric", {"value": 5})

    # Restore URL for other tests if needed
    os.environ["TRACKING_SERVICE_URL"] = "http://localhost:3002/api/track"

    # Test with invalid API key (will likely fail if backend validates)
    os.environ["API_KEY"] = "invalid-key"
    print("\nTesting with invalid API_KEY...")
    client_invalid_key = LocalTrackerClient()
    client_invalid_key.send_metrics("test", "test_metric", {"value": 5})

    os.environ["API_KEY"] = "test-api-key" # Restore

    # Test with retries
    print("\nTesting with retries (assuming service is down or returns error)...")
    # To properly test retries, you'd need to simulate a failing service.
    # For now, this just demonstrates the call structure.
    client.send_metrics("retry-test", "retry_metric", {"value": 1}, retries=3)

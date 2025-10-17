#!/usr/bin/env python

import requests
import time

URL_ANVIL_URL = "http://localhost:8080"

def solve_graceful_degradation():
    """Sends requests to the url-anvil service to generate metrics for the graceful-degradation challenge."""
    print("--- Starting graceful-degradation solver ---")
    while True:
        try:
            # Get sample URLs
            response = requests.get(f"{URL_ANVIL_URL}/api/sample-urls")
            response.raise_for_status()
            urls = response.json()

            # Send a test request
            test_response = requests.post(f"{URL_ANVIL_URL}/api/test", json={"urls": urls})
            test_response.raise_for_status()

            print("Successfully sent a test request to url-anvil.")

        except requests.exceptions.RequestException as e:
            print(f"Error sending request: {e}")
        
        # Wait for a short period before sending the next request
        time.sleep(5)

if __name__ == "__main__":
    solve_graceful_degradation()

#!/usr/bin/env python

import requests
import time

URL_ANVIL_URL = "http://localhost:8080"

def solve_crash_challenge():
    """Sends requests to the url-anvil service to generate metrics for the crash-challenge."""
    print("--- Starting crash-challenge solver ---")
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
    solve_crash_challenge()

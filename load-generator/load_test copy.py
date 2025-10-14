import requests
import argparse
import time
import os
import json
import datetime

print("Script started!")

def send_tracking_data(tracking_url, api_key, influencer_user, run_details):
    """Sends load test run details to the tracking service."""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "userId": influencer_user,
        "challengeType": "load-test",
        "metricName": "load_test_run",
        "value": 1,
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "labels": {"test_type": "manual_load_test"},
        "runDetails": run_details
    }
    try:
        response = requests.post(tracking_url, headers=headers, json=payload)
        response.raise_for_status()
        print(f"Tracking data sent to {tracking_url} - Status: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Failed to send tracking data to {tracking_url}: {e}")

def send_request(url, method, payload_urls=None):
    """Sends a single HTTP request to the specified URL."""
    try:
        start_time = time.time()
        if method.upper() == 'POST':
            headers = {'Content-Type': 'application/json'}
            data = json.dumps({'urls': payload_urls})
            response = requests.post(url, headers=headers, data=data)
        else: # Default to GET
            response = requests.get(url)
        end_time = time.time()
        print(f"Request to {url} ({method}) - Status: {response.status_code}, Time: {end_time - start_time:.4f} seconds")
    except requests.exceptions.RequestException as e:
        print(f"Request to {url} ({method}) failed: {e}")

def main():
    """Main function to parse arguments and run the load test."""
    try:
        print("Entering main function.")
        parser = argparse.ArgumentParser(description="Simple load testing script.")
        parser.add_argument("url", nargs='?', default="http://url-anvil:8080", help="The URL to send requests to. Defaults to http://url-anvil:8080.")
        parser.add_argument("request_count", type=int, help="The number of requests to send.")
        parser.add_argument("--method", default=os.getenv('REQUEST_METHOD', 'GET'), help="HTTP method (GET or POST).")
        parser.add_argument("--payload-urls", default=os.getenv('PAYLOAD_URLS', ''), help="Comma-separated URLs for POST request payload.")
        
        print("Parsing arguments...")
        args = parser.parse_args()
        print(f"Arguments parsed: {args}")

        payload_urls_list = [url.strip() for url in args.payload_urls.split(',') if url.strip()]
        if not payload_urls_list and args.method.upper() == 'POST':
            print("Warning: POST method specified but no payload URLs provided. Using sample URLs.")
            payload_urls_list = ["https://example.com", "https://google.com"]

        print(f"Starting load test with {args.request_count} requests to {args.url} using {args.method} method.")

        for i in range(args.request_count):
            send_request(args.url, args.method, payload_urls_list if args.method.upper() == 'POST' else None)
            print(f"Request {i+1}/{args.request_count} sent.")
            time.sleep(0.1)

        print("Load test finished.")

        tracking_url = os.getenv("TRACKING_SERVICE_URL")
        api_key = os.getenv("API_KEY")
        influencer_user = os.getenv("INFLUENCER_USER")

        if tracking_url and api_key and influencer_user:
            print("Sending tracking data...")
            run_details = {
                "target_url": args.url,
                "request_count": args.request_count,
                "method": args.method,
                "payload_urls": payload_urls_list
            }
            send_tracking_data(tracking_url, api_key, influencer_user, run_details)
        else:
            print("Warning: TRACKING_SERVICE_URL, API_KEY, or INFLUENCER_USER not set. Skipping tracking data submission.")
    except Exception as e:
        print(f"An error occurred in main: {e}")

if __name__ == "__main__":
    print("Inside __name__ == '__main__'")
    main()

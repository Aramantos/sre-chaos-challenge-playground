import requests
import argparse
import time
import os
import json
import datetime
import uuid
from local_tracker_client import LocalTrackerClient

print("Script started!")

def get_session_id():
    session_id_file = ".session_id"
    if os.path.exists(session_id_file):
        with open(session_id_file, "r") as f:
            return f.read().strip()
    else:
        session_id = f"{datetime.datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:8]}"
        with open(session_id_file, "w") as f:
            f.write(session_id)
        return session_id

def send_request(url, method, payload_urls=None):
    """Sends a single HTTP request to the specified URL and returns metrics."""
    start_time = time.time()
    status_code = None
    success = False
    try:
        if method.upper() == 'POST':
            headers = {'Content-Type': 'application/json'}
            data = json.dumps({'urls': payload_urls})
            response = requests.post(url, headers=headers, data=data)
        else: # Default to GET
            response = requests.get(url)
        status_code = response.status_code
        response.raise_for_status() # Raise an exception for HTTP errors (4xx or 5xx)
        success = True
    except requests.exceptions.RequestException as e:
        print(f"Request to {url} ({method}) failed: {e}")
        if hasattr(e, 'response') and e.response is not None:
            status_code = e.response.status_code
    finally:
        end_time = time.time()
        latency = (end_time - start_time) * 1000 # Latency in ms
        print(f"Request to {url} ({method}) - Status: {status_code}, Time: {latency:.2f} ms, Success: {success}")
        return {"latency": latency, "status_code": status_code, "success": success}

def main():
    """Main function to parse arguments and run the load test."""
    try:
        print("Entering main function.")
        parser = argparse.ArgumentParser(description="Simple load testing script.")
        parser.add_argument("url", nargs='?', default="http://url-anvil:8080", help="The URL to send requests to. Defaults to http://url-anvil:8080.")
        parser.add_argument("request_count", type=int, help="The number of requests to send.")
        parser.add_argument("--method", default=os.getenv('REQUEST_METHOD', 'GET'), help="HTTP method (GET or POST).")
        parser.add_argument("--payload-urls", default=os.getenv('PAYLOAD_URLS', ''), help="Comma-separated URLs for POST request payload.")
        parser.add_argument("--challenge-type", default="load-test", help="Type of challenge for tracking.")
        parser.add_argument("--metric-name", default="load_test_run_metrics", help="Name of the metric for tracking.")
        parser.add_argument("--commit-hash", help="The git commit hash for the load test run.")
        
        print("Parsing arguments...")
        args = parser.parse_args()
        session_id = get_session_id()
        print(f"Arguments parsed: {args}")

        payload_urls_list = [url.strip() for url in args.payload_urls.split(',') if url.strip()]
        if not payload_urls_list and args.method.upper() == 'POST':
            print("Warning: POST method specified but no payload URLs provided. Using sample URLs.")
            payload_urls_list = ["https://example.com", "https://google.com"]

        print(f"Starting load test with {args.request_count} requests to {args.url} using {args.method} method.")

        results = []
        start_test_time = time.time()
        for i in range(args.request_count):
            result = send_request(args.url, args.method, payload_urls_list if args.method.upper() == 'POST' else None)
            results.append(result)
            print(f"Request {i+1}/{args.request_count} sent.")
            time.sleep(0.1) # Small delay to avoid overwhelming the target
        end_test_time = time.time()
        duration_s = end_test_time - start_test_time

        print("Load test finished. Aggregating metrics...")

        total_requests = len(results)
        successful_requests = sum(1 for r in results if r["success"])
        failed_requests = total_requests - successful_requests
        avg_latency_ms = sum(r["latency"] for r in results) / total_requests if total_requests > 0 else 0
        error_rate = (failed_requests / total_requests) * 100 if total_requests > 0 else 0
        rps = successful_requests / duration_s if duration_s > 0 else 0

        print(f"Total Requests: {total_requests}")
        print(f"Successful Requests: {successful_requests}")
        print(f"Failed Requests: {failed_requests}")
        print(f"Average Latency: {avg_latency_ms:.2f} ms")
        print(f"Error Rate: {error_rate:.2f} %")
        print(f"Requests Per Second (RPS): {rps:.2f}")
        print(f"Duration: {duration_s:.2f} s")

        # Prepare metrics for tracking service
        metrics_data = {
            "target_url": args.url,
            "request_count": args.request_count,
            "method": args.method,
            "payload_urls": payload_urls_list,
            "total_requests": total_requests,
            "successful_requests": successful_requests,
            "failed_requests": failed_requests,
            "avg_latency_ms": avg_latency_ms,
            "error_rate": error_rate,
            "rps": rps,
            "duration_s": duration_s,
            "test_type": "manual_load_test", # Example label
            "commit_hash": args.commit_hash
        }

        # Send tracking data using the new client
        tracking_client = LocalTrackerClient()
        tracking_client.send_metrics(
            challenge_type=args.challenge_type,
            metric_name=args.metric_name,
            metrics_data=metrics_data,
            session_id=session_id
        )

    except Exception as e:
        print(f"An error occurred in main: {e}")

if __name__ == "__main__":
    print("Inside __name__ == '__main__'")
    main()
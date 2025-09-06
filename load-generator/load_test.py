import requests
import argparse
import time

def send_request(url):
    """Sends a single GET request to the specified URL."""
    # print(f"DEBUG: Sending request to {url}")
    try:
        start_time = time.time()
        response = requests.get(url)
        end_time = time.time()
        print(f"Request to {url} - Status: {response.status_code}, Time: {end_time - start_time:.4f} seconds")
    except requests.exceptions.RequestException as e:
        print(f"Request to {url} failed: {e}")

def main():
    """Main function to parse arguments and run the load test."""
    parser = argparse.ArgumentParser(description="Simple load testing script.")
    parser.add_argument("url", help="The URL to send requests to.")
    parser.add_argument("request_count", type=int, help="The number of requests to send.")
    args = parser.parse_args()

    print(f"Starting load test with {args.request_count} requests to {args.url}")

    for i in range(args.request_count):
        send_request(args.url)
        print(f"Request {i+1}/{args.request_count} sent.")
        # A small delay to avoid overwhelming the server and to be a bit more realistic.
        time.sleep(0.1)

    print("Load test finished.")

if __name__ == "__main__":
    main()
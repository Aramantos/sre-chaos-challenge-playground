import requests
import argparse
import time
import threading

def send_request(url):
    """Sends a single GET request and prints the result."""
    try:
        start_time = time.time()
        response = requests.get(url)
        end_time = time.time()
        print(f"Request to {url} - Status: {response.status_code}, Time: {end_time - start_time:.4f} seconds")
    except requests.exceptions.RequestException as e:
        print(f"Request to {url} failed: {e}")

def main():
    """Main function to parse arguments and run the concurrent load test."""
    parser = argparse.ArgumentParser(description="Simple concurrent load testing script.")
    parser.add_argument("url", help="The URL to send requests to.")
    parser.add_argument("request_count", type=int, help="The total number of requests to send.")
    parser.add_argument("-c", "--concurrency", type=int, default=10, help="The number of concurrent requests to run.")
    args = parser.parse_args()

    print(f"Starting load test with {args.request_count} requests to {args.url} using {args.concurrency} concurrent workers.")

    threads = []
    for _ in range(args.request_count):
        thread = threading.Thread(target=send_request, args=(args.url,))
        threads.append(thread)
        thread.start()

        # Limit the number of active threads to the specified concurrency level
        if len(threads) % args.concurrency == 0:
            for t in threads:
                t.join() # Wait for the current batch of threads to finish
            threads = []

    # Wait for any remaining threads
    for thread in threads:
        thread.join()

    print("Load test finished.")

if __name__ == "__main__":
    main()
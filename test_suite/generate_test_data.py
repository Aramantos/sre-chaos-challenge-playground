#!/usr/bin/env python

import requests
import snappy
import time
import sys
import os

# Add the proto directory to the python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'proto'))

import remote_pb2
import types_pb2

# --- Configuration ---
BACKEND_URL = "http://localhost:3001/api/v1/metrics/write"
API_KEY = "key1"
USER_ID = "contributor_a"
CHALLENGE_TYPE = "default-challenge"
METRIC_NAME = "test_metric"


def register_influencer(api_key, challenge_type):
    """Registers the user as an active influencer for the challenge."""
    headers = {
        "Authorization": f"Bearer {api_key}"
    }
    data = {
        "challenge_type": challenge_type
    }
    try:
        response = requests.post(f"{BACKEND_URL.replace('/api/v1/metrics/write', '/api/v1/register-influencer')}", json=data, headers=headers)
        response.raise_for_status()
        print(f"Successfully registered as influencer for {challenge_type}. Response: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Error registering as influencer: {e}")

def create_write_request(metric_name, value, timestamp_ms, user_id, challenge_type):
    """Creates a Prometheus WriteRequest protobuf message."""
    write_request = remote_pb2.WriteRequest()
    timeseries = write_request.timeseries.add()

    # Add metric name label
    label_name = timeseries.labels.add()
    label_name.name = "__name__"
    label_name.value = metric_name

    # Add job label
    label_job = timeseries.labels.add()
    label_job.name = "job"
    label_job.value = "url-anvil"

    # Add user_id label
    label_user = timeseries.labels.add()
    label_user.name = "user_id"
    label_user.value = user_id

    # Add challenge_type label
    label_challenge = timeseries.labels.add()
    label_challenge.name = "challenge_type"
    label_challenge.value = challenge_type

    # Add a sample
    sample = timeseries.samples.add()
    sample.value = value
    sample.timestamp = timestamp_ms

    return write_request

def send_request(write_request):
    """Serializes, compresses, and sends the WriteRequest."""
    # Serialize the protobuf message
    serialized_data = write_request.SerializeToString()

    # Compress the data with snappy
    compressed_data = snappy.compress(serialized_data)

    # Set the headers
    headers = {
        "Content-Type": "application/x-protobuf",
        "Content-Encoding": "snappy",
        "Authorization": f"Bearer {API_KEY}"
    }

    # Send the request
    try:
        response = requests.post(BACKEND_URL, data=compressed_data, headers=headers)
        response.raise_for_status()  # Raise an exception for bad status codes
        print(f"Successfully sent metric. Response: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Error sending metric: {e}")

def generate_crash_challenge_data(user):
    """Generates data for the crash-challenge."""
    METRIC_NAME = "http_request_duration_ms_count"
    print(f"--- Sending metrics for user: {user['user_id']} ---")
    for i in range(5):
        timestamp_ms = int(time.time() * 1000)
        metric_value = 10 * (i + 1)
        write_request = create_write_request(
            METRIC_NAME,
            metric_value,
            timestamp_ms,
            user["user_id"],
            "crash-challenge"
        )
        send_request(write_request)
        time.sleep(1)

def generate_robust_service_data(user):
    """Generates data for the robust-service challenge."""
    print(f"--- Sending metrics for user: {user['user_id']} ---")
    # Simulate a service that is up and handling requests
    for i in range(5):
        timestamp_ms = int(time.time() * 1000)
        # Send up metric
        write_request_up = create_write_request("up", 1, timestamp_ms, user["user_id"], "robust-service")
        send_request(write_request_up)
        time.sleep(0.5)

        # Send request count and sum
        write_request_count = create_write_request("http_request_duration_ms_count", 10 * (i + 1), timestamp_ms, user["user_id"], "robust-service")
        send_request(write_request_count)
        time.sleep(0.5)

        write_request_sum = create_write_request("http_request_duration_ms_sum", 50 * (i + 1), timestamp_ms, user["user_id"], "robust-service")
        send_request(write_request_sum)
        time.sleep(1)

def generate_longest_upkeep_data(user):
    """Generates data for the longest-upkeep challenge."""
    print(f"--- Sending metrics for user: {user['user_id']} ---")
    # Simulate a service that starts and stays up
    start_time = int(time.time())
    timestamp_ms = start_time * 1000
    write_request_start = create_write_request("process_start_time_seconds", start_time, timestamp_ms, user["user_id"], "longest-upkeep")
    send_request(write_request_start)
    time.sleep(1)

    for _ in range(5):
        timestamp_ms = int(time.time() * 1000)
        write_request_up = create_write_request("up", 1, timestamp_ms, user["user_id"], "longest-upkeep")
        send_request(write_request_up)
        time.sleep(1)

if __name__ == "__main__":
    test_users = [
        {"user_id": "contributor_a", "api_key": "key1"},
        {"user_id": "contributor_b", "api_key": "key2"},
        {"user_id": "contributor_c", "api_key": "key3"},
    ]

    challenges = ["crash-challenge", "robust-service", "longest-upkeep"]

    for challenge in challenges:
        print(f"=== Generating data for challenge: {challenge} ===")
        for user in test_users:
            print(f"--- Registering user: {user['user_id']} for {challenge} ---")
            register_influencer(user["api_key"], challenge)
            
            if challenge == "crash-challenge":
                generate_crash_challenge_data(user)
            elif challenge == "robust-service":
                generate_robust_service_data(user)
            elif challenge == "longest-upkeep":
                generate_longest_upkeep_data(user)
        print("\n")

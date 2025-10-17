# Load Testing Guide

This guide explains how to run load tests against your applications and how to interpret the results.

## 1. Running a Load Test

You can run a basic load test using the `run_load_test.sh` script. This script takes two arguments: the target URL and the number of requests to send.

```bash
# Example: Run a load test against the url-anvil with 100 requests
bash scripts/run_load_test.sh http://url-anvil:8080 100
```

## 2. Running Example Challenge Scripts

For more specific load testing tailored to each challenge, you can use the example scripts located in `test_suite/public/`.

*   **`solve_graceful_degradation.py`**: Generates load for the Graceful Degradation challenge.
*   **`solve_robust_service.py`**: Generates load for the Robust Service challenge.
*   **`solve_longest_upkeep.py`**: Provides information on how to approach the Longest Upkeep challenge.

To run these scripts, first ensure your Python virtual environment is active (see "Python Virtual Environment (venv)" in the [README.md](../README.md)). Then, install their dependencies:

```bash
pip install -r test_suite/public/requirements.txt
```

Then, execute the desired script:

```bash
python test_suite/public/solve_graceful_degradation.py
# or
python test_suite/public/solve_robust_service.py
# or
python test_suite/public/solve_longest_upkeep.py
```

## 3. Interpreting the Results

The results of the load test will be displayed in the console. The results include the following metrics:

*   **Total Requests:** The total number of requests sent.
*   **Successful Requests:** The number of successful requests.
*   **Failed Requests:** The number of failed requests.
*   **Average Latency:** The average latency in milliseconds.
*   **Error Rate:** The percentage of requests that failed.
*   **RPS:** The number of requests per second.
*   **Duration:** The total duration of the test in seconds.

## 3. Viewing the Results in the Local Tracker

The results of the load test will also be sent to the Local Tracker. You can view the results in the Local Tracker App at `http://localhost:8082`.

The results will be grouped by session and by target. This allows you to easily compare the results of different load test runs.

# A Beginner's Guide to Stress Testing & Chaos Engineering

Welcome! You've successfully set up a web server and a monitoring stack. Now it's time to think like a Site Reliability Engineer (SRE) and ask the important questions: "What are the limits of our system?" and "How does it break?"

This guide will introduce you to two key concepts for answering those questions: Stress Testing and Chaos Engineering.

## What is Stress Testing?

You've already run a **load test** using `load_test.py`. A load test checks how the system behaves under a *normal* or expected amount of traffic.

A **stress test** is more extreme. Its goal is to push the system to its breaking point to see what happens. By intentionally overwhelming the server, we can find its limits, identify bottlenecks, and observe how it fails. Does it get slow? Does it become unresponsive? Does it start returning errors? These are the questions a stress test helps us answer.

## How to Stress Test This Project

### Using the Graceful Degradation Solver

The `solve_graceful_degradation.py` script (located in `test_suite/public/`) is designed to continuously send requests to the `url-anvil` service, simulating a sustained load. This is an excellent way to stress test your application and observe its behavior under pressure.

**The Command:**

First, ensure you have installed the dependencies for the public test suite:
`pip install -r test_suite/public/requirements.txt`

Then, run the solver script:
`python test_suite/public/solve_graceful_degradation.py`

**What to Watch For:**

While this script is running, keep your Grafana dashboard open. Observe how your application and the `url-anvil` service respond:
*   **Latency:** Does the average response time increase significantly?
*   **Throughput:** Can your application maintain a high rate of successful requests?
*   **Errors:** Does your application start returning errors, or does it gracefully handle the load?
*   **Resource Usage:** Monitor CPU and memory usage for signs of bottlenecks.

### Scenario 1: The Slow Burn (Finding the Limit)

Let's start by pushing the server with a significantly higher number of sequential requests. This will help us find the upper limit of what it can handle in its current configuration.

**The Command:**

Run the original load generator with 500 requests:
`docker-compose run --rm load-generator python load_test.py http://<your-app-name> 500`

**What to Watch For:**

Keep your Grafana dashboard open while this is running. You are looking for signs of stress:
*   **CPU & Memory Usage:** Do the graphs for the `web` container's resource usage start to climb towards 100%?
*   **Response Time:** Does the average response time (if your dashboard shows it) start to increase?
*   **Errors:** Does the load test script start printing any non-200 status codes (like `502 Bad Gateway`)? This would indicate the server is struggling to keep up.

### Scenario 2: The Sudden Spike (A More Realistic Stress Test)

Our `load_test.py` script sends requests one after another. A real-world traffic spike involves many users hitting the server *at the same time*. To simulate this, we will use a new, more powerful script called `stress_test.py` that sends requests concurrently.

**The New Script (`stress_test.py`):**

This script uses Python's `threading` library to dispatch multiple requests at once. It adds a `-c` (concurrency) flag to control how many requests are sent simultaneously.

**The Command:**

This command will send 100 total requests, but it will run them in batches of 50 concurrent requests. This is a much more intense test.
`docker-compose run --rm load-generator python stress_test.py http://<your-app-name> 100 -c 50`

This type of load is much more likely to overwhelm the server and reveal how it behaves under sudden, intense pressure.

### Scenario 3: Normal Load Test (Baseline for URL Anvil)

Before you start stress testing your own application, it's often useful to establish a baseline for the `url-anvil` service itself. This helps you understand its normal behavior.

**The Command:**

Run the load generator with 10 requests against the `url-anvil` service:
`docker-compose run --rm load-generator python load_test.py http://url-anvil:8080 10`

**What to Watch For:**

Observe the response times and status codes. This provides a healthy baseline for `url-anvil` when not under stress from your application.

## A Gentle Introduction to Chaos Engineering

Chaos engineering is the practice of intentionally injecting failure into your system to see how it responds. The goal is not to break things, but to build confidence that your system can withstand unexpected failures gracefully.

### Chaos Experiment: Kill the Metrics Exporter

Let's run a simple chaos experiment.

**Hypothesis:** "If the `nginx-exporter` container, which translates metrics, is shut down, we will lose our monitoring data in Grafana, but the main website will remain online and accessible to users."

This tests whether our monitoring system is properly decoupled from our main application.

**The Experiment:**

1.  While everything is running, open your Grafana dashboard. You should see data.
2.  Open your web browser to the Nginx server at `http://localhost:8080`. You should see the "Welcome" page.
3.  In your terminal, run the following command to instantly kill the exporter container:
    `docker-compose kill nginx-exporter`
4.  **Observe the results:**
    *   Your Grafana dashboard will stop receiving new data.
    *   Refresh your browser on `http://localhost:8080`. The website should still be perfectly functional.

**Conclusion:** The experiment is a success! It proves that a failure in our monitoring pipeline does not impact our users. This is a sign of a resilient, well-architected system.

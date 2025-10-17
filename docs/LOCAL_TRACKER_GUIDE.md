# Local Tracker (Personal Performance Sandbox)

**THIS IS NOT THE OFFICIAL SCORING SYSTEM.**

This guide explains what the Local Tracker is and how to use it for personal performance experimentation. It is a sandbox environment for you to test your applications and has **no connection to the official SRE Chaos Challenge leaderboard or scoring mechanics.**

## 1. What is the Local Tracker?

The Local Tracker is a set of services (`local-tracker-service`, `local-tracker-app`) designed for one purpose: **to help you track the performance of your own applications in your local development environment.**

Think of it as your personal lab notebook. As you optimize your code, you can use the tracker to log performance metrics (like latency, RPS, and error rates) and see how your changes impact your application's behavior over time.

**Crucial Limitations:**
*   **Local-Only:** It runs exclusively on your machine and is not accessible from the internet.
*   **Unofficial:** Data submitted to the Local Tracker is for your eyes only. It **never** affects your official score in the SRE Chaos Challenge.
*   **Untrusted:** The data comes from your own scripts. For official competitions, metrics are gathered by a secure, centralized system to ensure fairness and prevent tampering.

## 2. How to Use the Local Tracker

You can send data to the `local-tracker-service` using the provided Python client (`local_tracker_client.py`).

### 2.1. Environment Variables

Set the following in your `.env` file:

*   `LOCAL_TRACKER_API_KEY`: A simple password to distinguish your local data from another user's if you are sharing a machine. **This is not a real security feature.**
*   `LOCAL_TRACKER_USER_ID`: Your username, to associate data with your profile in the local app.

Example `.env` entries:
```
LOCAL_TRACKER_API_KEY=local_dev_key
LOCAL_TRACKER_USER_ID=local_dev_user
```

### 2.2. Using `local_tracker_client.py`

Metrics are automatically collected and sent by the `load-generator` and `local-tracker-client`. The `load-generator` will create a new session each time it is started. All subsequent load tests will be grouped under this session.

To ensure all necessary Python dependencies are installed, first activate your Python virtual environment (see "Python Virtual Environment (venv)" in the [README.md](../README.md)), then run:

```bash
pip install -r requirements.txt
```

Developers extending these tools can refer to **[METRIC_SCHEMA_REFERENCE.md](METRIC_SCHEMA_REFERENCE.md)** for the data structure.

## 3. Viewing Your Local Results

Navigate to the **Local Tracker App** in your browser (usually `http://localhost:8082`). It will display the data you have sent.

## 4. Architectural Context & Data Storage

The Local Tracker is intentionally isolated. For a detailed explanation of the official competition architecture and how it differs from this local utility, please see the **[ARCHITECTURE.md](../ARCHITECTURE.md)** file.

**Database Note:** For convenience in local development, the Local Tracker may use the same PostgreSQL container as other services. However, it uses its own tables (e.g., `local_test_runs`) and should be considered entirely separate. For true isolation, you could configure it to use a local SQLite database.

# Node.js Backend

## What is the Node.js Backend?
The Node.js Backend is the central API service for the SRE Chaos Challenge. Built with Express.js, it acts as the brain of the operation, processing incoming data, applying business logic, and serving information to the frontend.

## How this Project Uses the Node.js Backend
The `backend` service is critical for the real-time scoring and leaderboard functionality. Its primary responsibilities include:

1.  **Prometheus Remote Write Receiver:** It exposes an endpoint (`/api/v1/metrics/write`) to receive all metrics scraped by Prometheus via its `remote_write` feature. These metrics are sent as snappy-compressed Protobuf data.
2.  **Metric Processing:** It decompresses and decodes the incoming Prometheus metrics, extracting relevant data points for scoring.
3.  **Authentication:** It authenticates incoming requests (e.g., from `remote_write` or the frontend) using API keys stored in the PostgreSQL database.
4.  **Challenge Scoring:** Based on the `challenge_type` associated with a contributor (retrieved from the database), it applies specific scoring algorithms to the incoming metrics. This is where the core challenge logic resides.
5.  **Leaderboard Data Management:** It stores and updates the calculated scores and competition entries in the PostgreSQL database.
6.  **Leaderboard API:** It provides API endpoints (e.g., `/api/v1/leaderboard/:challenge`) that the Angular frontend queries to display real-time rankings.
7.  **Database Schema Initialization:** On startup, the backend ensures the necessary database tables (`api_keys`, `competition_entries`) are created or updated.

## How You Can Use the Node.js Backend (Interacting with the Platform)

As a contributor, your primary interaction with the Node.js Backend will be through the metrics your application sends and the leaderboard data it provides. Understanding its role helps you optimize your application for scoring:

*   **Metric Impact:** The backend processes the metrics your application exposes via Prometheus. Focus on ensuring your application provides the right metrics to positively impact your score in a given challenge.
*   **API Key Usage:** Your unique API key is used by the backend to authenticate your metrics and associate them with your challenge entry.
*   **Leaderboard Data:** The backend serves the data that populates the leaderboard. You can observe how your application's performance translates into scores by viewing the frontend.

**Note:** Direct contributions to the core backend logic, scoring algorithms, or API endpoints are generally not accepted for Hacktoberfest. If you have suggestions for platform-level improvements, please open an issue.

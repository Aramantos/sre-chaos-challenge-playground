# Understanding the SRE Chaos Challenge Stack

**Table of Contents**

*   [1 Core Application Services](#1-core-application-services)
*   [2 Data and Management Services](#2-data-and-management-services)
*   [3 Monitoring and Observability Services](#3-monitoring-and-observability-services)
*   [4 Interconnections and Data Flow](#4-interconnections-and-data-flow)
*   [5 Detailed Component Guides](#5-detailed-component-guides)

The SRE Chaos Challenge is a comprehensive, containerized application designed to simulate a real-world microservices environment, complete with a web application, a backend API, a persistent database, and a full monitoring stack. This section provides a high-level overview of each component and how they interact to form a cohesive system.

## 1 Core Application Services

*   **`url-anvil` service (Node.js URLAnvil)**:
    *   **Purpose**: This is a **sample**, observable target application for the SRE challenges. It is designed to have multiple realistic failure modes (CPU, Network I/O) to provide an interesting and fair competition. Contributors will typically deploy their own applications, but `url-anvil` serves as a good baseline and example.
    *   **How it's used**: It is the target for the `load-generator` and a source of metrics for `prometheus`. It has several endpoints, including a main `/api/test` endpoint that performs a workload of fetching and processing external URLs.
    *   **Communication**: Accessible via `http://localhost:8080`. It exposes a `/metrics` endpoint for Prometheus to scrape.
    *   **[Detailed Guide: Nginx](./tech/Nginx.md)**

*   **`load-generator` service (Python Script)**:
    *   **Purpose**: Simulates user traffic against the `url-anvil` service to generate meaningful metrics.
    *   **How it's used**: Continuously sends HTTP requests to the `url-anvil` service.
    *   **Communication**: Connects directly to the `url-anvil` service within the Docker network.

*   **`create_contributor_app.py` (Python Script)**:
    *   **Purpose**: Automates the onboarding process for new contributors.
    *   **How it's used**: Guides contributors through setting up their application, generates personalized Docker Compose files, registers their application with Prometheus, and provides them with an API key.
    *   **Communication**: Interacts with the user via CLI, generates local files, and (in future iterations) will communicate with the `backend` for dynamic Prometheus target registration.

*   **`backend` service (Node.js/Express API)**:
    *   **Purpose**: The central nervous system of the SRE Chaos Challenge. It's responsible for ingesting real-time Prometheus metrics, calculating challenge scores, authenticating contributors, storing data, and serving leaderboard information.
    *   **How it's used**: 
        *   Receives Prometheus `remote_write` requests (snappy-compressed protobuf data) from the `prometheus` service.
        *   Decompresses and decodes these metrics using `snappy` and `protobufjs`.
        *   Authenticates requests and identifies the `challenge_type` using API keys stored in the `db` service.
        *   Applies challenge-specific scoring logic (for "Robust", "Graceful Degradation", and "Longest Upkeep" challenges) to the incoming metrics.
        *   Stores and updates competition entries (scores) into the `db` service.
        *   Serves the leaderboard data to the `frontend` service.
    *   **Communication**: 
        *   Listens for POST requests on `/api/v1/metrics/write` (for Prometheus `remote_write`).
        *   Connects to the `db` service (PostgreSQL) to store and retrieve data.
        *   Serves API endpoints (e.g., `/api/v1/leaderboard/:challenge`) to the `frontend`.
    *   **[Detailed Guide: Node.js Backend](./tech/NodejsBackend.md)**

*   **`frontend` service (Angular Application)**:
    *   **Purpose**: The user-facing leaderboard that displays contributor rankings based on their service performance.
    *   **How it's used**: Fetches data from the `backend` API and renders it in a dynamic, sortable table for each of the three challenges.
    *   **Communication**: Makes HTTP GET requests to the `backend` service's leaderboard endpoint. Accessible via `http://localhost:8081`.
    *   **[Detailed Guide: Angular Frontend](./tech/AngularFrontend.md)**

## 2 Data and Management Services

*   **`db` service (PostgreSQL Database)**:
    *   **Purpose**: Provides persistent storage for the `backend` service, holding API keys and collected competition entries.
    *   **How it's used**: The `backend` service connects to it to store and retrieve data.
    *   **Communication**: Listens for connections from the `backend` and `pgadmin` services on port `5432` within the Docker network. Data is persisted using a named Docker volume (`db_data`).
    *   **[Detailed Guide: PostgreSQL](./tech/PostgreSQL.md)**

*   **`pgadmin` service (PostgreSQL Administration Tool)**:
    *   **Purpose**: A web-based graphical interface for managing and inspecting the PostgreSQL `db` service.
    *   **How it's used**: Allows developers to view tables, query data, and manage the database schema.
    *   **Communication**: Connects to the `db` service. Accessible via `http://localhost:5050`.

## 3 Monitoring and Observability Services

*   **`prometheus` service (Metrics Collection and Storage)**:
    *   **Purpose**: The core monitoring system. It scrapes metrics from configured targets (like `url-anvil` and contributor applications), stores them, makes them queryable, and forwards them to the backend for scoring.
    *   **How it's used**: 
        *   Periodically scrapes metrics from the `/metrics` endpoint of `url-anvil` and deployed contributor applications.
        *   Stores these time-series metrics locally.
        *   Forwards a copy of all scraped metrics to the `backend` service via `remote_write`.
    *   **Communication**: 
        *   Scrapes `url-anvil` and contributor applications on their `/metrics` endpoints.
        *   Serves its own UI and metrics on port `9090`.
        *   Sends metrics to the `backend` service's `/api/v1/metrics/write` endpoint.
    *   **[Detailed Guide: Prometheus](./tech/Prometheus.md)**

*   **`grafana` service (Data Visualization)**:
    *   **Purpose**: Provides powerful dashboards and visualization tools for the metrics stored in Prometheus.
    *   **How it's used**: Connects to `prometheus` as a data source to build and display interactive dashboards.
    *   **Communication**: Connects to the `prometheus` service to query metrics. Accessible via `http://localhost:3000`. Its configuration and dashboards are persisted using a named Docker volume (`grafana_data`).
    *   **[Detailed Guide: Grafana](./tech/Grafana.md)**

## 4 Interconnections and Data Flow

The entire stack operates as a continuous feedback loop, driven by real-time metrics:

1.  The **`load-generator`** creates traffic for a **contributor's deployed application** (e.g., `url-anvil` or their custom app).
2.  The **contributor's application** processes requests and exposes its performance metrics via a `/metrics` endpoint (often through an Nginx exporter sidecar).
3.  **`prometheus`** scrapes these metrics from the deployed applications.
4.  **`prometheus`** then forwards a copy of these scraped metrics to the **`backend`** service via `remote_write`.
5.  The **`backend`** receives, decompresses, decodes, and processes these metrics. It identifies the contributor and challenge type, calculates scores based on predefined logic, and stores/updates these scores in the **`db`** (PostgreSQL) service.
6.  The **`frontend`** application queries the **`backend`** for leaderboard data.
7.  The **`backend`** retrieves the latest scores from the **`db`** and serves them to the `frontend`.
8.  **`grafana`** connects directly to **`prometheus`** to visualize the raw, real-time metrics from the deployed applications, providing insights into their performance under load.
9.  **`pgadmin`** provides a direct interface to manage and inspect the **`db`** service.

This interconnected system allows for comprehensive monitoring, real-time scoring, data analysis, and a dynamic leaderboard experience, forming the core of the SRE Chaos Challenge.

## 5 Detailed Component Guides

For more in-depth information on specific technologies used in this project, refer to the following guides:

*   **[Angular Frontend](./tech/AngularFrontend.md)**
*   **[Grafana](./tech/Grafana.md)**
*   **[Nginx](./tech/Nginx.md)**
*   **[Node.js Backend](./tech/NodejsBackend.md)**
*   **[PostgreSQL](./tech/PostgreSQL.md)**
*   **[Prometheus](./tech/Prometheus.md)**
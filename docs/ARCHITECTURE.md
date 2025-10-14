# SRE Chaos Challenge - Project Architecture & Vision

## 1. High-Level Vision

This document outlines the core architectural principles and goals for the SRE Chaos Challenge project. It serves as a guiding charter to ensure all development and troubleshooting efforts align with the project's intended purpose.

The project has two primary modes of operation:
1.  **A Local Playground:** A self-contained Docker Compose environment for individuals to learn and experiment with SRE principles.
2.  **A Cloud-Based Competition:** A future cloud-native deployment where users can compete in standardized SRE challenges.

---

## 2. Core Components & Services

### 2.1. The Local Playground

This is the primary function of the `main` branch.

-   **Purpose:** To provide a stable, easy-to-run local sandbox. A developer can clone the repository, run `docker-compose up`, and have a fully functional environment.
-   **User Actions:**
    -   Set up and run their own web applications.
    -   Direct metrics from their applications to a provided Prometheus instance.
    -   Visualize metrics in a provided Grafana instance.
    -   Experiment with SRE concepts like load balancing, chaos engineering, and performance tuning in a consequence-free environment.

### 2.2. The Local Tracker (Personal Sandbox)

-   **Purpose:** To provide a **personal, non-competitive, local-only sandbox** for a user to experiment with performance tracking for their *own applications*.
-   **Functionality:** As a user makes changes to their application, they can send metrics to this service to log their performance over time. This allows them to see a historical view of their improvements in a private, consequence-free environment.
-   **Scope:** This service is **strictly for the user's benefit** and is **completely separate from the public competition**. It has no pathway to submit scores to the official leaderboard and is disabled by default. It must be explicitly enabled via an environment variable (`ENABLE_LOCAL_TRACKER=true`) for local use.

### 2.3. The Leaderboard & Competition

-   **Purpose:** To provide a public, competitive challenge environment. This is currently in development and being tested locally before any cloud deployment.
-   **The Role of `url-anvil`:** The `url-anvil` service is the **standardized baseline** for the competition. All participants are measured on how their infrastructure handles load directed at this common service. This ensures a fair, apples-to-apples comparison. Users do not modify the `url-anvil` itself; they build infrastructure *around* it.
-   **Current Status:** The immediate goal is to get the leaderboard fully functional in the local environment. This includes fixing the bug where only one of three statistics is correctly displayed for the "Robust Service" and "Longest Upkeep" challenges.

---

## 3. Future Vision: Cloud Deployment

-   **Goal:** To deploy the entire suite of services into a cloud-native environment (e.g., Kubernetes).
-   **Competition Integrity:** To ensure the legitimacy of competition results, the cloud architecture will be designed to provide a controlled execution environment. The proposed model is:
    1.  A user submits their infrastructure-as-code configuration.
    2.  The system spins up the user's environment within a dedicated, isolated pod (or set of pods) on a project-owned cluster.
    3.  The load test is run against their pod.
    4.  Metrics are collected and scored by the centralized backend services.
    -   This model prevents users from submitting fraudulent or locally generated metrics to the public leaderboard.

## 4. Developer Experience

The local tracker is a key component of the developer experience. It provides a personal, non-competitive sandbox for users to experiment with performance tracking for their own applications. As a user makes changes to their application, they can use the local tracker to log their performance over time. This allows them to see a historical view of their improvements in a private, consequence-free environment.

The local tracker is designed to be easy to use. The `dev-setup.sh` script automates the process of setting up the local environment, and the `run_load_test.sh` script provides a simple way to run load tests against different targets. The local tracker app provides a simple UI for visualizing the results of these tests.

The local tracker is also designed to be isolated from the production environment. It uses its own database and has its own set of environment variables. This ensures that the local tracker does not interfere with the official competition.

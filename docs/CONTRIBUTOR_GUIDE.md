# Contributor Guide

## CURRENT STATUS: The Playground is working so you can proceed with using the [Contributor Onboarding: Deploying Your Application](#contributor-onboarding-deploying-your-application) and the [Step 2: Build and Run the Application](#step-2-build-and-run-the-application) guides and this should have your playground up and running.

**Table of Contents**

*   [1. Project Overview](#1-project-overview)
*   [2. Prerequisites](#2-prerequisites)
*   [3. Getting Started (Running the Project Locally)](#3-getting-started-running-the-project-locally)
    *   [Step 1: Get the Code](#step-1-get-the-code)
    *   [Step 2: Build and Run the Application](#step-2-build-and-run-the-application)
    *   [Step 3: Access the Services](#step-3-access-the-services)
    *   [Step 4: Setting up the Grafana Dashboard](#step-4-setting-up-the-grafana-dashboard)
*   [4. Contributing to the Project](#4-contributing-to-the-project)
    *   [Code of Conduct](#code-of-conduct)
    *   [Reporting Bugs and Opening Issues](#reporting-bugs-and-opening-issues)
    *   [Feature Requests](#feature-requests)
    *   [Contributor Onboarding: Deploying Your Application](#contributor-onboarding-deploying-your-application)
    *   [Development Workflow](#development-workflow)
    *   [Coding Standards and Conventions](#coding-standards-and-conventions)
*   [5. Understanding the Architecture](#5-understanding-the-architecture)
*   [6. Getting Help](#6-getting-help)

Welcome to the SRE Chaos Challenge project! This guide will help you get started with the project, understand its architecture, and contribute effectively.

## 1. Project Overview

This project is a complete, containerized web application stack designed to teach and evaluate Site Reliability Engineering (SRE) concepts. It includes:

*   **Contributor Web Applications**: Your deployed web services that will be monitored.
*   **Prometheus**: A monitoring system that collects metrics from your applications.
*   **Grafana**: A dashboarding tool for visualizing the collected metrics.
*   **Backend (Node.js/Express)**: Processes metrics from Prometheus, calculates scores for various challenges, and stores them in a PostgreSQL database.
*   **Frontend (Angular)**: Displays a real-time leaderboard based on the scores calculated by the backend.
*   **PostgreSQL**: The database for storing API keys and competition entries.

The platform emphasizes verifiable, live metrics rather than self-reported results, ensuring integrity in scoring across multiple challenge types.

## 2. Prerequisites

Before you begin, you will need to have Docker and Docker Compose installed on your system.

*   **Docker**: This is the underlying technology that allows us to run applications in isolated environments called containers. You can find the official installation guide here: [Get Docker](https://docs.docker.com/get-docker/)
*   **Docker Compose**: This is a tool for defining and running multi-container Docker applications. It makes it easy to manage all the different services in our project (like the web server, database, etc.) with a single command. Docker Compose is included with most Docker Desktop installations.

For a detailed explanation of the Docker Compose commands used in this project, please refer to the [Command Glossary](COMMAND_GLOSSARY.md).

## 3. Getting Started (Running the Project Locally)

### Step 1: Get the Code

Clone the repository and navigate into the project directory:

```bash
git clone https://github.com/your-username/your-repository.git # Replace with actual URL
cd your-repository
```

### Step 2: Build and Run the Application

This command will build the Docker images and start all the services defined in `docker-compose.yml`:

```bash
docker compose up --build
```

*   `--build`: Builds images from scratch (use this the first time or after `Dockerfile` changes).
*   `up`: Starts all services.

> **Pro Tip**: To run services in the background, use `docker compose up --build -d`.

### Step 3: Access the Services

Once running, access services in your web browser:

*   **Leaderboard**: `http://localhost:8081`
*   **URLAnvil Service**: `http://localhost:8080` (target app for challenges)
*   **Prometheus**: `http://localhost:9090`
*   **Grafana**: `http://localhost:3000` (Default login: `admin` / `admin`)

### Step 4: Setting up the Grafana Dashboard

1.  **Log in to Grafana** at `http://localhost:3000` (`admin` / `admin`).
2.  **Add Prometheus Data Source**:
    *   Go to **Configuration** (gear icon ⚙️) > **Data Sources**.
    *   Click **Add data source** > **Prometheus**.
    *   Set **URL** to `http://prometheus:9090` (services communicate via Docker network names).
    *   Click **Save & test**.
3.  **Import a Dashboard**:
    *   Go to **Dashboards** (four-squares icon ⊞) > **Manage**.
    *   Click **Import**.
    *   Enter ID `12708` (for Nginx Prometheus Exporter).
    *   Click **Load**, select the **Prometheus** data source, and click **Import**.

> **Note**: While this guide shows you how to import a standard dashboard, you are encouraged to create your own custom Grafana dashboards to explore your application's metrics in more detail. The official leaderboard, however, will use the scores calculated by the backend API, not directly from your Grafana dashboards.

## 4. Contributing to the Project

We welcome contributions! Please follow these guidelines to ensure a smooth collaboration.

### Code of Conduct

We expect all contributors to be respectful and collaborative. Please ensure your interactions are inclusive and constructive.

### Reporting Bugs and Opening Issues

*   Before opening a new issue, please search existing issues to see if your problem has already been reported.
*   If not, open a new issue and provide a clear title and detailed description. Include steps to reproduce, expected behavior, actual behavior, and relevant environment details (OS, Docker versions, etc.).

### Feature Requests

*   Open an issue to propose new features or enhancements. Describe the problem you're trying to solve and how your proposed feature would address it.

### Contributor Onboarding: Deploying Your Application

To participate in the SRE Chaos Challenge, you'll deploy your own web application into the platform. We provide a script to automate the initial setup.

1.  **Run the Onboarding Script**:
    From the project root, run the `create_contributor_app.py` script.
    ```bash
    python create_contributor_app.py
    ```
    The script will prompt you for a GitHub username. This will be your unique identifier in the
    challenge. It will then create your personal application directory at contributors/<your-username>/ and
    automatically update your local `.env` file with your API key and username for seamless integration.

2.  **Implement Your Solution**:
    Your goal is to modify the files in this directory (`index.html`, `nginx.conf`, `Dockerfile`) to create a web service that can best handle the various challenges. **For details on each challenge, refer to the "Understanding the Challenges" section above.** This is where you get creative!

3.  **Launch Your Application**:
    The onboarding script will give you a command to launch your application. It will look like this:
    ```bash
    docker-compose -f docker-compose.yml -f compose-files/docker-compose.<your-username>.yml up --build -d
    ```
    This command combines the main platform services with your new application. Prometheus will automatically discover and begin monitoring your app in real-time.

### Understanding the Challenges

The SRE Chaos Challenge features three distinct challenges, each designed to test different aspects of your application's performance and resilience. For all challenges, your deployed application will interact with the platform's **`url-anvil` service** as a consistent target. **Scores for the main leaderboard are derived from `url-anvil`'s metrics and attributed to the contributor currently registered as the "active influencer" for that challenge.**

#### 1. Graceful Degradation Challenge

*   **Goal:** To build a resilient application that can gracefully handle stress and continue to serve requests even when the target service (`url-anvil`) is unstable.
*   **Mechanism:** Your deployed application will be subjected to a continuous stressor. Your goal is to implement architectural patterns (like load balancing, retries, circuit breakers, etc.) to ensure that your application can continue to interact with `url-anvil` and that `url-anvil` can handle as many requests as possible.
*   **Scoring:** Your score is based on the **total number of requests handled** by `url-anvil` while your solution is active. A solution that keeps `url-anvil` available and handling requests, even if it's slow or periodically unavailable, will score higher than a solution that allows `url-anvil` to become unresponsive and stay down.
*   **Fairness:** `url-anvil` provides a consistent, known target for all participants.

#### 2. Robust Service Challenge

*   **Goal:** To build a highly efficient and reliable service that can handle a standardized, sustained load, often by interacting with `url-anvil`.
*   **Mechanism:** You will deploy your application (e.g., a custom web service, a caching layer, or a smart proxy). This application will be subjected to a standardized load from the platform's `load-generator`. Your service will often be designed to interact with **`url-anvil`** as part of its function (e.g., proxying requests to `url-anvil`).
*   **Scoring:** Your score will be based on metrics from **`url-anvil`**, specifically those influenced by **your deployed application**. This will include:
    *   Average latency of requests to `url-anvil` (as influenced by your service).
    *   Throughput (requests per second - RPS) of `url-anvil` (as influenced by your service).
    *   Error rates from `url-anvil`.
*   **Fairness:** `url-anvil` provides a consistent, known target for all participants.

#### 3. Longest Upkeep Challenge

*   **Goal:** To build the most resilient and highly available service that can withstand continuous, aggressive stress and maintain uptime for the longest duration.
*   **Mechanism:** You will deploy your application, potentially implementing advanced architectural patterns like load balancing, auto-scaling, and redundancy. The platform will subject your application to a continuous stressor that will test its stability. Your application will likely interact with **`url-anvil`** as part of its workload.
*   **Scoring:** Your score will be based on metrics from **`url-anvil`**, specifically those influenced by **your deployed application**. This will include:
    *   Total uptime duration of `url-anvil` under continuous stress.
    *   Time for `url-anvil` to recover from any induced failures.
    *   Number of successful requests served by `url-anvil` during the stress period.
*   **Fairness:** `url-anvil` provides a consistent, known target for all participants.
### Development Workflow

For a detailed guide on Git, forking, and project navigation, please refer to the [Git Tutorial (docs/GIT_TUTORIAL.md)](./docs/GIT_TUTORIAL.md).

For a detailed guide on how to use the local tracker and run load tests, please see the [Local Tracker Guide](./LOCAL_TRACKER_GUIDE.md) and the [Load Testing Guide](./LOAD_TESTING_GUIDE.md).

1.  **Fork the Repository**: Fork the project repository to your GitHub account.
2.  **Clone Your Fork**: Clone your forked repository to your local machine.

```bash
git clone https://github.com/your-username/sre-chaos-challenge.git
cd sre-chaos-challenge
```

3.  **Create a New Branch**: Create a new branch for your feature or bug fix. Use a descriptive name (e.g., `feature/add-dynamic-sd`, `bugfix/fix-scoring-logic`).

```bash
git checkout -b feature/your-feature-name
```

4.  **Make Your Changes**: Implement your feature or bug fix. Ensure your code adheres to the project's coding style and conventions.
5.  **Test Your Changes**: Run existing tests and add new tests for your changes if applicable. Ensure all tests pass.
6.  **Commit Your Changes**: Write clear, concise commit messages.

```bash
git commit -m "feat: Add new feature" # or "fix: Fix bug"
```

7.  **Push Your Branch**: Push your local branch to your forked repository on GitHub.

```bash
git push origin feature/your-feature-name
```

8.  **Open a Pull Request (PR)**: Go to the original repository on GitHub and open a new Pull Request from your branch. Provide a clear title and detailed description of your changes. Reference any related issues.

### Coding Standards and Conventions

*   **Follow Existing Style**: Mimic the style (formatting, naming), structure, framework choices, typing, and architectural patterns of existing code in the project.
*   **Comments**: Add comments sparingly, focusing on *why* something is done, especially for complex logic. Avoid comments that simply restate what the code does.
*   **Testing**: If you're adding new features or fixing bugs, please include appropriate unit or integration tests.

## 5. Understanding the Architecture

For a deeper dive into the project's technical components, data flow, and high-level design decisions, please refer to the following documents:

*   **[Tech Stack Overview](TECH_STACK.md)**: A detailed breakdown of each service and how they interconnect.
*   **[Architecture Decisions](ARCHITECTURE.md)**: A record of the strategic design choices and trade-offs made for the platform.

## 6. Getting Help

If you have any questions or need assistance, please open an issue on GitHub or reach out through **srechaoschallenge@gmail.com**.

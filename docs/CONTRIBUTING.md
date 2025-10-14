# Contributing to the SRE Chaos Challenge

First off, thank you for considering contributing! This document provides guidelines to help you get started with the project, understand the development workflow, and use the local performance tracker.

## Getting Started: One-Command Setup

The goal is to get you from a fresh clone to a running environment with a single command.

**Prerequisites:**
*   Docker and Docker Compose
*   Git
*   Node.js and npm (for pre-commit hooks)

**Initial Setup:**

```bash
# Clone the repository
git clone <repository-url>
cd sre-chaos-challenge

# Run the developer setup script
bash scripts/dev-setup.sh
```

This script will build the necessary Docker images, start all services, and run a smoke test to verify that the environment is healthy and ready for development.

## Project Structure

Here is a high-level overview of the most important directories:

```
.
├── backend/             # The main backend service for the official competition.
├── docs/                # Project documentation, including architecture and guides.
├── frontend/
│   ├── leaderboard-app/ # The official competition leaderboard UI.
│   └── local-tracker-app/ # The UI for the local-only performance tracker.
├── load-generator/      # Scripts for generating load and submitting metrics.
├── local-tracker-service/ # The local-only service for storing performance data.
├── scripts/             # Automation, verification, and utility scripts.
└── ...
```

## Development Workflow

1.  **Create a Branch:** Always start your work on a new feature branch:
    ```bash
    git checkout -b your-feature-name
    ```

2.  **Make Your Changes:** As you work, take advantage of the local performance tracker to monitor the impact of your changes.

3.  **Use the Local Tracker:**
    *   The local tracker is your personal sandbox for performance testing. Data sent to it is for your eyes only and does not affect the official leaderboard.
    *   To run a load test and send data to the tracker, execute:
        ```bash
        docker-compose exec load-generator python load_test.py 100
        ```
    *   View your results in the **Local Tracker App** at `http://localhost:8082`.
    *   For a detailed guide, please see the [Local Tracker Guide](./docs/LOCAL_TRACKER_GUIDE.md).

4.  **Commit Your Changes:** When you commit, a pre-commit hook will automatically run to verify that your changes adhere to the project's architectural rules (e.g., no outdated references).

5.  **Submit a Pull Request:** Push your branch to the remote repository and open a pull request. Please provide a clear description of the changes and the problem they solve.

## Questions?

If you have any questions or get stuck, please feel free to open an issue on GitHub.

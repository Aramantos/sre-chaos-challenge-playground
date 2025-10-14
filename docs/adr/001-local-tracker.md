# 1. Title

Local Tracker for Personal Performance Experimentation

## 2. Status

Accepted

## 3. Context

As the SRE Chaos Challenge project evolved, it became clear that there was a need for a way for users to experiment with performance tracking for their own applications in a private, consequence-free environment. The official leaderboard and competition environment is designed for fair, apples-to-apples comparisons, which means that users cannot modify the baseline application (`url-anvil`) or submit their own metrics.

This created a gap in the developer experience. Users had no way to see a historical view of their improvements as they made changes to their applications. They also had no way to test their monitoring and observability setups in a realistic way.

## 4. Decision

To address this gap, we decided to create a new set of services called the "Local Tracker". The Local Tracker is a personal, non-competitive, local-only sandbox for users to experiment with performance tracking for their own applications.

The Local Tracker consists of three main components:

*   **`local-tracker-service`:** A Node.js backend that receives and stores tracking data.
*   **`local-tracker-app`:** An Angular frontend that provides a simple UI for visualizing the results of these tests.
*   **`local-db`:** A PostgreSQL database that stores the tracking data.

The Local Tracker is designed to be easy to use and isolated from the production environment. It has its own set of environment variables and uses its own database. This ensures that the Local Tracker does not interfere with the official competition.

## 5. Consequences

*   **Positive:**
    *   Provides a safe and easy way for users to experiment with performance tracking.
    *   Improves the developer experience by providing a way to see a historical view of improvements.
    *   Allows users to test their monitoring and observability setups in a realistic way.
*   **Negative:**
    *   Adds complexity to the project by introducing a new set of services.
    *   Requires users to understand the difference between the Local Tracker and the official competition.

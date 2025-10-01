# Prometheus

## What is Prometheus?
Prometheus is an open-source monitoring system with a dimensional data model, flexible query language (PromQL), efficient time series database, and a modern alerting approach. It collects metrics from configured targets at given intervals, evaluates rule expressions, displays the results, and can trigger alerts if some condition is observed to be true.

## How this Project Uses Prometheus
In the SRE Chaos Challenge, Prometheus serves as the core of our monitoring stack. Its primary roles are:

1.  **Metric Scraping:** Prometheus is configured to automatically discover and scrape metrics from various targets within our Docker Compose (local) or Kubernetes (cloud) environment. This includes:
    *   The `url-anvil` service (our baseline target application).
    *   Contributor applications deployed by users (e.g., `your-username-app`).
    *   Associated exporters (like `nginx-prometheus-exporter`) that expose application-specific metrics.
    *   Itself (Prometheus also exposes its own operational metrics).

2.  **Time-Series Storage:** It stores all collected metrics in its efficient time-series database, allowing for historical analysis and trending.

3.  **Remote Write to Backend:** A critical feature for this project is Prometheus's `remote_write` capability. All metrics scraped by Prometheus are forwarded in real-time to our `backend` service. This allows the backend to:
    *   Process metrics for real-time scoring of challenges.
    *   Maintain the leaderboard based on verifiable data.

4.  **Data Source for Grafana:** Prometheus acts as the primary data source for Grafana, enabling the creation of rich, interactive dashboards to visualize application performance and system health.

## How You Can Use Prometheus Integration (Within Your Contributor App)

As a contributor, understanding Prometheus is key to optimizing your application's performance and ensuring it's correctly monitored. Your focus will be on how your application integrates with Prometheus:

*   **Exposing Metrics:** Ensure your application (or its sidecar/exporter) exposes metrics in a Prometheus-compatible format (typically on a `/metrics` endpoint). Our `contributor-app` template includes an Nginx setup that exposes `/stub_status` metrics, which are then translated by `nginx-prometheus-exporter`.
*   **Custom Metrics:** If your application is more complex, consider instrumenting it to expose custom metrics relevant to its performance and reliability. This could give you an edge in certain challenges.
*   **Monitoring Your App:** Use Grafana to query Prometheus and build custom dashboards to visualize *your application's* metrics. This is invaluable for understanding how your app performs under different conditions.
*   **Challenge Scoring:** Remember that the backend uses the metrics forwarded by Prometheus to calculate your challenge score. Focus on exposing relevant, accurate metrics from *your application* that reflect its performance against the challenge objectives.

**Note:** Direct contributions to the core Prometheus configuration or the platform's metric processing logic are generally not accepted for Hacktoberfest. If you have suggestions for platform-level improvements, please open an issue.

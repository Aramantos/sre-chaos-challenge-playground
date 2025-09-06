# SRE Challenge: Containerized Web App with Monitoring

This document is divided into three sections:
1.  **Instructions:** A detailed guide to build and run this project, perfect for a Hacktoberfest submission.
2.  **My Learning Journey:** A narrative of my development process, including the concepts I learned and the challenges I overcame.
3.  **Gemini's Context:** A technical summary of the project for AI assistant context.

---

## 1. Instructions for Hacktoberfest Contributors

Welcome! This section provides a detailed, beginner-friendly guide to get the project running on your local machine.

### What is This Project?

This project is a complete, containerized web application stack. It includes a simple Nginx web server, a tool to simulate traffic, and a full monitoring suite using Prometheus and Grafana. It's a great way to get hands-on experience with fundamental Site Reliability Engineering (SRE) and DevOps concepts.

### Prerequisites

Before you begin, you will need to have Docker and Docker Compose installed on your system. These tools are essential for working with containers.

*   **Docker**: This is the underlying technology that allows us to run applications in isolated environments called containers. You can find the official installation guide here: [Get Docker](https://docs.docker.com/get-docker/)
*   **Docker Compose**: This is a tool for defining and running multi-container Docker applications. It makes it easy to manage all the different services in our project (like the web server, database, etc.) with a single command. Docker Compose is included with most Docker Desktop installations.

### Getting Started

**Step 1: Get the Code**

First, you need to get a copy of the project's code. The best way to do this is by cloning the repository using Git.

```bash
# Replace the URL with the actual repository URL
git clone https://github.com/your-username/your-repository.git

# Navigate into the newly created project directory
cd your-repository
```

**Step 2: Build and Run the Application**

Now for the magic. The `docker-compose.yml` file in the project root contains all the instructions for building and running our services.

Run the following command in your terminal from the project's root directory:

```bash
docker-compose up --build
```

*   **What does this command do?**
    *   `--build`: This flag tells Docker Compose to build the Docker images from scratch using the `Dockerfile` in the project. This is important to do the first time you run the project, or anytime you make changes to the `Dockerfile` or the application code.
    *   `up`: This command starts all the services defined in the `docker-compose.yml` file in the correct order.

> **Pro Tip**: If you want to run the services in the background (so you can continue using your terminal), you can add the `-d` (detached) flag: `docker-compose up --build -d`

**Step 3: Access the Services**

Once the command finishes, all the services will be running. You can access them in your web browser at the following URLs:

*   **Nginx Web Server**: `http://localhost:8080` - This is your main web application.
*   **Prometheus**: `http://localhost:9090` - This is the monitoring system that collects and stores metrics.
*   **Grafana**: `http://localhost:3000` - This is the dashboard where you will visualize the metrics. (Default login: `admin` / `admin`)

### Setting up the Grafana Dashboard

To see your metrics, you need to configure Grafana to use Prometheus as its data source and then import a pre-built dashboard.

1.  **Log in to Grafana** at `http://localhost:3000` with the username `admin` and password `admin`.
2.  **Add the Prometheus Data Source**:
    *   On the left menu, click the gear icon (⚙️) for **Configuration**, then **Data Sources**.
    *   Click **Add data source** and select **Prometheus**.
    *   In the **URL** field, enter `http://prometheus:9090`. 
    *   *Why this URL?* All the services in our `docker-compose.yml` are on the same internal Docker network. This means they can communicate with each other using their service names as hostnames. So, from inside the Grafana container, the Prometheus container is reachable at the hostname `prometheus`.
    *   Click **Save & test**. You should see a green success message.
3.  **Import a Dashboard**:
    *   On the left menu, click the four-squares icon (⊞) for **Dashboards**, then **Manage**.
    *   Click **Import** on the top right.
    *   In the **Import via grafana.com** field, enter the ID `9614`. This is a popular dashboard for the Nginx Prometheus Exporter.
    *   Click **Load**.
    *   On the next screen, at the bottom, select the **Prometheus** data source you just created.
    *   Click **Import**.

That's it! You should now have a fully operational dashboard showing the metrics from your Nginx web server.

---

## 2. My Learning Journey

This section is a log of my development process and the challenges I encountered while building this project.

### The Initial Idea

My goal was to do more than just build a simple web server. I wanted to understand how to run it in a professional way, which meant I needed to be able to see what it was doing. This led me down the path of learning about containerization and observability.

### Phase 1: Getting the Web Server Running

First, I chose Nginx as my web server because it's lightweight and widely used. I wrote a simple `Dockerfile` to containerize it. To make sure I had something to monitor, I also wrote a basic Python script, `load_test.py`, to act as a load tester and simulate user traffic. To make it easy to run both the web server and the load tester together, I created a `docker-compose.yml` file. This allowed me to define both services and run them with a single command.

### Phase 2: The "Aha!" Moment with Observability

With the server running, I wanted to get insight into its performance. This is where I learned about the concept of **observability**. It's not just about having dashboards with predefined metrics; it's about having the data to ask any question about your system's state. 

I chose Prometheus and Grafana, as they are the industry standard for this. The tricky part was that Nginx doesn't produce metrics in a format Prometheus can understand out of the box. This led me to discover the need for an **exporter**. I added the `nginx-prometheus-exporter` to my `docker-compose.yml`. This service acts as a translator, scraping Nginx's basic status page and converting the data into time-series metrics that Prometheus can collect.

### Phase 3: The Troubleshooting Chronicles

I ran into a couple of interesting problems along the way that taught me a lot.

#### Grafana Connection Issues
*   **Problem:** When I tried to add Prometheus as a data source in Grafana, I kept getting errors like "failed to update datasource" or "UNIQUE constraint failed".
*   **Discovery:** After some digging, I realized there were two issues. First, my `prometheus.yml` file had some indentation errors that stopped the Prometheus container from starting correctly. Second, my first attempt to add the data source with the wrong URL (`localhost:9090`) had created a broken, "ghost" data source with the same name.
*   **Solution:** I fixed the indentation in `prometheus.yml` and restarted the services. Then, instead of creating a new data source in Grafana, I found the old broken one and just updated its URL to the correct `http://prometheus:9090`. This taught me a valuable lesson about how services communicate inside a Docker network.

#### Nginx 404 "Not Found" Error
*   **Problem:** When I tried to access my web server at `http://localhost:8080`, I was getting a 404 Not Found error. The logs showed that Nginx couldn't find the `index.html` file at `/etc/nginx/html/index.html`.
*   **Discovery:** I realized that my `Dockerfile` was copying the `index.html` file to `/usr/share/nginx/html`, but my `nginx.conf` did not specify a `root` directory. This meant Nginx was looking in its default location, which was the wrong place.
*   **Solution:** I fixed this by adding the `root /usr/share/nginx/html;` and `index index.html;` directives to my `nginx.conf` file. After a quick rebuild of the containers, my custom page showed up correctly. This was a good lesson in how important explicit configuration is.

---

## 3. Gemini's Context

This section provides a technical summary of the project for AI assistant context.

*   **Project Goal**: To create a simple, observable, containerized web application stack. This serves as a practical, hands-on example of SRE principles for beginners.
*   **Component Breakdown & Purpose**:
    *   **`web` service**: The system under test. Its purpose is to serve a simple HTML webpage. It is configured via `nginx.conf` to also expose a `/stub_status` page for metrics.
    *   **`load-generator` service**: The workload generator. Its purpose is to create synthetic traffic against the `web` service so that there are interesting metrics to observe in Grafana.
    *   **`nginx-exporter` service**: The metrics translator. Its purpose is to bridge the gap between Nginx's simple status format and the time-series format that Prometheus requires.
    *   **`prometheus` service**: The metrics backend. Its purpose is to scrape, store, and make queryable the time-series metrics from the `nginx-exporter`.
    *   **`grafana` service**: The visualization layer. Its purpose is to provide a user-friendly interface for creating dashboards and exploring the metrics stored in Prometheus.
*   **Key Configurations**:
    *   **`docker-compose.yml`**: The heart of the orchestration. It defines all the services, their builds, ports, volumes, and startup dependencies (`depends_on`).
    *   **`prometheus.yml`**: The brain of Prometheus. It tells Prometheus which targets to scrape for metrics (in this case, the `nginx-exporter` and Prometheus itself).

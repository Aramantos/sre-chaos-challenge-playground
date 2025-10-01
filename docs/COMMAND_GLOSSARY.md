## Command Glossary

**Table of Contents**

*   [`docker compose up --build -d`](#docker-compose-up---build--d)
*   [`docker compose run --rm <service> <command>`](#docker-compose-run---rm-service-command)
*   [`docker compose logs <service>`](#docker-compose-logs-service)
*   [`docker compose down`](#docker-compose-down)
*   [`docker compose down -v`](#docker-compose-down--v)
*   [`docker ps`](#docker-ps)
*   [`docker exec <container_name_or_id> <command>`](#docker-exec-container_name_or_id-command)
*   [`psql -U <user> -d <database> -c "<SQL_query>"`](#psql--u-user--d-database--c-sql_query)
*   [`python create_contributor_app.py`](#python-create-contributor_apppy)
*   [`findstr <pattern>` (Windows) / `grep <pattern>` (Linux/macOS)](#findstr-pattern-windows--grep-pattern-linuxmacos)
*   [Common Scenarios](#common-scenarios)

For those new to Docker Compose and general debugging, here is a brief explanation of the commands used in this project.

> **Note**: This project uses the modern `docker compose` syntax (without the hyphen). Older Docker installations may require `docker-compose` instead.

### `docker compose up --build -d`

This is the main command to start the entire application stack.

*   **`docker compose up`**: The core command that reads your `docker-compose.yml` file(s) and starts all the services. It also creates a shared network so they can communicate with each other.
*   **`--build`**: A flag that tells Docker Compose to build the images from the local `Dockerfile`s before starting. This is essential on the first run or anytime you make changes to a `Dockerfile` or the application code.
*   **`-d`**: A flag for "detached" mode, which runs the containers in the background and frees up your terminal.

### `docker compose run --rm <service> <command>`

This command is for running a specific, one-off task within a service container.

*   **`docker compose run`**: Unlike `up`, `run` is for executing a single task (like a script) in a service's container.
*   **`--rm`**: A cleanup flag that automatically removes the container after the task is finished. This is perfect for preventing a build-up of old containers.
*   **`<service>`**: The name of the service from `docker-compose.yml` you want to run the task in (e.g., `load-generator`).
*   **`<command>`**: The actual command to execute inside the container (e.g., `python load_test.py http://url-anvil 100`).

### `docker compose logs <service>`

This is your most important debugging tool for viewing container output.

*   **`docker compose logs`**: Fetches and displays the log output from your services.
*   **`<service>`**: The name of the service whose logs you want to see (e.g., `docker compose logs backend`). If a container is failing, its logs are the first place to look for errors.

### `docker compose down`

This command is used to stop and remove the entire application stack.

*   **`docker compose down`**: This will stop all the running containers and remove them, along with the network that was created. It's the command you use when you are finished and want to clean everything up.

### `docker compose down -v`

This command is similar to `docker compose down` but also removes all named volumes associated with the services.

*   **`docker compose down -v`**: The `-v` (or `--volumes`) flag tells Docker Compose to remove any named volumes declared in the `volumes` section of your `docker-compose.yml` file. This is useful for ensuring a completely clean slate, especially when troubleshooting persistence issues or when you want to remove all data associated with your services (e.g., database data, Grafana configuration).

### `docker ps`

Lists running Docker containers.

*   **`docker ps`**: Shows information about all currently running containers, including their ID, name, image, and exposed ports. Useful for identifying container names for `docker exec`.
*   **`docker ps --format "{{.ID}}\t{{.Names}}"`**: A formatted output to easily get container ID and name.

### `docker exec <container_name_or_id> <command>`

Executes a command inside a running Docker container.

*   **`docker exec`**: Allows you to run commands inside a container without entering it.
*   **`<container_name_or_id>`**: The name or ID of the running container (e.g., `sre_chaos_challenge-db-1`).
*   **`<command>`**: The command to execute inside the container (e.g., `ls -l /app`).

### `psql -U <user> -d <database> -c "<SQL_query>"`

Executes a PostgreSQL query. This command is typically used in conjunction with `docker exec` to interact with the database inside its container.

*   **`psql`**: The command-line interface for PostgreSQL.
*   **`-U <user>`**: Specifies the PostgreSQL user (e.g., `user`).
*   **`-d <database>`**: Specifies the database to connect to (e.g., `sre_challenge_db`).
*   **`-c "<SQL_query>"`**: Executes the specified SQL query.
*   **Example**: To view API keys:
    ```bash
    docker exec sre_chaos_challenge-db-1 psql -U user -d sre_challenge_db -c "SELECT * FROM api_keys;"
    ```

### `python create_contributor_app.py`

Runs the contributor onboarding script.

*   **`python create_contributor_app.py`**: Executes the Python script that guides new contributors through setting up their application, generating Docker Compose files, and registering with Prometheus.

### `findstr <pattern>` (Windows) / `grep <pattern>` (Linux/macOS)

Filters text in command output.

*   **`findstr <pattern>`**: (Windows) Searches for text patterns in files or command output.
*   **`grep <pattern>`**: (Linux/macOS) Searches for text patterns in files or command output.
*   **Usage**: Often used with `docker compose logs <service> | findstr "pattern"` to filter logs for specific keywords.

### Common Scenarios

Here are some common scenarios and the commands you might use:

*   **Restart a failing service**:
    ```bash
    docker compose up --build -d <service_name>
    ```
    (e.g., `docker compose up --build -d backend`)
*   **Reset everything (clear all data and rebuild)**:
    ```bash
    docker compose down -v && docker compose up --build -d
    ```
*   **Inspect the database quickly**:
    ```bash
    docker exec -it sre_chaos_challenge-db-1 psql -U user -d sre_challenge_db -c "SELECT * FROM competition_entries;"
    ```
# PostgreSQL

## What is PostgreSQL?
PostgreSQL is a powerful, open-source object-relational database system with over 30 years of active development that has earned it a strong reputation for reliability, feature robustness, and performance. It supports both SQL (relational) and JSON (non-relational) querying.

## How this Project Uses PostgreSQL
In the SRE Chaos Challenge, PostgreSQL (running as the `db` service) serves as the primary persistent data store for the `backend` service. Its key functions are:

1.  **API Key Management:** It stores the unique API keys generated for each contributor, along with their associated `user_id` and currently active `challenge_type`. This allows the backend to authenticate incoming metrics and associate them with the correct contributor and challenge.
2.  **Competition Entry Storage:** It stores the calculated scores and other relevant details for each contributor's performance in various challenges. This data is used to populate the leaderboard.
3.  **Reliable Data Storage:** As a robust relational database, PostgreSQL ensures the integrity and persistence of critical challenge data, even across service restarts.

## How You Can Use PostgreSQL Integration (Understanding Data Storage)

While direct interaction with the PostgreSQL database is primarily handled by the `backend` service, understanding its role is important for contributors:

*   **Data Persistence:** Your challenge scores and API keys are stored here. This means your progress is saved across sessions.
*   **`pgadmin` Access:** You can use the `pgadmin` service (accessible via `http://localhost:5050`) to inspect the database directly. This can be useful for debugging or understanding how scores and user data are stored.
    *   **Login:** `admin@example.com` / `your_pgadmin_password_here` (from your `.env` file).
    *   **Server Connection:** Connect to host `db` on port `5432` with user `user` and password `your_postgres_password_here`.

**Note:** Direct contributions to the core database schema or backend database interaction logic are generally not accepted for Hacktoberfest. If you have suggestions for platform-level improvements, please open an issue.

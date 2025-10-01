import os
import subprocess
import json
import uuid
import psycopg2
import sys

NAMESPACE = "sre-chaos"
PROJECT_ID = "artful-winter-473414-q1" # Replace with your actual GCP Project ID

def get_db_connection():
    try:
        # Assuming the backend service is running in Kubernetes and accessible
        # from where this script is executed (e.g., via port-forward or external IP)
        # For local execution, you might need to port-forward the backend-db service
        conn = psycopg2.connect(
            dbname=os.getenv("POSTGRES_DB", "sre_challenge_db"),
            user=os.getenv("POSTGRES_USER", "user"),
            password=os.getenv("POSTGRES_PASSWORD", "password"),
            host=os.getenv("POSTGRES_HOST", "localhost"), # This will need to be updated for GKE
            port=os.getenv("POSTGRES_PORT", "5432")
        )
        return conn
    except psycopg2.OperationalError as e:
        print(f"Error: Could not connect to the PostgreSQL database. Please ensure the database is running and accessible.")
        print(f"Details: {e}")
        sys.exit(1)

def create_contributor_app_k8s(username):
    if not username:
        print("GitHub username cannot be empty. Exiting.")
        return

    # --- Generate API Key and insert into DB ---
    api_key = str(uuid.uuid4())
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        # Set a default challenge type on creation
        challenge_type = 'robust-service'
        cur.execute(
            "INSERT INTO api_keys (key, user_id, challenge_type) VALUES (%s, %s, %s) ON CONFLICT (user_id) DO UPDATE SET key = EXCLUDED.key, challenge_type = EXCLUDED.challenge_type",
            (api_key, username, challenge_type)
        )
        conn.commit()
        cur.close()
        print(f"Successfully created/updated API key for '{username}' with default challenge type '{challenge_type}'.")
    except psycopg2.Error as e:
        print(f"Error: Could not insert/update API key into the database for '{username}'.")
        print(f"Details: {e}")
        if conn:
            conn.rollback()
        return # Stop execution if DB operation fails
    finally:
        if conn:
            conn.close()

    # --- Generate Kubernetes Deployment YAML ---
    deployment_yaml = f"""
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {username}-app-deployment
  namespace: {NAMESPACE}
  labels:
    app: {username}-app
spec:
  replicas: 1
  selector:
    matchLabels:
      app: {username}-app
  template:
    metadata:
      labels:
        app: {username}-app
    spec:
      containers:
      - name: {username}-app
        image: gcr.io/{PROJECT_ID}/sre-chaos-challenge-{username}-app:latest
        ports:
        - containerPort: 80
---
apiVersion: v1
kind: Service
metadata:
  name: {username}-app-service
  namespace: {NAMESPACE}
spec:
  selector:
    app: {username}-app
  ports:
    - protocol: TCP
      port: 80
      targetPort: 80
  type: ClusterIP
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {username}-app-exporter-deployment
  namespace: {NAMESPACE}
  labels:
    app: {username}-app-exporter
spec:
  replicas: 1
  selector:
    matchLabels:
      app: {username}-app-exporter
  template:
    metadata:
      labels:
        app: {username}-app-exporter
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "9113"
    spec:
      initContainers:
      - name: wait-for-{username}-app
        image: busybox
        command: ['sh', '-c', 'until wget -q -O - http://{username}-app-service:80/stub_status; do echo waiting for {username}-app; sleep 2; done']
      containers:
      - name: {username}-app-exporter
        image: nginx/nginx-prometheus-exporter:0.10.0
        args: ["-nginx.scrape-uri", "http://{username}-app-service:80/stub_status"]
        ports:
        - containerPort: 9113
"""

    # Write temporary YAML file
    manifest_file = f"k8s/contributors/{username}-app.yaml"
    with open(manifest_file, "w") as f:
        f.write(deployment_yaml)

    # Apply deployment and service
    try:
        subprocess.run(["kubectl", "apply", "-f", manifest_file, "-n", NAMESPACE], check=True)
        print(f"Contributor '{username}' app and exporter deployed to Kubernetes.")
    except subprocess.CalledProcessError as e:
        print(f"Error applying Kubernetes manifests: {e}")
        return

    print("\n" + "="*60)
    print("Contributor Onboarding Complete".center(60))
    print("="*60)
    print(f"Your unique API key is: {api_key}")
    print("Save this key securely. You will need it to submit your challenge results.")
    print("-" * 60)
    print(f"Your app '{username}-app' is deployed in the '{NAMESPACE}' namespace.")
    print("Prometheus will automatically discover and scrape its metrics.")
    print("="*60 + "\n")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python create_contributor_app_k8s.py <username>")
        sys.exit(1)
    username = sys.argv[1]
    create_contributor_app_k8s(username)

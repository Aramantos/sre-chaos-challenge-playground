import os
import shutil
import uuid
import psycopg2
import sys
import json
import requests
from dotenv import load_dotenv

load_dotenv() # Load environment variables from .env

def get_db_connection():
    """Establishes a connection to the PostgreSQL database using environment variables."""
    db_password = os.getenv("POSTGRES_PASSWORD")
    if not db_password:
        print("Error: POSTGRES_PASSWORD environment variable is not set.")
        sys.exit(1)

    try:
        conn = psycopg2.connect(
            dbname=os.getenv("POSTGRES_DB", "sre_challenge_db"),
            user=os.getenv("POSTGRES_USER", "user"),
            password=db_password,
            host=os.getenv("POSTGRES_HOST", "localhost"), # Assuming script is run from host
            port=os.getenv("POSTGRES_PORT", "5432")
        )
        return conn
    except psycopg2.OperationalError as e:
        print(f"Error: Could not connect to the PostgreSQL database. Please ensure the database is running and accessible.")
        print(f"Details: {e}")
        sys.exit(1)

def create_contributor_app():
    github_username = input("Enter the new contributor's GitHub username: ")

    if not github_username:
        print("GitHub username cannot be empty. Exiting.")
        return

    # --- Create user directory first ---
    source_dir = os.path.join("contributors", "contributor-app")
    destination_dir = os.path.join("contributors", github_username)

    if not os.path.exists(source_dir):
        print(f"Error: Source directory '{source_dir}' not found. Make sure 'contributor-app' exists inside 'contributors'.")
        return

    if os.path.exists(destination_dir):
        print(f"Error: Contributor app directory for '{github_username}' already exists at '{destination_dir}'. Exiting.")
        return

    # --- Generate API Key and insert into DB ---
    api_key = str(uuid.uuid4())
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO api_keys (key, user_id, challenge_type) VALUES (%s, %s, %s)",
            (api_key, github_username, 'robust-service') # Default to robust-service
        )
        conn.commit()
        cur.close()
        print(f"Successfully created API key for '{github_username}'.")
    except psycopg2.Error as e:
        print(f"Error: Could not insert new API key into the database for '{github_username}'.")
        print(f"Details: {e}")
        if conn:
            conn.rollback()
        return # Stop execution if DB operation fails
    finally:
        if conn:
            conn.close()

    # --- Copy files after successful DB operation ---
    try:
        shutil.copytree(source_dir, destination_dir)
        print(f"Successfully created contributor app for '{github_username}' at '{destination_dir}'.")

        # --- Create private folder and save API key/run command ---
        private_dir = os.path.join(destination_dir, 'private')
        os.makedirs(private_dir, exist_ok=True)

        with open(os.path.join(private_dir, 'api_key.txt'), 'w') as f:
            f.write(api_key)
        print(f"Saved API key to '{private_dir}/api_key.txt'.")

        run_command = f"docker-compose -f docker-compose.yml -f compose-files/docker-compose.{github_username}.yml up --build -d"
        with open(os.path.join(private_dir, 'run_command.txt'), 'w') as f:
            f.write(run_command)
        print(f"Saved run command to '{private_dir}/run_command.txt'.")

        # --- Register as active influencer for default challenge ---
        backend_url = os.getenv("BACKEND_URL")
        if not backend_url:
            print("Error: BACKEND_URL environment variable is not set.")
            sys.exit(1)

        register_influencer_url = f"{backend_url}/api/v1/register-influencer"
        default_challenge = 'robust-service' # Default challenge for new users

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "challenge_type": default_challenge
        }

        try:
            response = requests.post(register_influencer_url, headers=headers, json=payload)
            response.raise_for_status() # Raise an exception for HTTP errors
            print(f"Successfully registered '{github_username}' as active influencer for '{default_challenge}'.")
        except requests.exceptions.RequestException as e:
            print(f"Error calling backend API to register influencer: {e}")
            print(f"CRITICAL: Contributor '{github_username}' created, but failed to register as active influencer.")
            sys.exit(1)

        # ... existing final print block ...




        # --- Configure Dockerfile and nginx.conf with correct user path ---
        dockerfile_path = os.path.join(destination_dir, 'Dockerfile')
        with open(dockerfile_path, 'r') as f:
            dockerfile_content = f.read()
        dockerfile_content = dockerfile_content.replace(
            "/usr/share/nginx/html/contributor-app",
            f"/usr/share/nginx/html/{github_username}"
        )
        with open(dockerfile_path, 'w') as f:
            f.write(dockerfile_content)
        print("Configured 'Dockerfile' with the correct user path.")

        nginx_conf_path = os.path.join(destination_dir, 'nginx.conf')
        with open(nginx_conf_path, 'r') as f:
            nginx_conf_content = f.read()
        nginx_conf_content = nginx_conf_content.replace(
            "root /usr/share/nginx/html/contributor-app;",
            f"root /usr/share/nginx/html/{github_username};"
        )
        with open(nginx_conf_path, 'w') as f:
            f.write(nginx_conf_content)
        print("Configured 'nginx.conf' with the correct user path.")

        # --- Create a dedicated Docker Compose file for the new user ---
        compose_file_path = os.path.join('compose-files', f'docker-compose.{github_username}.yml')
        compose_content = f"""
services:
  {github_username}-app:
    build:
      context: ./contributors/{github_username}
    image: sre-chaos-challenge-{github_username}-app:latest
    networks:
      - default

  {github_username}-app-exporter:
    image: nginx/nginx-prometheus-exporter:0.10.0
    command: -nginx.scrape-uri http://{github_username}-app/stub_status
    networks:
      - default
    depends_on:
      - {github_username}-app
"""
        with open(compose_file_path, 'w') as f:
            f.write(compose_content)
        print(f"Created dedicated Docker Compose file at '{compose_file_path}'.")

        # --- Update Prometheus targets file ---
        targets_file = 'prometheus/targets.json'
        new_target = {
            "targets": [f"{github_username}-app-exporter:9113"],
            "labels": {
                "job": "contributor-apps",
                "instance": f"{github_username}"
            }
        }
        
        targets_data = []
        if os.path.exists(targets_file):
            with open(targets_file, 'r') as f:
                try:
                    targets_data = json.load(f)
                except json.JSONDecodeError:
                    print(f"Warning: Could not decode {targets_file}. Starting with an empty list.")
                    targets_data = []

        # Filter out any existing entries for this user to prevent duplicates
        targets_data = [target for target in targets_data if target.get('labels', {}).get('instance') != github_username]

        targets_data.append(new_target)
        
        with open(targets_file, 'w') as f:
            json.dump(targets_data, f, indent=2)
        print(f"Updated Prometheus targets file at '{targets_file}'.")

        print("\n" + "="*60)
        print("Contributor Setup Complete".center(60))
        print("="*60)
        print(f"Your unique API key is: {api_key}")
        print("Save this key securely. You will need it to submit your challenge results.")
        print("-"*60)
        print("To start your new application and see it in Grafana, run:")
        print(f"  docker-compose -f docker-compose.yml -f compose-files/docker-compose.{github_username}.yml up --build -d")
        print("-"*60)
        print(f"Your API key and run command have also been saved to: contributors/{github_username}/private/")
        print("Please check that directory for your details.")
        print("="*60 + "\n")
    except Exception as e:
        print(f"An error occurred while creating the contributor app directory: {e}")
        # If file copy fails, we should ideally roll back the DB change, but for this script, we'll just notify the user.
        print(f"CRITICAL: An API key was created for '{github_username}' but the application directory could not be created.")

if __name__ == "__main__":
    create_contributor_app()

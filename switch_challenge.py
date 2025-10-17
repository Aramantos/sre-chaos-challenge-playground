import os
import sys
import argparse
import requests
from dotenv import load_dotenv

load_dotenv() # Load environment variables from .env

def switch_challenge():
    """Updates the challenge type for a given user by calling the backend API."""
    parser = argparse.ArgumentParser(description="Switch the active challenge for a contributor.")
    parser.add_argument("--user", required=True, help="The GitHub username of the contributor.")
    parser.add_argument("--challenge", required=True, help="The new challenge to switch to (e.g., 'robust-service', 'graceful-degradation', 'longest-upkeep').")
    args = parser.parse_args()

    github_username = args.user
    new_challenge_type = args.challenge

    valid_challenges = ['robust-service', 'graceful-degradation', 'longest-upkeep'];
    if new_challenge_type not in valid_challenges:
        print(f"Error: Invalid challenge type '{new_challenge_type}'.")
        print(f"Please choose from: {valid_challenges}")
        sys.exit(1)

    # Read API key from the contributor's private folder
    api_key_path = os.path.join('contributors', github_username, 'private', 'api_key.txt')
    if not os.path.exists(api_key_path):
        print(f"Error: API key file not found for user '{github_username}' at '{api_key_path}'.")
        sys.exit(1)

    with open(api_key_path, 'r') as f:
        api_key = f.read().strip()

    # Call the new backend API endpoint
    backend_url = os.getenv("BACKEND_URL")
    if not backend_url:
        print("Error: BACKEND_URL environment variable is not set.")
        sys.exit(1)

    register_influencer_url = f"{backend_url}/api/v1/register-influencer"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "challenge_type": new_challenge_type
    }

    try:
        response = requests.post(register_influencer_url, headers=headers, json=payload)
        response.raise_for_status() # Raise an exception for HTTP errors
        print(f"Successfully switched '{github_username}' to the '{new_challenge_type}' challenge.")
    except requests.exceptions.RequestException as e:
        print(f"Error calling backend API to register influencer: {e}")
        sys.exit(1)

if __name__ == "__main__":
    switch_challenge()
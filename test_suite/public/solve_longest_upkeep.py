#!/usr/bin/env python

import time

def solve_longest_upkeep_challenge():
    """Explains the goal of the longest-upkeep challenge and how to succeed."""
    print("--- Longest-Upkeep Challenge Information ---")
    print("The goal of this challenge is to keep the url-anvil service running for as long as possible without any restarts.")
    print("Your score is based on the 'process_start_time_seconds' and 'up' metrics, which are collected automatically by Prometheus.")
    print("A restart of the url-anvil service will reset your uptime score.")
    print("\nTo succeed in this challenge, you need to ensure a stable environment for the url-anvil service.")
    print("This script will now run indefinitely to signify that the challenge is ongoing. There is no need to actively send requests.")
    print("You can stop this script at any time.")

    while True:
        time.sleep(3600) # Sleep for an hour

if __name__ == "__main__":
    solve_longest_upkeep_challenge()


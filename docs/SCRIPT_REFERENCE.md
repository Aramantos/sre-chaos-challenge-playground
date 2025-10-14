# Script Reference

This document provides a reference for the scripts in the `scripts` directory.

## `dev-setup.sh`

This script is used to set up the local development environment. It builds the necessary Docker images, starts all services, and runs a smoke test to verify that the environment is healthy and ready for development.

## `enforce_local_tracker_bounds.sh`

This script is used to enforce the boundaries of the local tracker. It ensures that the local tracker is not able to communicate with the official competition backend.

## `rebuild_all.sh`

This script is used to rebuild all the Docker images. This is useful when you have made changes to the source code and want to ensure that the changes are reflected in the running containers.

## `run_load_test.sh`

This script is used to run a load test against a specified target. It takes two arguments: the target URL and the number of requests to send.

## `verify_local_tracker_dirs.sh`

This script is used to verify that all the directory and file names are consistent. It is run as a pre-commit hook to prevent errors and maintain a clean codebase.

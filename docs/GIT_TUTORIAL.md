# Git Tutorial: Navigating the SRE Chaos Challenge Project

This guide will help you understand the basics of Git, the forking workflow essential for contributing to open-source projects like this one, and how to navigate the SRE Chaos Challenge repository.

## 1. How Git Works (The Basics)

Git is a distributed version control system. It tracks changes in source code during software development. It's designed for coordinating work among programmers, but it can be used to track changes in any set of files.

*   **Repository:** A Git repository (`.git` folder) contains all the history of your project, including all commits, branches, and tags.
*   **Commit:** A snapshot of your project at a specific point in time. Each commit has a unique ID (SHA-1 hash), a message, an author, and a timestamp.
*   **Branch:** A lightweight, movable pointer to a commit. Branches allow you to work on different features or fixes in isolation without affecting the main codebase.
*   **Merge:** The process of combining changes from one branch into another.
*   **Remote:** A version of your repository that is hosted on the internet or network (e.g., GitHub, GitLab). `origin` is the conventional name for the remote repository from which you cloned.

## 2. The Forking Workflow (for Open Source Contributions)

The forking workflow is a common way to contribute to open-source projects where you don't have direct write access to the main repository.

1.  **Fork the Starter Kit Repository:** Instead of forking the main project, you will fork a simplified "starter kit" repository. This provides a clean and minimal starting point for your contributions.
    *   Go to `https://github.com/original-owner/sre-chaos-challenge-starter-kit` (or the actual starter kit URL).
    *   Click the "Fork" button to create your own copy on your GitHub account. This is your personal sandbox.
2.  **Clone Your Fork:** Download your forked starter kit repository to your local machine.
    ```bash
    git clone https://github.com/your-username/sre-chaos-challenge-starter-kit.git
    cd sre-chaos-challenge-starter-kit
    ```
3.  **Add Upstream Remote:** Configure a remote that points to the original *main project* repository (the "upstream"). This allows you to fetch updates from the original project.
    ```bash
    git remote add upstream https://github.com/original-owner/sre-chaos-challenge.git
    ```
4.  **Create a New Branch:** Always work on a new branch for each feature or bug fix. This keeps your changes isolated.
    ```bash
    git checkout -b feature/my-awesome-feature
    ```
5.  **Make Your Changes:** Implement your feature or fix, commit your changes locally.
    ```bash
    git add .
    git commit -m "feat: Add my awesome feature"
    ```
6.  **Push to Your Fork:** Push your new branch to your *forked* repository on GitHub.
    ```bash
    git push origin feature/my-awesome-feature
    ```
7.  **Open a Pull Request (PR):** Go to your forked repository on GitHub and open a new Pull Request. The PR should be from your `feature/my-awesome-feature` branch *to the `main` branch of the original repository*.

## 3. Project Navigation: SRE Chaos Challenge Structure

The project is organized into several key directories:

*   **`backend/`**: Contains the Node.js/Express backend application.
*   **`frontend/`**: Contains the Angular leaderboard application.
*   **`url-anvil/`**: The target application for challenges.
*   **`load-generator/`**: Python scripts for generating load and stress.
*   **`prometheus/`**: Prometheus configuration and targets.
*   **`grafana/`**: Grafana setup.
*   **`docs/`**: Project documentation (like this guide!).
*   **`contributors/`**: Where contributor applications are created by the onboarding script.
*   **`compose-files/`**: Contains Docker Compose files for individual contributor apps.

## 4. Branching & Pull Request Best Practices

*   **Branch Naming:** Use descriptive names (e.g., `feat/new-feature`, `fix/bug-description`, `docs/update-guide`).
*   **Commit Messages:** Follow Conventional Commits (e.g., `feat:`, `fix:`, `docs:`, `chore:`).
*   **Pull Request Scope:** Keep PRs focused on a single feature or fix to make reviews easier.
*   **Stay Updated:** Regularly fetch and rebase from `upstream/main` to keep your branch up-to-date.
    ```bash
    git fetch upstream
    git rebase upstream/main
    ```

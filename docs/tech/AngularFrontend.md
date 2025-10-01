# Angular Frontend

## What is the Angular Frontend?
Angular is a popular open-source framework for building client-side web applications. The Angular Frontend in this project is a single-page application (SPA) responsible for displaying the SRE Chaos Challenge leaderboard and providing a user interface for interacting with the challenge results.

## How this Project Uses the Angular Frontend
The `frontend` service (running as an Nginx static file server) provides the user interface for the SRE Chaos Challenge. Its primary functions are:

1.  **Leaderboard Display:** It fetches real-time scoring data from the Node.js Backend API and presents it in a dynamic, sortable, and visually appealing leaderboard format.
2.  **Challenge Selection:** Users can switch between different challenge leaderboards (e.g., `robust-service`, `crash-challenge`) using interactive buttons, allowing them to view rankings specific to each challenge.
3.  **User Experience:** It provides a responsive and intuitive interface for contributors to track their progress and see how they rank against others.
4.  **Dark Mode:** The frontend is styled with a permanent dark mode theme for improved aesthetics and reduced eye strain.

## How You Can Use the Angular Frontend (Viewing Your Results)

As a contributor, the Angular Frontend is your primary interface for observing your performance in the SRE Chaos Challenge:

*   **Track Your Scores:** View your current rank and score on the various challenge leaderboards. This provides immediate feedback on your application's performance.
*   **Challenge Switching:** Use the challenge selector buttons to see how you rank in different challenges.
*   **UI/UX Suggestions:** If you have ideas for improving the visual design, layout, or responsiveness of the leaderboard, please open an issue to suggest them. The proposed styling changes in `docs/private/future_styling/` are a great starting point for discussion.

**Note:** Direct contributions to the core Angular frontend code are generally not accepted for Hacktoberfest. Your focus should be on optimizing your own deployed application.

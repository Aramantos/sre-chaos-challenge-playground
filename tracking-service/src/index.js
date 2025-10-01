require('dotenv').config();
const express = require('express');
const { Pool } = require('pg');

const app = express();
const port = 3002; // Unique port for tracking service

app.use(express.json()); // For parsing application/json

// PostgreSQL Connection Pool
const pool = new Pool({
    user: process.env.POSTGRES_USER,
    host: 'db', // Connects to the 'db' service in docker-compose
    database: process.env.POSTGRES_DB,
    password: process.env.POSTGRES_PASSWORD,
    port: 5432,
});

// Test DB connection
pool.on('connect', () => {
    console.log('Tracking service connected to PostgreSQL database');
});

pool.on('error', (err) => {
    console.error('Unexpected error on idle client', err);
    process.exit(-1);
});

// Endpoint to receive tracking data from load-generator
app.post('/api/track', async (req, res) => {
    const { userId, challengeType, metricName, value, timestamp, labels, runDetails } = req.body;

    try {
        // Insert into a new tracking table (e.g., 'load_test_runs')
        await pool.query(
            `INSERT INTO load_test_runs (user_id, challenge_type, metric_name, value, timestamp, labels, run_details)
             VALUES ($1, $2, $3, $4, $5, $6, $7)`,
            [userId, challengeType, metricName, value, timestamp, labels, runDetails]
        );
        res.status(200).send('Tracking data received and stored');
    } catch (error) {
        console.error('Error storing tracking data:', error);
        res.status(500).send('Error storing tracking data');
    }
});

// Healthcheck endpoint
app.get('/health', (req, res) => {
    res.sendStatus(200);
});

app.listen(port, () => {
    console.log(`Tracking service listening at http://localhost:${port}`);
});
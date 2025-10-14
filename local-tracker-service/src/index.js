require('dotenv').config();

if (process.env.ENABLE_LOCAL_TRACKER !== 'true') {
    console.error('❌ Local Tracker disabled by environment. Set ENABLE_LOCAL_TRACKER=true to enable.');
    process.exit(1);
}

console.log('✅ Local Tracker enabled.');

const express = require('express');
const { Pool } = require('pg');

const app = express();
const port = 3002; // Unique port for tracking service

app.use(express.json()); // For parsing application/json

// PostgreSQL Connection Pool
const pool = new Pool({
  user: process.env.POSTGRES_USER,
  host: process.env.POSTGRES_HOST || 'local-db',
  database: process.env.POSTGRES_DB,
  password: process.env.POSTGRES_PASSWORD,
  port: 5432,
});

// Test DB connection
pool.on('connect', () => {
    console.log('Local Tracker Service connected to PostgreSQL database');
});

pool.on('error', (err) => {
    console.error('Unexpected error on idle client', err);
    process.exit(-1);
});

// Middleware for API Key Validation
const LOCAL_TRACKER_API_KEY = process.env.LOCAL_TRACKER_API_KEY || process.env.API_KEY; // The expected API key

const validateApiKey = (req, res, next) => {
    if (!LOCAL_TRACKER_API_KEY) {
        console.warn("LOCAL_TRACKER_API_KEY or API_KEY is not set in environment variables. Skipping API key validation.");
        return next(); // Allow all requests if no API key is configured
    }

    const token = req.headers['x-api-key'];

    if (!token) {
        return res.status(401).json({ error: 'API key is missing.' });
    }

    if (token === LOCAL_TRACKER_API_KEY) {
        next(); // API key is valid
    } else {
        res.status(403).json({ error: 'Invalid API key.' });
    }
};

// Endpoint to receive tracking data from load-generator
app.post('/api/track', validateApiKey, async (req, res) => {
    const { schema_version, userId, challengeType, metricName, value, timestamp, labels, runDetails } = req.body;
    const { session_id, commit_hash, target_url } = runDetails;

    // Basic Validation
    if (!userId || !challengeType || !metricName || !runDetails) {
        return res.status(400).json({ status: "error", message: "Missing required fields: userId, challengeType, metricName, runDetails." });
    }
    if (typeof userId !== 'string' || typeof challengeType !== 'string' || typeof metricName !== 'string') {
        return res.status(400).json({ status: "error", message: "userId, challengeType, metricName must be strings." });
    }
    if (typeof runDetails !== 'object' || runDetails === null) {
        return res.status(400).json({ status: "error", message: "runDetails must be an object." });
    }
    // Optional: Add more specific validation for runDetails content if needed

    try {
        await pool.query(
            `INSERT INTO load_test_runs (schema_version, user_id, challenge_type, metric_name, value, timestamp, labels, run_details, session_id, commit_hash, target_app)
             VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)`,
            [schema_version, userId, challengeType, metricName, value, timestamp, labels, runDetails, session_id, commit_hash, target_url]
        );
        res.status(200).json({ status: "ok", message: "Tracking data received and stored." });
    } catch (error) {
        console.error('Error storing tracking data:', error);
        res.status(500).json({ status: "error", message: "Error storing tracking data." });
    }
});

// Endpoint to retrieve tracking data for a specific user
app.get('/api/track/:userId', async (req, res) => {
    const { userId } = req.params;

    try {
        const { rows } = await pool.query(
            'SELECT * FROM load_test_runs WHERE user_id = $1 ORDER BY timestamp DESC',
            [userId]
        );

        const groupedData = rows.reduce((acc, row) => {
            const { target_app, session_id } = row;
            if (!acc[target_app]) {
                acc[target_app] = {};
            }
            if (!acc[target_app][session_id]) {
                acc[target_app][session_id] = [];
            }
            acc[target_app][session_id].push(row);
            return acc;
        }, {});

        res.status(200).json(groupedData);
    } catch (error) {
        console.error('Error retrieving tracking data:', error);
        res.status(500).json({ status: "error", message: "Error retrieving tracking data." });
    }
});

const crypto = require('crypto');

let isRecording = false;
let recordingInterval = null;
let sessionId = null;

function runLoadTest() {
    console.log('Running scheduled load test...');
    const commitHash = git.short();
    exec(`docker-compose exec load-generator python3 load_test.py http://url-anvil:8080 10 --session-id ${sessionId} --commit-hash ${commitHash}`, (error, stdout, stderr) => {
        if (error) {
            console.error(`Error running load test: ${error.message}`);
            return;
        }
        if (stderr) {
            console.error(`Load test stderr: ${stderr}`);
            return;
        }
        console.log(`Load test stdout: ${stdout}`);
    });
}

app.post('/api/record', (req, res) => {
    isRecording = !isRecording;
    if (isRecording) {
        console.log('Starting recording session...');
        sessionId = crypto.randomBytes(16).toString('hex');
        runLoadTest(); // Run once immediately
        recordingInterval = setInterval(runLoadTest, 300000); // 5 minutes
    } else {
        console.log('Stopping recording session...');
        clearInterval(recordingInterval);
        sessionId = null;
    }
    res.status(200).json({ status: "ok", isRecording, sessionId });
});

app.post('/api/migrate', async (req, res) => {
    try {
        console.log('Attempting to create load_test_runs table...');
        await pool.query(`
            CREATE TABLE IF NOT EXISTS load_test_runs (
                id SERIAL PRIMARY KEY,
                schema_version VARCHAR(255),
                user_id VARCHAR(255),
                challenge_type VARCHAR(255),
                metric_name VARCHAR(255),
                value NUMERIC,
                timestamp TIMESTAMPTZ,
                labels JSONB,
                run_details JSONB,
                target_app VARCHAR(255)
            );
        `);
        console.log('load_test_runs table creation/check complete.');

        console.log('Attempting to add session_id column...');
        await pool.query('ALTER TABLE load_test_runs ADD COLUMN IF NOT EXISTS session_id VARCHAR(255);');
        console.log('session_id column addition/check complete.');

        console.log('Attempting to add commit_hash column...');
        await pool.query('ALTER TABLE load_test_runs ADD COLUMN IF NOT EXISTS commit_hash VARCHAR(255);');
        console.log('commit_hash column addition/check complete.');

        console.log('Attempting to add target_app column...');
        await pool.query('ALTER TABLE load_test_runs ADD COLUMN IF NOT EXISTS target_app VARCHAR(255);');
        console.log('target_app column addition/check complete.');

        res.status(200).json({ status: "ok", message: "Migration completed successfully." });
    } catch (error) {
        console.error('Error running migration:', error);
        res.status(500).json({ status: "error", message: "Error running migration." });
    }
});

// Healthcheck endpoint
app.get('/health', (req, res) => {
    res.status(200).json({ status: "ok", message: "Local Tracker Service is healthy." });
});

app.listen(port, () => {
    console.log(`Local Tracker Service listening at http://localhost:${port}`);
    console.warn('⚠️  WARNING: This is a local-only service for personal tracking and is NOT for official competition scoring. ⚠️');
});

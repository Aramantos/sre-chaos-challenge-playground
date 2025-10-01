
require('dotenv').config();
const express = require('express');
const path = require('path');
const { Pool } = require('pg'); // Import the PostgreSQL client
const snappy = require('snappy'); // Import snappy
const protobuf = require('protobufjs'); // Import protobufjs

const app = express();
const port = 3001;

// Custom middleware to handle different body parsers based on route
app.use((req, res, next) => {
    if (req.path === '/api/v1/metrics/write') {
        // For Prometheus remote_write, we need the raw body as a Buffer
        let data = [];
        req.on('data', chunk => {
            data.push(chunk);
        });
        req.on('end', () => {
            req.body = Buffer.concat(data);
            next();
        });
        req.on('error', (err) => {
            console.error('Error reading raw body:', err);
            res.status(500).send('Error reading raw body');
        });
    } else {
        express.json()(req, res, next);
    }
});

// Load protobufs
let WriteRequest;
protobuf.load(path.resolve(__dirname, './proto/remote.proto'), (err, root) => {
    if (err) throw err;
    WriteRequest = root.lookupType('prometheus.WriteRequest');
});

// PostgreSQL Connection Pool
const pool = new Pool({
    user: process.env.POSTGRES_USER,
    host: 'db', // This remains 'db' as it refers to the docker service name
    database: process.env.POSTGRES_DB,
    password: process.env.POSTGRES_PASSWORD,
    port: 5432,
});

// Helper function to extract user_id and challenge_type from labels and database
const getUserIdAndChallengeType = async (labels) => {
    const results = [];

    if (labels.job === 'url-anvil') {
        // For url-anvil metrics, find ALL active influencers for ALL challenges
        try {
            const res = await pool.query('SELECT user_id, challenge_type FROM active_influencers');
            if (res.rows.length > 0) {
                res.rows.forEach(row => {
                    results.push({ userId: row.user_id, challengeType: row.challenge_type });
                });
            } else {
                // Fallback if no active influencers are registered for url-anvil
                // Process for url-anvil-user with a default challenge type
                results.push({ userId: 'url-anvil-user', challengeType: 'robust-service' });
            }
        } catch (error) {
            console.error(`Error fetching active influencers for url-anvil:`, error);
            // Fallback: if error, still process for url-anvil-user
            results.push({ userId: 'url-anvil-user', challengeType: 'robust-service' });
        }
    } else { // If not url-anvil, then default to no scoring for main leaderboard
        return [{ userId: null, challengeType: 'default-challenge' }];
    }

    // If no specific user/challenge found, return a default or empty array
    if (results.length === 0) {
        return [{ userId: null, challengeType: 'default-challenge' }]; // Should ideally not happen with fallbacks
    }
    return results;
};

const lastNginxRequests = {};
const lastNginxUpStatus = {}; // To track uptime status for crash challenge
const upkeepStatus = {}; // To track longest upkeep duration

// Function to calculate and store scores
const calculateAndStoreScore = async (userId, challengeType, metricName, value, timestamp, labels) => {
    console.log(`Attempting to calculate score for User: ${userId}, Challenge: ${challengeType}, Metric: ${metricName}, Value: ${value}`);

    let currentScore = 0;
    try {
        const result = await pool.query(
            'SELECT score FROM competition_entries WHERE user_id = $1 AND challenge_type = $2',
            [userId, challengeType]
        );
        if (result.rows.length > 0) {
            currentScore = result.rows[0].score;
        }
    } catch (error) {
        console.error(`Error fetching current score for ${userId} (${challengeType}):`, error);
    }

    let pointsToAdd = 0;
    const details = { metric: metricName, value: value, labels: labels };
    const startTime = timestamp; // For simplicity, using current metric timestamp
    const endTime = timestamp; // For simplicity, using current metric timestamp

    switch (challengeType) {
        case 'robust-service':
            // Score for Robust Service: requests handled by url-anvil
            if (metricName === 'http_request_duration_ms_count') {
                const previousRequests = lastNginxRequests[userId] || 0;
                const requestIncrease = value - previousRequests;
                if (requestIncrease > 0) {
                    pointsToAdd += requestIncrease * 0.1; // 0.1 points per request
                }
                lastNginxRequests[userId] = value; // Update last known value
            }
            // Add more robust-service specific scoring logic here (e.g., penalize errors from url-anvil)
            break;
        case 'crash-challenge':
            // --- Original Crash Challenge Logic (commented out for Hacktoberfest) ---
            /*
            if (metricName === 'process_cpu_seconds_total') {
                const previousCpuTotal = lastNginxUpStatus[userId] ? lastNginxUpStatus[userId].status : 0; // Using status to store last known CPU total
                const currentCpuTotal = value;

                if (previousCpuTotal === 0 && currentCpuTotal > 0) {
                    // url-anvil started or recovered
                    console.log(`url-anvil started/recovered for ${userId} at ${timestamp.toISOString()}`);
                    pointsToAdd += 5; // Small bonus for url-anvil starting up
                    lastNginxUpStatus[userId] = { status: currentCpuTotal, timestamp: timestamp };
                } else if (previousCpuTotal > 0 && currentCpuTotal <= previousCpuTotal) {
                    // url-anvil crashed or stopped (CPU total not increasing or reset)
                    console.log(`url-anvil crashed/stopped for ${userId} at ${timestamp.toISOString()}`);
                    pointsToAdd -= 50; // Penalty for url-anvil crashing
                    lastNginxUpStatus[userId] = { status: 0, timestamp: timestamp }; // Mark as down
                } else if (currentCpuTotal > previousCpuTotal) {
                    // url-anvil is still up and processing (CPU total increasing)
                    pointsToAdd += 1; // Small continuous uptime bonus for url-anvil
                    lastNginxUpStatus[userId] = { status: currentCpuTotal, timestamp: timestamp };
                }
            }
            */
            // --- Temporary Crash Challenge Logic for Hacktoberfest ---
            // Score for Crash Challenge: based on requests handled by url-anvil
            if (metricName === 'http_request_duration_ms_count') {
                const previousRequests = lastNginxRequests[userId] || 0;
                const requestIncrease = value - previousRequests;
                if (requestIncrease > 0) {
                    pointsToAdd += requestIncrease * 0.1; // 0.1 points per request
                }
                lastNginxRequests[userId] = value; // Update last known value
            }
            break;
        case 'longest-upkeep':
            // Score for Longest Upkeep Challenge: longest continuous uptime of url-anvil
            if (metricName === 'process_start_time_seconds') {
                if (!upkeepStatus[userId]) {
                    upkeepStatus[userId] = { current_up_start_time: null, max_up_duration: 0 };
                }

                // If the start time changes, it means url-anvil restarted
                const currentStartTime = value; // value is process_start_time_seconds
                const previousStartTime = upkeepStatus[userId].current_up_start_time;

                if (previousStartTime === null || currentStartTime > previousStartTime) {
                    // url-anvil started or restarted, reset uptime tracking
                    upkeepStatus[userId].current_up_start_time = currentStartTime;
                }

                // Calculate current uptime duration (from currentStartTime to now)
                const now = timestamp.getTime() / 1000; // Convert to seconds
                const currentUpDuration = now - upkeepStatus[userId].current_up_start_time;

                if (currentUpDuration > upkeepStatus[userId].max_up_duration) {
                    upkeepStatus[userId].max_up_duration = currentUpDuration;
                }
                pointsToAdd = upkeepStatus[userId].max_up_duration; // Score is the longest upkeep duration
            }
            break;
        default:
            pointsToAdd = Math.random() * 100; // Default random score for other challenges
            break;
    }

    const newScore = currentScore + pointsToAdd;

    try {
        await pool.query(
            `INSERT INTO competition_entries (user_id, challenge_type, score, start_time, end_time, details) \
             VALUES ($1, $2, $3, $4, $5, $6) \
             ON CONFLICT (user_id, challenge_type) DO UPDATE SET \
             score = $3, \
             start_time = EXCLUDED.start_time, \
             end_time = EXCLUDED.end_time, \
             details = EXCLUDED.details, \
             timestamp = NOW()`,
            [userId, challengeType, newScore, startTime, endTime, details]
        );
        console.log(`Score for ${userId} (${challengeType}) updated: ${newScore}`);
    } catch (error) {
        console.error(`Error storing score for ${userId} (${challengeType}):`, error);
    }
};

// Function to initialize the database schema
const initializeDatabase = async () => {
    try {
        // await pool.query(`DROP TABLE IF EXISTS competition_entries, metrics, api_keys CASCADE;`); // Commented out for data persistence

        await pool.query(`
            CREATE TABLE IF NOT EXISTS api_keys (
                id SERIAL PRIMARY KEY,
                key VARCHAR(255) UNIQUE NOT NULL,
                user_id VARCHAR(255) UNIQUE NOT NULL,
                challenge_type VARCHAR(255) DEFAULT 'default-challenge'
            );
        `);

        // Drop table if it exists to ensure schema changes are applied during development
        // await pool.query(`DROP TABLE IF EXISTS competition_entries;`);
        await pool.query(`
            CREATE TABLE IF NOT EXISTS competition_entries (
                id SERIAL PRIMARY KEY,
                user_id VARCHAR(255) NOT NULL,
                challenge_type VARCHAR(255) NOT NULL,
                score DOUBLE PRECISION NOT NULL,
                start_time TIMESTAMPTZ NOT NULL,
                end_time TIMESTAMPTZ NOT NULL,
                details JSONB,
                timestamp TIMESTAMPTZ DEFAULT NOW(),
                FOREIGN KEY (user_id) REFERENCES api_keys(user_id),
                UNIQUE (user_id, challenge_type)
            );
        `);

        await pool.query(`
            CREATE TABLE IF NOT EXISTS active_influencers (
                challenge_type VARCHAR(255) PRIMARY KEY,
                user_id VARCHAR(255) NOT NULL,
                timestamp TIMESTAMPTZ DEFAULT NOW(),
                FOREIGN KEY (user_id) REFERENCES api_keys(user_id)
            );
        `);

        // Insert example API keys if they don't exist
        /*
        await pool.query(`
            INSERT INTO api_keys (key, user_id, challenge_type) VALUES ('key1', 'contributor_a', 'default-challenge') ON CONFLICT (user_id) DO NOTHING;
            INSERT INTO api_keys (key, user_id, challenge_type) VALUES ('key2', 'contributor_b', 'default-challenge') ON CONFLICT (user_id) DO NOTHING;
            INSERT INTO api_keys (key, user_id, challenge_type) VALUES ('key3', 'contributor_c', 'default-challenge') ON CONFLICT (user_id) DO NOTHING;
            INSERT INTO api_keys (key, user_id, challenge_type) VALUES ('url-anvil-key', 'url-anvil-user', 'robust-service') ON CONFLICT (user_id) DO NOTHING;
            INSERT INTO api_keys (key, user_id, challenge_type) VALUES ('newuser-key', 'newuser', 'robust-service') ON CONFLICT (user_id) DO NOTHING;
        `);
        */
        console.log('Database schema initialized. Default API key insertion commented out.');
    } catch (err) {
        console.error('Error initializing database:', err);
        process.exit(1); // Exit if database cannot be initialized
    }
};

// Middleware for API Key Authentication
const apiKeyAuth = async (req, res, next) => {
    const authHeader = req.headers['authorization'];
    const apiKey = authHeader && authHeader.split(' ')[1]; // Expecting "Bearer <key>"

    if (apiKey == null) {
        return res.sendStatus(401); // Unauthorized
    }

    try {
        const result = await pool.query('SELECT user_id FROM api_keys WHERE key = $1', [apiKey]);
        if (result.rows.length > 0) {
            req.user_id = result.rows[0].user_id; // Attach user_id to the request
            next();
        } else {
            return res.sendStatus(403); // Forbidden
        }
    } catch (err) {
        console.error('Error during API key authentication:', err);
        return res.sendStatus(500); // Internal Server Error
    }
};

// Prometheus remote_write endpoint
app.post('/api/v1/metrics/write', async (req, res) => {
    try {
        // Decompress the snappy-compressed request body
        const decompressed = await snappy.uncompress(req.body, { asBuffer: true });

        // Decode the protobuf message
        const decoded = WriteRequest.decode(decompressed);

        // Log the received time series for now
        console.log('Received Prometheus WriteRequest:', JSON.stringify(decoded, null, 2));

        const receivedMetrics = decoded.timeseries;

        for (const series of receivedMetrics) {
            const labels = {};
            series.labels.forEach(label => {
                labels[label.name] = label.value;
            });

            const job = labels.job;
            const instance = labels.instance; // This will be the contributor's username for contributor-apps

            // We are interested in metrics from 'contributor-apps' and 'url-anvil'
            if (job === 'contributor-apps' || job === 'url-anvil') {
                for (const sample of series.samples) {
                    const metricName = labels.__name__; // Prometheus metric name
                    const value = isNaN(sample.value) ? null : sample.value; // Handle NaN values
                    let timestamp;
                    if (sample.timestamp && !isNaN(Number(sample.timestamp))) {
                        timestamp = new Date(Number(sample.timestamp));
                    } else {
                        console.warn(`Invalid or missing timestamp for metric ${metricName}. Using current time.`);
                        timestamp = new Date(); // Use current time if timestamp is invalid
                    }

                    // Only process relevant metrics for scoring
                    const relevantMetrics = {
                        'robust-service': 'http_request_duration_ms_count',
                        'crash-challenge': 'http_request_duration_ms_count',
                        'longest-upkeep': 'process_start_time_seconds'
                    };

                    const userChallengePairs = await getUserIdAndChallengeType(labels);

                    // Process metrics for url-anvil challenges for the main leaderboard
                    if (labels.job === 'url-anvil') {
                        for (const { userId, challengeType } of userChallengePairs) {
                            if (userId && challengeType) {
                                if (relevantMetrics[challengeType] === metricName) {
                                    await calculateAndStoreScore(userId, challengeType, metricName, value, timestamp, labels);
                                }
                            }
                        }
                    } else if (labels.job === 'contributor-apps') {
                        // For contributor-apps metrics, process for personal dashboard (future)
                        // For now, just log that they are being received.
                        console.log(`Received contributor-app metric for personal dashboard: User: ${userChallengePairs[0].userId}, Metric: ${metricName}, Value: ${value}`);
                    }
                }
            }
        }

        res.sendStatus(200);
    } catch (error) {
        console.error('Error processing remote_write request:', error);
        res.status(500).send('Error processing remote_write request');
    }
});

app.post('/api/v1/leaderboard/:challenge', async (req, res) => {
    const challengeType = req.params.challenge;

    // Basic validation for challenge type
    const validChallenges = ['crash-challenge', 'robust-service', 'longest-upkeep'];
    if (!validChallenges.includes(challengeType)) {
        return res.status(400).send('Invalid challenge type.');
    }

    try {
        const dbResult = await pool.query(`
            SELECT
                user_id,
                score,
                start_time,
                end_time,
                details
            FROM competition_entries
            WHERE challenge_type = $1
            ORDER BY score DESC
            LIMIT 20;
        `, [challengeType]);

        const leaderboard = dbResult.rows.map((entry, index) => ({
            rank: index + 1,
            user: entry.user_id,
            score: entry.score,
            ...entry.details // Optionally merge the details object
        }));

        res.json(leaderboard);
    } catch (err) {
        console.error(`Error fetching leaderboard data for ${challengeType}:`, err);
        res.status(500).send('Error fetching leaderboard data');
    }
});

// New API endpoint to register an active influencer for a challenge
app.post('/api/v1/register-influencer', apiKeyAuth, async (req, res) => {
    const { challenge_type } = req.body;
    const user_id = req.user_id; // From apiKeyAuth middleware

    const validChallenges = ['crash-challenge', 'robust-service', 'longest-upkeep'];
    if (!validChallenges.includes(challenge_type)) {
        return res.status(400).send('Invalid challenge type.');
    }

    try {
        await pool.query(
            `INSERT INTO active_influencers (challenge_type, user_id) \
             VALUES ($1, $2) \
             ON CONFLICT (challenge_type) DO UPDATE SET \
             user_id = EXCLUDED.user_id, \
             timestamp = NOW()`,
            [challenge_type, user_id]
        );
        console.log(`Contributor ${user_id} registered as active influencer for ${challenge_type}.`);
        res.status(200).send(`Successfully registered ${user_id} as active influencer for ${challenge_type}.`);
    } catch (error) {
        console.error(`Error registering active influencer for ${user_id} (${challenge_type}):`, error);
        res.status(500).send('Error registering active influencer.');
    }
});

app.get('/api/v1/leaderboard/:challenge', async (req, res) => {
    const challengeType = req.params.challenge;

    // Basic validation for challenge type
    const validChallenges = ['crash-challenge', 'robust-service', 'longest-upkeep'];
    if (!validChallenges.includes(challengeType)) {
        return res.status(400).send('Invalid challenge type.');
    }

    try {
        const dbResult = await pool.query(`
            SELECT
                user_id,
                score,
                start_time,
                end_time,
                details
            FROM competition_entries
            WHERE challenge_type = $1
            ORDER BY score DESC
            LIMIT 20;
        `, [challengeType]);

        const leaderboard = dbResult.rows.map((entry, index) => ({
            rank: index + 1,
            user: entry.user_id,
            score: entry.score,
            ...entry.details // Optionally merge the details object
        }));

        res.json(leaderboard);
    } catch (err) {
        console.error(`Error fetching leaderboard data for ${challengeType}:`, err);
        res.status(500).send('Error fetching leaderboard data');
    }
});

// Healthcheck endpoint
app.get('/health', (req, res) => {
    res.sendStatus(200);
});

initializeDatabase().then(() => {
    app.listen(port, () => {
        console.log(`Backend server listening at http://localhost:${port}`);
    });
});

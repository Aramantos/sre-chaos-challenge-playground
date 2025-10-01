const express = require('express');
const axios = require('axios');
const path = require('path');
const client = require('prom-client');
const crypto = require('crypto');

const app = express();
const port = 8080;

// --- Prometheus Metrics Setup ---
const register = new client.Registry();
client.collectDefaultMetrics({ register });

const httpRequestDurationMicroseconds = new client.Histogram({
    name: 'http_request_duration_ms',
    help: 'Duration of HTTP requests in ms',
    labelNames: ['method', 'route', 'code'],
    buckets: [50, 100, 200, 300, 400, 500, 750, 1000, 2000]
});
register.registerMetric(httpRequestDurationMicroseconds);

// Middleware to measure request duration
app.use((req, res, next) => {
    const end = httpRequestDurationMicroseconds.startTimer();
    res.on('finish', () => {
        end({ route: req.path, code: res.statusCode, method: req.method });
    });
    next();
});

// Middleware
app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

// In-memory store for the last 10 tests
const history = [];

const MASTER_URL_LIST = [
    'https://www.archives.gov/founding-docs/constitution-transcript',
    'https://www.archives.gov/founding-docs/declaration-transcript',
    'https://en.wikipedia.org/wiki/United_States',
    'https://en.wikipedia.org/wiki/World_War_II',
    'https://en.wikipedia.org/wiki/Black_hole',
    'https://en.wikipedia.org/wiki/Philosophy',
    'https://policies.google.com/privacy',
    'https://docs.github.com/en/site-policy/github-terms/github-terms-of-service',
    'https://www.apache.org/licenses/LICENSE-2.0'
];

// --- API Endpoints ---

app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

app.get('/api/history', (req, res) => {
    res.json(history);
});

app.get('/api/sample-urls', (req, res) => {
    // Shuffle the array and take the first 5
    const shuffled = MASTER_URL_LIST.sort(() => 0.5 - Math.random());
    res.json(shuffled.slice(0, 5));
});

app.post('/api/test', async (req, res) => {
    const { urls } = req.body;

    if (!urls || !Array.isArray(urls) || urls.length === 0) {
        return res.status(400).json({ error: 'Invalid or empty URL array provided.' });
    }

    try {
        const testStartTime = process.hrtime.bigint(); // High-resolution time start

        const fetchPromises = urls.map(url => axios.get(url, { timeout: 15000 }));
        const responses = await Promise.all(fetchPromises);

        const testEndTime = process.hrtime.bigint(); // High-resolution time end
        const totalFetchTimeNs = testEndTime - testStartTime;
        const totalFetchTimeMs = Number(totalFetchTimeNs) / 1_000_000; // Convert nanoseconds to milliseconds
        const averageFetchTimeMs = totalFetchTimeMs / urls.length;

        const combinedContent = responses.map(response => response.data).join('\n---\n');
        
        const hash = crypto.createHash('sha256').update(combinedContent).digest('hex');

        const result = {
            urls_tested: urls.length,
            total_fetch_time_ms: parseFloat(totalFetchTimeMs.toFixed(2)), // Format to 2 decimal places
            average_fetch_time_ms: parseFloat(averageFetchTimeMs.toFixed(2)), // Format to 2 decimal places
            content_hash: hash,
            timestamp: new Date().toISOString(),
        };

        history.unshift(result);
        if (history.length > 10) {
            history.pop();
        }

        res.json(result);

    } catch (error) {
        console.error(`Error testing URLs:`, error.message);
        // Add more detailed logging for axios errors
        if (error.response) {
            console.error('Axios Error - Response Data:', error.response.data);
            console.error('Axios Error - Response Status:', error.response.status);
            console.error('Axios Error - Response Headers:', error.response.headers);
        } else if (error.request) {
            console.error('Axios Error - No Response Received:', error.request);
        } else {
            console.error('Axios Error - Request Setup:', error.config);
        }
        res.status(500).json({ error: `Failed to test URLs.`, message: error.message });
    }
});

// Metrics endpoint for Prometheus
app.get('/metrics', async (req, res) => {
    res.set('Content-Type', register.contentType);
    res.end(await register.metrics());
});

app.listen(port, () => {
    console.log(`URL Anvil listening on port ${port}`);
});

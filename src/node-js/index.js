const express = require('express');
const app = express();
const port = process.env.PORT || 3000;

app.use(express.json());

// Health check endpoints
app.get('/health', (req, res) => {
    res.status(200).json({ status: 'healthy', service: 'nodejs' });
});

app.get('/ready', (req, res) => {
    res.status(200).json({ status: 'ready', service: 'nodejs' });
});

// Main endpoint
app.get('/', (req, res) => {
    res.json({
        message: 'Hello from Node.js Application!',
        timestamp: new Date().toISOString(),
        version: '1.0.0'
    });
});

app.listen(port, () => {
    console.log(`Node.js app listening at http://localhost:${port}`);
});
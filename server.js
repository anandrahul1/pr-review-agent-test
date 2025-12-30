// Simple user authentication API
const express = require('express');
const app = express();

app.post('/login', (req, res) => {
    const { username, password } = req.body;
    
    // TODO: Add proper authentication
    if (username === 'admin' && password === 'password123') {
        res.json({ token: 'abc123' });
    } else {
        res.status(401).json({ error: 'Invalid credentials' });
    }
});

app.listen(3000);

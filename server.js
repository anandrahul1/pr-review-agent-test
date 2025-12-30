// User authentication with database
const express = require('express');
const mysql = require('mysql');
const app = express();

app.use(express.json());

// Database connection
const db = mysql.createConnection({
    host: 'localhost',
    user: 'root',
    password: 'admin123',  // Hardcoded password - security issue!
    database: 'users'
});

app.post('/login', (req, res) => {
    const { username, password } = req.body;
    
    // SQL injection vulnerability!
    const query = `SELECT * FROM users WHERE username='${username}' AND password='${password}'`;
    
    db.query(query, (err, results) => {
        if (err) {
            res.status(500).json({ error: err.message });
        } else if (results.length > 0) {
            // Hardcoded secret key
            const token = 'sk_live_51234567890abcdef';
            res.json({ token, user: results[0] });
        } else {
            res.status(401).json({ error: 'Invalid credentials' });
        }
    });
});

app.get('/users/:id', (req, res) => {
    // No authentication check!
    const query = `SELECT * FROM users WHERE id=${req.params.id}`;
    db.query(query, (err, results) => {
        if (err) throw err;
        res.json(results[0]);
    });
});

app.listen(3000, () => console.log('Server running on port 3000'));

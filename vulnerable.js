const express = require('express');
const mysql = require('mysql');
const app = express();

app.use(express.json());

// Hardcoded database credentials
const db = mysql.createConnection({
    host: 'localhost',
    user: 'root',
    password: 'SuperSecret123!',
    database: 'production'
});

// SQL injection vulnerability
app.get('/user', (req, res) => {
    const userId = req.query.id;
    const query = "SELECT * FROM users WHERE id = " + userId;
    db.query(query, (err, results) => {
        if (err) throw err;
        res.json(results);
    });
});

// Hardcoded API key (fake format)
const API_KEY = "api_key_1234567890abcdefghijklmnop";

// No authentication on admin endpoint
app.delete('/admin/users/:id', (req, res) => {
    const query = `DELETE FROM users WHERE id = ${req.params.id}`;
    db.query(query);
    res.json({ success: true });
});

// Eval vulnerability
app.post('/calculate', (req, res) => {
    const expression = req.body.expression;
    const result = eval(expression);
    res.json({ result });
});

app.listen(3000);
// Updated
